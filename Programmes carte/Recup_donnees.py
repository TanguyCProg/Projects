import requests, json
import pickle, os
from math import ceil, pi, atan2,cos,sin,tan
import numpy as np
from Tmrt import utci
import time
from Azimuth_calculation import sunpos
from pythermalcomfort.models import at

def convert(value):
    value/=3.6
    value/=13
    return value


def lux_to_flux(value):
    return value/116 #lux to W/m²

def get_data(date, long_min,long_max,lat_min,lat_max, liste_models):


    def enregistrer(liste, nom):
        nomtxt = nom + '.txt'
        k = 0
        while nomtxt in os.listdir('.'):
            k+=1
            nomtxt = nom + '(' + str(k) + ')' + '.txt'
        fichier = open(nomtxt, 'wb')
        pickle.dump(liste, fichier)
        fichier.close()

    def lire(nom):
        nom = nom + '.txt'
        if nom in os.listdir('.'):
            fichier = open(nom, 'rb')
            liste = pickle.load(fichier)
            fichier.close()
            return liste

    def coords_limites():
        fichier = lire("Délimitation_France")
        aList = json.loads(fichier)
        lis = aList['geometry']['coordinates'][0][0]
        lf_np = np.array(lis)
        long_max = max(lf_np[:,0])
        long_min = min(lf_np[:,0])
        lat_max = max(lf_np[:,1])
        lat_min = min(lf_np[:,1])
        return long_min,long_max,lat_min,lat_max

    Key = "QR6LDKO9H1HW"
    lien_skecth2 ="http://api.timezonedb.com/v2.1/get-time-zone?key={}&format=json&by=position&lat={}&lng={}&time={}"
    TOKEN = 'aWuGjOHoFzbRWTvAVmAr'
    meteo = []
    azimuth = []
    coords = []
    lien_sketch = "https://power.larc.nasa.gov/api/temporal/daily/regional?latitude-min={}&latitude-max={}&longitude-min={}&longitude-max={}&parameters=SG_DAY_HOURS,CLRSKY_SFC_LW_DWN,CLRSKY_SFC_SW_DWN,ALLSKY_SFC_LW_DWN,ALLSKY_SFC_SW_DWN,CLOUD_AMT,WS2M,T2M,RH2M,T2MDEW,DIRECT_ILLUMINANCE,DIFFUSE_ILLUMINANCE&community=RE&start={}&end={}&format=JSON"
    zone_time=time.strptime("{} {} {} {}".format(date[6:],date[4:6],date[:4],12), "%d %m %Y %H")
    zone_time = time.mktime(zone_time)
    #long_min,long_max,lat_min,lat_max = coords_limites()
    lien2 = lien_skecth2.format(Key,(lat_max + lat_min)/2,(long_max + long_min)/2,zone_time)
    answer = requests.get(lien2)
    UTC = json.loads(answer.text)['gmtOffset']//3600
    Div_lat = ceil((lat_max - lat_min)/10)
    Div_long = ceil((long_max-long_min)/10)
    Sep_lat = np.linspace(lat_min,lat_max,Div_lat+1)
    Sep_long = np.linspace(long_min,long_max,Div_long+1)
    t0 = time.time()
    compteur = 0
    c= 0
    total = Div_lat * Div_long
    print("0 %", end = '\r')
    for i in range(Div_lat):
        for j in range(Div_long):
            if compteur == 20:
                if time.time() - t0 < 60:
                    time.sleep(60 - (time.time - t0))
                t0 = time.time()
                compteur = 0
            elif time.time() - t0 > 60:
                t0 = time.time()
                compteur = 0
            compteur += 1
            lien = lien_sketch.format(Sep_lat[i],Sep_lat[i+1],Sep_long[j],Sep_long[j+1],date,date)
            nb_Try = 0
            erreur = False
            while True:
                fichier = requests.get(lien)
                if str(fichier) != "<Response [200]>":
                    nb_Try += 1
                    if nb_Try >= 5:
                        erreur = True
                        print("erreur",Sep_lat[i],Sep_lat[i+1],Sep_long[j],Sep_long[j+1])
                        break
                else:
                    break

            texte = fichier.text
            data = json.loads(texte)
            filler = data["header"]["fill_value"]
            liste = data["features"]
            for point in liste:
                #CLOUD_AMT,WS2M,T2M,RH2M,T2MDEW,ALLSKY_SFC_SW_DNI,ALLSKY_SFC_SW_DIFF
                infos = point["properties"]["parameter"]
                #meteo.append([point["geometry"]["coordinates"][0],point["geometry"]["coordinates"][1],infos["CLOUD_AMT"][date],infos["WS2M"][date],infos["T2M"][date],infos["RH2M"][date],infos["T2MDEW"][date],lux_to_flux(infos["DIFFUSE_ILLUMINANCE"][date]+infos["DIRECT_ILLUMINANCE"][date])])
                meteo.append([point["geometry"]["coordinates"][0],
                              point["geometry"]["coordinates"][1],
                              infos["CLOUD_AMT"][date],
                              infos["WS2M"][date],
                              infos["T2M"][date],
                              infos["RH2M"][date],
                              infos["T2MDEW"][date],
                              infos["ALLSKY_SFC_LW_DWN"][date]+1000*infos["ALLSKY_SFC_SW_DWN"][date]/(infos["SG_DAY_HOURS"][date]+0.000001),
                              infos["CLRSKY_SFC_LW_DWN"][date]+1000*infos["CLRSKY_SFC_SW_DWN"][date]/(infos["SG_DAY_HOURS"][date]+0.000001)])
                coords.append([meteo[-1][0],meteo[-1][1]])
                when = (int(date[:4]),int(date[4:6]),int(date[6:]),12,0,0,UTC)
                location = (meteo[-1][1],meteo[-1][0])
                azimuth_temp, sun_elevation = sunpos(when,location,refraction = True)
                azimuth.append(azimuth_temp)
            c += 1
            pourcentage = round((c/ total)*100)
            print(round(pourcentage), '%', end='\r')
    #[print(meteo[i]) for i in range(len(meteo))]
    #ALL_SKY
    liste_utci1 = [utci(meteo[i][7],sun_elevation,azimuth[i],meteo[i][4],meteo[i][5],round((100-meteo[i][2])/10),meteo[i][3]+0.5) for i in range(len(meteo))]
    #CLEAR_SKY
    liste_utci2 = [utci(meteo[i][8],sun_elevation,azimuth[i],meteo[i][4],meteo[i][5],round((100-meteo[i][2])/10),meteo[i][3]+0.5) for i in range(len(meteo))]
    liste_at = [at(tdb= meteo[i][4], rh=meteo[i][5]+0.0001, v=meteo[i][3]) for i in range(len(meteo))]
    liste_tdb = [meteo[i][4] for i in range(len(meteo))]
    l_temp = []  
    #print("i : {}\nALLSKY radiation : {}\nCLRSKY radiation : {}\nSun elevation : {}\nSun azimuth : {}\nTemperature : {}\nHumidity: {}\nCloudiness : {}\nWind speed : {}".format(i,meteo[i][7],meteo[i][8],sun_elevation,azimuth[i],meteo[i][4],meteo[i][5],round((100-meteo[i][2])/10),meteo[i][3]+0.5))
    for model in liste_models:
        if model == 'utci':
            l_temp.append(liste_utci1)
        elif model == 'at':
            l_temp.append(liste_at)
        elif model == "Tdb":
            l_temp.append(liste_tdb)
    #enregistrer(liste_utci1,"ALL_SKY")
    #enregistrer(liste_utci2,"CLEAR_SKY")
    #enregistrer(coords,'coord_carte')
    #return coords,liste_at,[]
    return coords,l_temp
    #print('\n\n\n\n')
    #[print(liste_utci1[i],liste_utci2[i],meteo[i][4]) for i in range(len(liste_utci1))]
