from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os
import pickle
import json
import os.path as path
from time import time
from Donnees_6 import Create_map
from Recup_donnees2 import get_data
import tkinter as tk
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

def creer_legende(n, temp_min, temp_max, compteur_Pays, model):
    if liste_Pays[compteur_Pays] == 'France':
        nom = "Carte de la France le {}/{}/{} , {}".format(date[6:], date[4:6], date[:4], model)
    elif liste_Pays[compteur_Pays] == 'Canada':
        nom = "Carte du Canada le {}/{}/{} , {}".format(date[6:], date[4:6], date[:4], model)
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


def find_long(long):
    for j in range(1, len(lg)):
        if long <= lg[j]:
            return j-1


def find_lat(lat):
    for i in range(1, len(lt)):
        if lat >= lt[i]:
            return i-1


def Convertisseur(x1, y1, x2, y2):
    return (((x2 - x1)**2) + (y2 - y1)**2)**(1/2)


def selected():
    global liste_Pays, val_Annee, val_Mois, val_Jour, n, liste_models, echelle
    val_Annee = str(Champ_Annee.get())
    val_Mois = str(Champ_Mois.get())
    val_Jour = str(Champ_Jour.get())
    n = int(Champ_n.get())
    liste_Pays = []
    liste_models = []
    if France.get() == 1:
        liste_Pays.append("France")
    if Canada.get() == 1:
        liste_Pays.append("Canada")
    if v_utci.get() == 1:
        liste_models.append('utci')
    if v_at.get() == 1:
        liste_models.append('at')
    if v_temp_dry_bulb.get() == 1:
        liste_models.append("Tdb")
    echelle = bool(v_echelle.get())
    Fenetre.destroy()
    
    
Fenetre = tk.Tk()
Fenetre.geometry('600x600')

boutton = tk.Button(Fenetre, text='Valider', command = selected)
boutton.place(x='250',y='560')

Annee = tk.Label ( Fenetre , text ="Année",bg = 'black',fg='white',bd=5)
Champ_Annee = tk.Entry( Fenetre )
Annee.place(x='95', y = '150')
Champ_Annee.place(x='50', y = '200')

Mois = tk.Label ( Fenetre , text ="Mois",bg = 'black',fg='white',bd=5)
Champ_Mois = tk.Entry( Fenetre )
Mois.place(x='295', y = '150')
Champ_Mois.place(x='250', y = '200')

Jour = tk.Label ( Fenetre , text ="Jour",bg = 'black',fg='white',bd=5)
Champ_Jour = tk.Entry( Fenetre )
Jour.place(x='495', y = '150')
Champ_Jour.place(x='450', y = '200')

l_n = tk.Label ( Fenetre , text ="n",bg = 'black',fg='white',bd=5)
Champ_n = tk.Entry( Fenetre )
l_n.place(x='450', y = '350')
Champ_n.place(x='400', y = '400')

France = tk.IntVar()
boutton_France = tk.Checkbutton(Fenetre, text = 'France', variable = France)
boutton_France.place(x = '100', y = '380')

Canada = tk.IntVar()
boutton_Canada = tk.Checkbutton(Fenetre, text = 'Canada', variable = Canada)
boutton_Canada.place(x = '100', y = '400')

v_utci = tk.IntVar()
boutton_utci = tk.Checkbutton(Fenetre, text = 'UTCI', variable = v_utci)
boutton_utci.place(x = '100', y = '420')

v_at = tk.IntVar()
boutton_at = tk.Checkbutton(Fenetre, text = 'Apparent Temperature', variable = v_at)
boutton_at.place(x = '100', y = '440')

v_temp_dry_bulb = tk.IntVar()
boutton_tdb = tk.Checkbutton(Fenetre, text = 'Dry Bulb Temperature', variable = v_temp_dry_bulb)
boutton_tdb.place(x = '100', y = '460')

v_echelle = tk.IntVar()
boutton_echelle = tk.Checkbutton(Fenetre, text = 'Même échelle', variable = v_echelle)
boutton_echelle.place(x = '100', y = '480')

Fenetre.mainloop()


date = val_Annee + val_Mois + val_Jour
print("Date choisie : {}/{}/{}".format(val_Jour,val_Mois,val_Annee))
results = np.zeros((len(liste_Pays),len(liste_models),n,n),dtype = np.float32)
l_temp_min = np.zeros((len(liste_Pays),len(liste_models)),dtype = np.float32)
l_temp_max = np.zeros((len(liste_Pays),len(liste_models)),dtype = np.float32)
l_presence = [0]*len(liste_Pays)

for compteur_Pays, Pays in enumerate(liste_Pays):

    if Pays == 'France':
        fchier = lire("Délimitation_France")
        aList = json.loads(fchier)
        lis = aList['geometry']['coordinates'][0][0]
        
    elif Pays == 'Canada':
        with open('Délimitation_Canada2.json') as mon_fichier:
            data_geo = json.load(mon_fichier)
        lis = data_geo['features'][0]["geometry"]["coordinates"][10][0]


    lf_np = np.array(lis)
    long_max = max(lf_np[:, 0]) +0.6
    long_min = min(lf_np[:, 0]) -0.6
    lat_max = max(lf_np[:, 1]) +0.6
    lat_min = min(lf_np[:, 1]) -0.6

    print("\n\nCréation de la carte vierge...")
    t0 = time()
    presence, lg, lt = Create_map(n,lis)
    t1 = time()
    print("Done,",seconds_to_minutes(t1 - t0))
    print("\nRécupération des données météo...")
    coords, temp, azimuth = get_data(date, long_min, long_max, lat_min, lat_max)
    presence = np.array(presence,dtype = np.int8)
    t2 = time()
    print("Done,",seconds_to_minutes(t2 - t1))
    print("\nExtension des données à l'ensemble de la carte...")

    presence = np.where(presence == 2, 0, presence)

    indexes = []
    temperatures = np.zeros((n,n,7),dtype=np.float32)
    for k in range(len(temp)): # Associe chaque point GPS où les données météos sont connues à un point dans la matrice (n,n)
        i, j = find_lat(coords[k][1]), find_long(coords[k][0])
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
            if ctot % 3 == 0 and ctot // 3 != last_ctot:
                print(ctot,'%',end = '\r')
                last_ctot = ctot // 3
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
    print("Done,",seconds_to_minutes(t3 - t2))
    for compteur_models, model in enumerate(liste_models):
        t3 = time()
        print("\nCalcul de la température ressentie {}...".format(model))
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
        print("Done,",seconds_to_minutes(t4 - t3))
        
    l_presence[compteur_Pays] = presence
print("\nConversions au format PNG")
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

            
        legende = creer_legende(n, temp_min, temp_max, compteur_Pays, liste_models[compteur_models])
        color_map[n:] = legende

        img = Image.fromarray(color_map, 'RGB')
        t4 = time()
        print("\nDone,",seconds_to_minutes(t4 - t3))
        img.show()
        t4 = time()
        print("\n\nCarte réalisée en :",seconds_to_minutes(t4 - t0))

        sauvegarde = input("\nSauvegarder la carte ? (Y/N)\n>>> ").upper()
        while not(sauvegarde in ['Y', 'N']):
            sauvegarde = input("Sauvegarder la carte ? (Y/N)\n>>> ").upper()

        if sauvegarde == 'Y':
            if Pays == 'France':
                nom = "C:\\Users\\Tanguy Chatelain\\Documents\\Programmes\\API\\Cartes\\{}\\Carte de la France le {}_{}_{}.png".format(liste_models[compteur_models].upper(), date[6:], date[4:6], date[:4])
            elif Pays == 'Canada':
                nom = "C:\\Users\\Tanguy Chatelain\\Documents\\Programmes\\API\\Cartes\\{}\\Carte du Canada le {}_{}_{}.png".format(liste_models[compteur_models].upper(), date[6:], date[4:6], date[:4])
            img.save(nom)
comp = ''
while not(comp in ['Y','N']):
    comp = input("Comparer les modèles ? (Y/N)\n>>> ").upper()
    if  comp == 'Y':
        from Comparateur import comparer
        comparer(results, liste_Pays, liste_models)
