from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os
import pickle
import json
import os.path as path
from time import time
from Donnees_6 import Create_map
from Recup_donnees2 import get_data
from copy import deepcopy
from Tmrt_np import thermal_model

def coeff(x,y):
    return (abs(x-y)/((x+y)/2))

def lire(nom):
    nom = nom + '.txt'
    if nom in os.listdir('.'):
        fichier = open(nom, 'rb')
        liste = pickle.load(fichier)
        fichier.close()
        return liste
    
def enregistrer(liste, nom):
        nomtxt = nom + '.txt'
        k = 0
        while nomtxt in os.listdir('.'):
            k+=1
            nomtxt = nom + '(' + str(k) + ')' + '.txt'
        fichier = open(nomtxt, 'wb')
        pickle.dump(liste, fichier)
        fichier.close()

def creer_legende(n, temp_min, temp_max, compteur_Pays, model, liste_Pays, date):
    nom = "Carte {} le {}/{}/{} , {}".format(liste_Pays[compteur_Pays], date[6:], date[4:6], date[:4], model)
    legende = np.zeros((300,n,3),dtype = np.uint8)
    largeur = np.linspace((n//10)*2,(n//10)*8,102,dtype = 'int')
    for ratio in range(101):
        legende[20:121,largeur[ratio]:largeur[ratio+1]] = color(ratio/100)
    img = Image.fromarray(legende, 'RGB')
    font1 = ImageFont.truetype("arial.ttf",size=30)
    font2 = ImageFont.truetype("arial.ttf",size=45)
    draw = ImageDraw.Draw(img)
    draw.text((largeur[0], 130),str(round(temp_min,1)),(255,255,255),font=font1)
    draw.text((largeur[-5], 130),str(round(temp_max,1)),(255,255,255),font=font1)
    draw.text((largeur[49] , 170),"(°C)",(255,255,255),font=font1)
    draw.text(((n//10)*2 , 210),nom,(255,255,255),align='center',font=font2)
    return np.array(img)
    


def color(ratio):
    if 0.75 < ratio <= 1:
        Q4 = (ratio - 3*0.25)//0.25
        R4 = (ratio - 3*0.25)%0.25
        Q3 = Q2 = Q1 = 1
        R3 = R2 = R1 = 0
    elif 0.5 < ratio <= 0.75:
        Q3 = (ratio - 2*0.25)//0.25
        R3 = (ratio - 2*0.25)%0.25
        Q4 = 0
        Q2 = Q1 = 1
        R4 = R2 = R1 = 0
    elif 0.25 < ratio <= 0.5:
        Q2 = (ratio - 0.25)//0.25
        R2 = (ratio - 0.25)%0.25
        Q1 = 1
        Q4 = Q3 = 0
        R1 = R3 = R4 = 0
    else:
        Q1 = (ratio)//0.25
        R1 = (ratio)%0.25
        Q2 = Q3 = Q4 = 0 
        R2 = R3 = R4 = 0

    RVB = [0,0,0]
    RVB[0] = (Q3+R3*4)*255
    RVB[1] = (Q1+R1*4 - Q4-R4*4)*255
    RVB[2] = 255 - (Q2+R2*4)*255

    return RVB    


def seconds_to_minutes(secondes):
    minutes = secondes//60
    return "{} minutes {} secondes".format(round(minutes), round(secondes - 60*minutes))


def encadrer(indexes, temp):
    i0 = indexes[0][0]
    compteur = 1
    for index in indexes[1:]: # On détermine le nombre de points où la météo est connues à i constant, on en déduit le nombre de points à j constant
        if index[0] == i0:
            compteur += 1

    ind_data = deepcopy(indexes)
    for k in range(len(indexes)):
        ind_data[k].append(temp[k].tolist())
    ind_data.sort() # On place les indices dans l'ordre croissant selon i, puis croissant selon j, le troisième élément n'est pas classé
    ind_data = np.array(ind_data, dtype = np.object)
    data = np.array(list(ind_data[:,2]),dtype = np.float32)
    data = np.reshape(data,(len(indexes)//compteur, compteur,7))

    points = np.array(list(ind_data[:,:2]),dtype = np.int16)
    points = np.reshape(points,(len(indexes)//compteur, compteur,2))
    points_pyt = points.tolist()
    
    return points, points_pyt, data


def find_long(long, lg):
    for j in range(1, len(lg)):
        if long <= lg[j]:
            return j-1


def find_lat(lat, lt):
    for i in range(1, len(lt)):
        if lat >= lt[i]:
            return i-1


def Convertisseur(x1, y1, x2, y2):
    return (((x2 - x1)**2) + (y2 - y1)**2)**(1/2)



def Carte(n, date, liste_Pays, liste_models, echelle, Sauvegarder):
    

    results = np.zeros((len(liste_Pays),len(liste_models),n,n),dtype = np.float32)
    l_temp_min = np.zeros((len(liste_Pays),len(liste_models)),dtype = np.float32)
    l_temp_max = np.zeros((len(liste_Pays),len(liste_models)),dtype = np.float32)
    l_presence = [0]*len(liste_Pays)

    for compteur_Pays, Pays in enumerate(liste_Pays):
        os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\Programmes carte")
        if Pays == 'France':
            fchier = lire("Délimitation_France")
            aList = json.loads(fchier)
            lis = aList['geometry']['coordinates'][0][0]
            
        elif Pays == 'Canada':
            with open('Délimitation_Canada2.json') as mon_fichier:
                data_geo = json.load(mon_fichier)
            lis = data_geo['features'][0]["geometry"]["coordinates"][10][0]

        elif Pays == "Inde":
            with open('india.txt') as mon_fichier:
                data_geo = json.load(mon_fichier)
            lis = data_geo["features"][0]["geometry"]["coordinates"][0][0]

        elif Pays == "Somalie":
            with open('Somalie.txt') as mon_fichier:
                data_geo = json.load(mon_fichier)
            lis = data_geo["geometry"]["coordinates"][0]
        
            
        lf_np = np.array(lis)
        long_max = max(lf_np[:, 0]) +0.6
        long_min = min(lf_np[:, 0]) -0.6
        lat_max = max(lf_np[:, 1]) +0.6
        lat_min = min(lf_np[:, 1]) -0.6

        t0 = time()
        os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_coords")
        L = lire(Pays)
        presence, lg, lt = L[0], L[1], L[2]
        t1 = time()
        os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_meteo\{}".format(Pays))
        L = lire(date)
        coords, temp, azimuth = L[0], L[1], L[2]
        os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_meteo_generalise\{}".format(Pays))
        presence = np.array(presence,dtype = np.int8)
        t2 = time()

        presence = np.where(presence == 2, 0, presence)

        indexes = []
        temperatures = np.zeros((n,n,7),dtype=np.float32)
        for k in range(len(temp)): # Associe chaque point GPS où les données météos sont connues à un point dans la matrice (n,n)
            i, j = find_lat(coords[k][1], lt), find_long(coords[k][0], lg)
            indexes.append([i, j])
        points, points_pyt, data = encadrer(indexes, temp)
        liste_deltas = []
        liste_ratio = [[],[],[],[]]
        num = 0
        tot = (len(points)-1)*(len(points[0])-1)
        c = 0
        last_ctot = 100
        for i1 in range(len(points)-1):
            for j1 in range(len(points[0])-1):
                c+= 1
                ctot = round((c/tot)*100)
                delta_i1 = points[i1+1,j1,0] - points[i1,j1,0]
                delta_j1 = points[i1,j1+1,1] - points[i1,j1,1]
                if not([delta_i1, delta_j1] in liste_deltas):
                    num = len(liste_deltas)
                    liste_deltas.append([delta_i1, delta_j1])
                    
                    for i2 in range(points[i1,j1,0],points[i1+1,j1,0]):
                        for j2 in range(points[i1,j1,1],points[i1,j1+1,1]):
                            ratio_i = (points[i1+1,j1,0] - i2)/delta_i1 #0 si situé en i+1
                            ratio_j = (points[i1,j1+1,1] - j2)/delta_j1 #0 si situé en j+1
                            ratio0 = (ratio_i * ratio_j) 
                            ratio1 = ((1-ratio_i) * ratio_j)
                            ratio2 = ((1-ratio_i) * (1-ratio_j))
                            ratio3 = (ratio_i * (1-ratio_j))
                            somme_ratios = ratio0 + ratio1 + ratio2 + ratio3
                            ratio0 /= somme_ratios
                            ratio1 /= somme_ratios
                            ratio2 /= somme_ratios
                            ratio3 /= somme_ratios
                            liste_ratio[num].extend(np.array(([ratio0]*7) +([ratio1]*7)+ ([ratio2]*7)+ ([ratio3]*7),dtype = np.float16))
                            temp0 = data[i1, j1]
                            temp1 = data[i1+1, j1]
                            temp2 = data[i1+1, j1+1]
                            temp3 = data[i1, j1+1]
                            temperatures[i2,j2] = (temp0 * ratio0 + temp1 * ratio1 + temp2 * ratio2 + temp3 * ratio3)
                    liste_ratio[num] = np.reshape(np.array(liste_ratio[num],dtype = np.float16), (delta_i1, delta_j1,4,7))
                else:
                    num = liste_deltas.index([delta_i1, delta_j1])
                    compteur = 0
                    temp0 = np.zeros((delta_i1, delta_j1,7),dtype = np.float32)
                    temp1 = np.zeros((delta_i1, delta_j1,7),dtype = np.float32)
                    temp2 = np.zeros((delta_i1, delta_j1,7),dtype = np.float32)
                    temp3 = np.zeros((delta_i1, delta_j1,7),dtype = np.float32)
                    temp0[:,:] = data[i1, j1]
                    temp1[:,:] = data[i1+1, j1]
                    temp2[:,:] = data[i1+1, j1+1]
                    temp3[:,:] = data[i1, j1+1]
                    temperatures[points[i1,j1,0]: points[i1+1,j1,0], points[i1,j1,1]: points[i1,j1+1,1]] = liste_ratio[num][:,:,0] * temp0 + liste_ratio[num][:,:,1] * temp1+ liste_ratio[num][:,:,2] * temp2 + liste_ratio[num][:,:,3] * temp3


        t3 = time()
        enregistrer(temperatures,date)
        return
        for compteur_models, model in enumerate(liste_models):
            t3 = time()
            Tr = thermal_model(temperatures, azimuth, model)
            color_map = np.zeros((len(lg)+299, len(lt)-1, 3), dtype=np.uint8)
            t_max = np.max(Tr)
            t_min = np.min(Tr)
            temp_max = np.max(np.where(presence!=0,Tr,t_min))
            temp_min = np.min(np.where(presence!=0,Tr,t_max))
            l_temp_min[compteur_Pays][compteur_models] = temp_min
            l_temp_max[compteur_Pays][compteur_models] = temp_max
            results[compteur_Pays][compteur_models] = deepcopy(Tr)
            t4 = time()
            
        l_presence[compteur_Pays] = presence
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
            c= 0
            tot = (len(lg)-1) **2
            ratio = 1 - (temp_max   - temperatures)/dtemp
            RVB = np.zeros((n,n,3),dtype = np.float32)
            presence_not_0 = presence != 0
            ratio_pg_5 = ratio >=0.5
            ratio_pp_5 = np.logical_not(ratio_pg_5)
            ratio_pg_25 = ratio >= 0.25
            ratio_pp_75 = ratio <= 0.75
            RVB[:,:,0] = np.where(presence_not_0,np.where((ratio_pg_5) & (ratio_pp_75),(((ratio - 0.5)//0.25) + ((ratio - 0.5)%0.25)*4)*255,np.heaviside(ratio - 0.6, 0.5)*255), 0)
            RVB[:,:,1] = np.where(presence_not_0, np.where((ratio_pg_25) & (ratio_pp_75), 255, np.where(ratio_pp_5, ((((ratio)//0.25) + ((ratio)%0.25)*4))*255, ((1 - ((ratio - 0.75)//0.25) -((ratio - 0.75)%0.25)*4))*255)),0)
            RVB[:,:,2] = np.where(presence_not_0, np.where((ratio_pp_5) & (ratio_pg_25),255 - (((ratio - 0.25)//0.25)+((ratio - 0.25)%0.25)*4)*255,np.heaviside(0.3 - ratio, 0.5)*255),0)
            

            color_map[:n] = np.array(RVB,dtype = np.uint8)

                
            legende = creer_legende(n, temp_min, temp_max, compteur_Pays, liste_models[compteur_models], liste_Pays, date)
            color_map[n:] = legende

            img = Image.fromarray(color_map, 'RGB')
            img.show()


            if Sauvegarder:
                nom = "C:\\Users\\Tanguy Chatelain\\Documents\\Programmes\\API\\Cartes\\{}\\Carte {} le {}_{}_{}.png".format(liste_models[compteur_models].upper(),Pays, date[6:], date[4:6], date[:4])
                img.save(nom)
    comp = ''
    while not(comp in ['Y','N']):
        comp = input("Comparer les modèles ? (Y/N)\n>>> ").upper()
        if  comp == 'Y':
            from Comparateur import comparer
            comparer(results, l_presence, liste_Pays, liste_models)


#################################################################################
#################################################################################
l_m = [31,28,31,30,31,30,31,31,30,31,30,31]
dates = [[k+1 for k in range(m)] for m in l_m]
for i,mois in enumerate(dates):
    for j,jour in enumerate(mois):
        s_jour = str(jour)
        if len(s_jour) == 1:
            dates[i][j] = '0' + s_jour
        else:
            dates[i][j] = s_jour

def enregistrer(liste, nom):
    nomtxt = nom + '.txt'
    k = 0
    while nomtxt in os.listdir('.'):
        k+=1
        nomtxt = nom + '(' + str(k) + ')' + '.txt'
    fichier = open(nomtxt, 'wb')
    pickle.dump(liste, fichier)
    fichier.close()

def seconds_to_hours(secondes):
    minutes = secondes/60
    heures = (secondes/60)//60
    return "{} heures {} minutes".format(round(heures), round(minutes - 60*heures))

l_t = []
c= 0
#long_min,long_max, lat_min, lat_max= 40.38105,51.73387,-2.28325,12.62464
l_mois = ['01','02','03','04','05','06','07','08','09','10','11','12']
annee = '2021'
Pays = ["Inde"]
model = ["Tdb"]
t0 = time()
for i, mois in enumerate(l_mois):
    for j, jour in enumerate(dates[i]):
        c +=1
        date = annee + mois + jour
        nom = jour + '_' + mois + '_' + annee
        Carte(2000, nom, Pays, model, False, False)
        print('\nTerminé :',nom)
        t1 = time()
        l_t.append(t1 - t0)
        t0 = time()
        t_moy = np.mean(l_t)
        j_res = 365 - c
        print('Temps restant :', seconds_to_hours(j_res*t_moy))


