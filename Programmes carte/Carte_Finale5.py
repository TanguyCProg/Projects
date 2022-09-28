from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os
import pickle
import json
from time import time
from Donnees_6 import Create_map
from Recup_donnees2 import get_data
from copy import deepcopy
from Tmrt_np import thermal_model


def lire(nom):
    """Renvoie les données enregistrées sous forme d'un fichier txt"""
    nom = nom + '.txt'
    if nom in os.listdir('.'):
        fichier = open(nom, 'rb')
        liste = pickle.load(fichier)
        fichier.close()
        return liste


def creer_legende(n, temp_min, temp_max, compteur_Pays, model, liste_Pays, date):
    """Renvoie la légende de la carte"""
    nom = "Carte {} le {}/{}/{} , {}".format(liste_Pays[compteur_Pays], date[6:], date[4:6], date[:4], model)
    legende = np.zeros((300, n, 3), dtype=np.uint8)
    largeur = np.linspace((n//10)*2, (n//10)*8, 102, dtype='int')
    for ratio in range(101):
        legende[20:121, largeur[ratio]:largeur[ratio+1]] = color(ratio/100)
    img = Image.fromarray(legende, 'RGB')
    font1 = ImageFont.truetype("arial.ttf", size=30)
    font2 = ImageFont.truetype("arial.ttf", size=45)
    draw = ImageDraw.Draw(img)
    draw.text((largeur[0], 130), str(round(temp_min, 1)), (255, 255, 255), font=font1)
    draw.text((largeur[-5], 130), str(round(temp_max, 1)), (255, 255, 255), font=font1)
    draw.text((largeur[49], 170), "(°C)", (255, 255, 255), font=font1)
    draw.text(((n//10)*2, 210), nom, (255, 255, 255), align='center', font=font2)
    return np.array(img)
    

def color(ratio):
    """Transforme un ratio entre 0 et 1 en une couleur sous la forme d'un triplet RVB"""
    if 0.75 < ratio <= 1:
        Q4 = (ratio - 3*0.25) // 0.25
        R4 = (ratio - 3*0.25) % 0.25
        Q3 = Q2 = Q1 = 1
        R3 = R2 = R1 = 0
    elif 0.5 < ratio <= 0.75:
        Q3 = (ratio - 2*0.25) // 0.25
        R3 = (ratio - 2*0.25) % 0.25
        Q4 = 0
        Q2 = Q1 = 1
        R4 = R2 = R1 = 0
    elif 0.25 < ratio <= 0.5:
        Q2 = (ratio - 0.25) // 0.25
        R2 = (ratio - 0.25) % 0.25
        Q1 = 1
        Q4 = Q3 = 0
        R1 = R3 = R4 = 0
    else:
        Q1 = ratio // 0.25
        R1 = ratio % 0.25
        Q2 = Q3 = Q4 = 0 
        R2 = R3 = R4 = 0

    RVB = [0, 0, 0]
    RVB[0] = (Q3 + R3 * 4) * 255
    RVB[1] = (Q1 + R1 * 4 - Q4 - R4 * 4) * 255
    RVB[2] = 255 - (Q2 + R2 * 4) * 255

    return RVB    


def seconds_to_minutes(secondes):
    """Fonction définie pour l'affichage, transforme les secondes en minutes"""
    minutes = secondes//60
    return "{} minutes {} secondes".format(round(minutes), round(secondes - 60 * minutes))


def encadrer(indexes, temp):
    """Ordonne les données météos, en les passant du format (p*m) à (p,m)"""
    i0 = indexes[0][0]
    compteur = 1
    for index in indexes[1:]:
        # On détermine le nombre de points où la météo est connue à i constant, on en déduit le
        # nombre de points à j constant
        if index[0] == i0:
            compteur += 1

    ind_data = deepcopy(indexes)
    for k in range(len(indexes)):
        ind_data[k].append(temp[k].tolist())
    # On place les indices dans l'ordre croissant selon i, puis croissant selon j, le troisième élément n'est pas classé
    ind_data.sort()
    ind_data = np.array(ind_data, dtype=np.object)
    data = np.array(list(ind_data[:, 2]), dtype=np.float32)
    data = np.reshape(data, (len(indexes) // compteur, compteur, 7))

    points = np.array(list(ind_data[:, :2]), dtype=np.int16)
    points = np.reshape(points, (len(indexes)//compteur, compteur, 2))
    points_pyt = points.tolist()
    # points(_pyt) est une matrice de taille (p,m) qui pointe vers les coordonnées d'une donnée météo dans la
    # matrice (n,n). La donnée météo associée est celle indexée au même endroit dans la liste data de taille
    # (p,m)
    return points, points_pyt, data


def find_long(long, lg):
    """Renvoie la position j d'une longitude dans la matrice (n,n)"""
    for j in range(1, len(lg)):
        if long <= lg[j]:
            return j-1


def find_lat(lat, lt):
    """Renvoie la position i d'une latitude dans la matrice (n,n)"""
    for i in range(1, len(lt)):
        if lat >= lt[i]:
            return i-1


def Carte(n, date, liste_Pays, liste_models, echelle, Sauvegarder):
    """
    Génère la/les carte(s) complétée(s) du/des pays considéré(s) pour différents modèles de températures ressenties

    Paramètres
    ----------
    n : int
        Dimension de la carte (pixels)
    date : str
        La date à laquelle correspondebt les données météos
    liste_Pays : list
        Liste des différents pays pour lesquels on souhaite tracer la carte
    liste_models : list
        Liste des différents modèles pour lesquels on souhaite tracer une carte
    échelle : bool
        True si l'on souhaite que les cartes de différents modèles soient à la même échelle pour un même pays
    Sauvegarder : bool
        True pour sauvegarder la carte
    """

    print("Date choisie : {}/{}/{}".format(date[6:], date[4:6], date[:4]))
    results = np.zeros((len(liste_Pays), len(liste_models), n, n), dtype=np.float32)
    l_temp_min = np.zeros((len(liste_Pays), len(liste_models)), dtype=np.float32)
    l_temp_max = np.zeros((len(liste_Pays), len(liste_models)), dtype=np.float32)
    l_presence = [0] * len(liste_Pays)

    for compteur_Pays, Pays in enumerate(liste_Pays):

        print("\n\nPays : {}".format(Pays))

        if Pays == 'France':
            fchier = lire("Délimitation_France")
            aList = json.loads(fchier)
            lp = aList['geometry']['coordinates'][0][0]
            
        elif Pays == 'Canada':
            with open('Délimitation_Canada2.json') as mon_fichier:
                data_geo = json.load(mon_fichier)
            lp = data_geo['features'][0]["geometry"]["coordinates"][10][0]

        elif Pays == "Inde":
            with open('india.txt') as mon_fichier:
                data_geo = json.load(mon_fichier)
            lp = data_geo["features"][0]["geometry"]["coordinates"][0][0]

        elif Pays == "Somalie":
            with open('Somalie.txt') as mon_fichier:
                data_geo = json.load(mon_fichier)
            lp = data_geo["geometry"]["coordinates"][0]
            
        lp_np = np.array(lp)
        long_max = max(lp_np[:, 0]) + 0.6  # +- 0.6 pour éliminer les CL
        long_min = min(lp_np[:, 0]) - 0.6
        lat_max = max(lp_np[:, 1]) + 0.6
        lat_min = min(lp_np[:, 1]) - 0.6

        print("\nCréation de la carte vierge...")
        t0 = time()
        presence, lg, lt = Create_map(n, lp)
        del lp, lp_np
        t1 = time()
        print("Done,", seconds_to_minutes(t1 - t0))
        print("\nRécupération des données météo...")
        coords, temp, azimuth = get_data(date, long_min, long_max, lat_min, lat_max)
        presence = np.array(presence, dtype=np.int8)
        t2 = time()
        print("Done,", seconds_to_minutes(t2 - t1))
        print("\nExtension des données à l'ensemble de la carte...")

        presence = np.where(presence == 2, 0, presence)

        indexes = []
        temperatures = np.zeros((n, n, 7), dtype=np.float32)
        for k in range(len(temp)):
            # Associe chaque point GPS où les données météos sont connues à un point dans la matrice (n,n)
            i, j = find_lat(coords[k][1], lt), find_long(coords[k][0], lg)
            indexes.append([i, j])
        points, points_pyt, data = encadrer(indexes, temp)

        # On étend les données à l'ensemble de la carte. Les données météos à un pixel sont égales à la
        # somme de celles connues aux quatres points les plus proches (un carré), avec un poids associé
        # qui dépend de la distance du point inconnu au point connu
        liste_deltas = []
        liste_ratio = [[], [], [], []]
        tot = (len(points)-1)*(len(points[0])-1)
        c = 0
        last_ctot = 100
        for i1 in range(len(points)-1):
            for j1 in range(len(points[0])-1):
                c += 1
                ctot = round((c/tot) * 100)
                if ctot % 3 == 0 and ctot // 3 != last_ctot:
                    print(ctot, '%', end='\r')
                    last_ctot = ctot // 3
                delta_i1 = points[i1+1, j1, 0] - points[i1, j1, 0]
                delta_j1 = points[i1, j1+1, 1] - points[i1, j1, 1]
                if not([delta_i1, delta_j1] in liste_deltas):
                    num = len(liste_deltas)
                    liste_deltas.append([delta_i1, delta_j1])
                    
                    for i2 in range(points[i1, j1, 0], points[i1+1, j1, 0]):
                        for j2 in range(points[i1, j1, 1], points[i1, j1+1, 1]):
                            ratio_i = (points[i1+1, j1, 0] - i2)/delta_i1  # 0 si situé en i+1
                            ratio_j = (points[i1, j1+1, 1] - j2)/delta_j1  # 0 si situé en j+1
                            ratio0 = (ratio_i * ratio_j) 
                            ratio1 = ((1-ratio_i) * ratio_j)
                            ratio2 = ((1-ratio_i) * (1-ratio_j))
                            ratio3 = (ratio_i * (1-ratio_j))
                            somme_ratios = ratio0 + ratio1 + ratio2 + ratio3
                            ratio0 /= somme_ratios
                            ratio1 /= somme_ratios
                            ratio2 /= somme_ratios
                            ratio3 /= somme_ratios
                            liste_ratio[num].extend(np.array([ratio0] * 7 + [ratio1] * 7 + [ratio2] * 7 + [ratio3] * 7,
                                                             dtype=np.float16)
                                                    )
                            temp0 = data[i1, j1]
                            temp1 = data[i1+1, j1]
                            temp2 = data[i1+1, j1+1]
                            temp3 = data[i1, j1+1]
                            temperatures[i2, j2] = (temp0 * ratio0 + temp1 * ratio1 + temp2 * ratio2 + temp3 * ratio3)
                    liste_ratio[num] = np.reshape(np.array(liste_ratio[num], dtype=np.float16),
                                                  (delta_i1, delta_j1, 4, 7))
                else:
                    num = liste_deltas.index([delta_i1, delta_j1])
                    temp0 = np.zeros((delta_i1, delta_j1, 7), dtype=np.float32)
                    temp1 = np.zeros((delta_i1, delta_j1, 7), dtype=np.float32)
                    temp2 = np.zeros((delta_i1, delta_j1, 7), dtype=np.float32)
                    temp3 = np.zeros((delta_i1, delta_j1, 7), dtype=np.float32)
                    temp0[:, :] = data[i1, j1]
                    temp1[:, :] = data[i1+1, j1]
                    temp2[:, :] = data[i1+1, j1+1]
                    temp3[:, :] = data[i1, j1+1]
                    temperatures[points[i1, j1, 0]: points[i1+1, j1, 0], points[i1, j1, 1]: points[i1, j1+1, 1]] = \
                        liste_ratio[num][:, :, 0] * temp0 + \
                        liste_ratio[num][:, :, 1] * temp1 + \
                        liste_ratio[num][:, :, 2] * temp2 + \
                        liste_ratio[num][:, :, 3] * temp3

        # On calcule la température ressentie pour chaque pixel à partir des données étendues à chaque pixel
        t3 = time()
        print("Done,", seconds_to_minutes(t3 - t2))
        for compteur_models, model in enumerate(liste_models):
            t3 = time()
            print("\nCalcul de la température ressentie {}...".format(model))
            Tr = thermal_model(temperatures, azimuth, model)
            t_max = np.max(Tr)
            t_min = np.min(Tr)
            temp_max = np.max(np.where(presence != 0, Tr, t_min))
            temp_min = np.min(np.where(presence != 0, Tr, t_max))
            l_temp_min[compteur_Pays][compteur_models] = temp_min
            l_temp_max[compteur_Pays][compteur_models] = temp_max
            results[compteur_Pays][compteur_models] = deepcopy(Tr)
            t4 = time()
            print("Done,", seconds_to_minutes(t4 - t3))
            
        l_presence[compteur_Pays] = presence

    # On transforme la température ressentie à chaque pixel en une couleur
    print("\nConversion(s) au format PNG...\n")
    compteur_Pays = -1
    for mod_temperatures, presence in zip(results, l_presence):
        compteur_Pays += 1
        compteur_models = -1    
        for temperatures in mod_temperatures:
            compteur_models += 1
            if echelle:
                temp_max = max(l_temp_max[compteur_Pays][:])
                temp_min = min(l_temp_min[compteur_Pays][:])
            else:
                temp_max = l_temp_max[compteur_Pays][compteur_models]
                temp_min = l_temp_min[compteur_Pays][compteur_models]
            color_map = np.zeros((len(lg)+299, len(lt)-1, 3), dtype=np.uint8)
            dtemp = (temp_max - temp_min)
            ratio = 1 - (temp_max - temperatures)/dtemp
            RVB = np.zeros((n, n, 3), dtype=np.float32)
            presence_not_0 = presence != 0
            ratio_pg_5 = ratio >= 0.5
            ratio_pp_5 = np.logical_not(ratio_pg_5)
            ratio_pg_25 = ratio >= 0.25
            ratio_pp_75 = ratio <= 0.75
            RVB[:, :, 0] = np.where(presence_not_0,
                                    np.where(ratio_pg_5 & ratio_pp_75,
                                             (((ratio - 0.5) // 0.25) + ((ratio - 0.5) % 0.25) * 4) * 255,
                                             np.heaviside(ratio - 0.6, 0.5) * 255),
                                    0)
            RVB[:, :, 1] = np.where(presence_not_0,
                                    np.where(ratio_pg_25 & ratio_pp_75,
                                             255,
                                             np.where(ratio_pp_5,
                                                      ((ratio // 0.25) + (ratio % 0.25) * 4) * 255,
                                                      (1 - ((ratio - 0.75) // 0.25) - ((ratio - 0.75) % 0.25)*4)*255)),
                                    0)
            RVB[:, :, 2] = np.where(presence_not_0,
                                    np.where(ratio_pp_5 & ratio_pg_25,
                                             255 - (((ratio - 0.25) // 0.25) + ((ratio - 0.25) % 0.25) * 4) * 255,
                                             np.heaviside(0.3 - ratio, 0.5) * 255),
                                    0)

            color_map[:n] = np.array(RVB, dtype=np.uint8)

            legende = creer_legende(n, temp_min, temp_max, compteur_Pays,
                                    liste_models[compteur_models], liste_Pays, date)
            color_map[n:] = legende

            img = Image.fromarray(color_map, 'RGB')
            img.show()

            if Sauvegarder:
                path = os.getcwd()
                path = os.path.dirname(path)
                nom = path + "\\Cartes\\{}\\Carte {} le {}_{}_{}.png"\
                    .format(liste_models[compteur_models].upper(), Pays, date[6:], date[4:6], date[:4])
                img.save(nom)
    comp = ''
    while not(comp in ['Y', 'N']):
        comp = input("Comparer les modèles ? (Y/N)\n>>> ").upper()
        if comp == 'Y':
            from Comparateur import comparer
            comparer(results, l_presence, liste_Pays, liste_models)
