import requests
import json
from math import ceil
import numpy as np
import time
from Azimuth_calculation import sunpos


def get_data(date, long_min, long_max, lat_min, lat_max):
    """
    Renvoie les données météos d'une zone définie par lat_min/max et long_min/max à une date donnée

    Paramètres
    ----------
    date : str
        Date à laquelle les données sont requises. Format: Année_Mois_Jour (exemple : 2021_04_30)
    long_min : float
        Longitude minimale de l'encadrement
    long_max : float
        Longitude maximale de l'encadrement
    lat_min : float
        Latitude minimale de l'encadrement
    lat_max : float
        Latitude maximale de l'encadrement
    """

    Key = "QR6LDKO9H1HW"
    lien_skecth2 = "http://api.timezonedb.com/v2.1/get-time-zone?key={}&format=json&by=position&lat={}&lng={}&time={}"
    coords = []
    lien_sketch = "https://power.larc.nasa.gov/api/temporal/daily/regional?latitude-min={}&latitude-max={}&longitude" \
                  "-min={}&longitude-max={}&parameters=SG_DAY_HOURS,CLRSKY_SFC_LW_DWN,CLRSKY_SFC_SW_DWN,ALLSKY_SFC_" \
                  "LW_DWN,ALLSKY_SFC_SW_DWN,CLOUD_AMT,WS2M,T2M,RH2M,T2MDEW,DIRECT_ILLUMINANCE,DIFFUSE_ILLUMINANCE&" \
                  "community=RE&start={}&end={}&format=JSON"
    zone_time = time.strptime("{} {} {} {}".format(date[6:], date[4:6], date[:4], 12), "%d %m %Y %H")
    zone_time = time.mktime(zone_time)
    lien2 = lien_skecth2.format(Key, (lat_max + lat_min) / 2, (long_max + long_min) / 2, zone_time)
    answer = requests.get(lien2)
    UTC = json.loads(answer.text)['gmtOffset'] // 3600
    Div_lat = ceil((lat_max - lat_min) / 10)
    Div_long = ceil((long_max - long_min) / 10)
    Sep_lat = np.linspace(lat_min, lat_max, Div_lat + 1)
    Sep_long = np.linspace(long_min, long_max, Div_long + 1)
    if len(Sep_long) >= 3:
        Sep_long[-2] = (Sep_long[-1] + Sep_long[-3]) / 2
    if len(Sep_lat) >= 3:
        Sep_lat[-2] = (Sep_lat[-1] + Sep_lat[-3]) / 2
    meteo = np.zeros((0, 7))
    total = Div_lat * Div_long
    t0 = time.time()
    compteur = 0
    c = 0
    print("0 %", end='\r')
    for i in range(Div_lat):
        for j in range(Div_long):
            if compteur == 60:
                if time.time() - t0 < 60:  # L'API interdit plus de 60 requêtes/minute
                    time.sleep(60 - (time.time() - t0))
                t0 = time.time()
                compteur = 0
            elif time.time() - t0 > 60:
                t0 = time.time()
                compteur = 0
            compteur += 1
            lien = lien_sketch.format(Sep_lat[i], Sep_lat[i + 1], Sep_long[j], Sep_long[j + 1], date, date)
            for tentative in range(5):  # On accorde jusqu'à 5 tentatives avant de déclarer une erreur
                fichier = requests.get(lien)
                if str(fichier) == "<Response [200]>":  # 200 = réponse valide
                    break
                elif tentative == 4:
                    txt_erreur = "L'API ne répond pas\n" + "Lien : " + lien
                    raise RuntimeError(txt_erreur)

            texte = fichier.text
            data = json.loads(texte)
            filler = data["header"]["fill_value"]
            liste = data["features"]
            for point in liste:
                # On obtient une liste de données pour différents points dans l'encadrement demandé
                # Des conversions d'unités sont parfois nécessaires
                infos = point["properties"]["parameter"]
                if infos["SG_DAY_HOURS"][date] == 0:  # Temps d'ensoleillement
                    AllSky = infos["ALLSKY_SFC_LW_DWN"][date]
                    ClrSky = infos["CLRSKY_SFC_LW_DWN"][date]
                else:
                    AllSky = infos["ALLSKY_SFC_LW_DWN"][date] + \
                             1000 * infos["ALLSKY_SFC_SW_DWN"][date] / infos["SG_DAY_HOURS"][date]
                    ClrSky = infos["CLRSKY_SFC_LW_DWN"][date] + \
                             1000 * infos["CLRSKY_SFC_SW_DWN"][date] / infos["SG_DAY_HOURS"][date]
                meteo = np.append(meteo, [[infos["CLOUD_AMT"][date],  # Taux de nuages
                                           infos["WS2M"][date],  # Vent
                                           infos["T2M"][date],  # Température
                                           infos["RH2M"][date],  # Humidité
                                           infos["T2MDEW"][date],  # Température du point de rosée
                                           AllSky,  # Radiation solaire avec rayonnement diffus
                                           ClrSky]],  # Radiation solaire sans rayonnement diffus
                                  axis=0)
                if filler in meteo[-1]:
                    # L'API ne couvre pas des données récentes
                    txt_erreur = "\nLa date demandée n'est pas pris en charge\nDate : {}/{}/{}" \
                        .format(date[6:], date[4:6], date[:4])
                    raise ValueError(txt_erreur)

                coords.append([point["geometry"]["coordinates"][0], point["geometry"]["coordinates"][1]])
                if c == total // 2:
                    when = (int(date[:4]), int(date[4:6]), int(date[6:]), 12, 0, 0, UTC)
                    location = (coords[-1][1], coords[-1][0])
                    azimuth, sun_elevation = sunpos(when, location, refraction=True)  # On récupère l'azimuth du soleil
            c += 1
            pourcentage = round((c / total) * 100)
            print(round(pourcentage), '%', end='\r')

    return coords, meteo, azimuth
