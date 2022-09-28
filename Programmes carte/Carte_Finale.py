from PIL import Image, ImageFont, ImageDraw
import numpy as np
import os
import pickle
import json
import os.path as path
from time import time
from Donnees_6 import Create_map
from Recup_donnees import get_data
import tkinter as tk


def lire(nom):
    nom = nom + '.txt'
    if nom in os.listdir('.'):
        fichier = open(nom, 'rb')
        liste = pickle.load(fichier)
        fichier.close()
        return liste


def creer_legende(n, temp_min, temp_max):
    if Pays == 'France':
        nom = "Carte de la France le {}/{}/{}".format(date[6:], date[4:6], date[:4])
    elif Pays == 'Canada':
        nom = "Carte du Canada le {}/{}/{}".format(date[6:], date[4:6], date[:4])
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



def test(nombre):
    import time as t
    from random import randint
    liste = [randint(0,100)/100 for i in range(nombre*nombre)]
    t0 = t.time()
    for element in liste:
        colori(element)
    print(t.time() - t0)

    liste = [randint(0,100)/100 for i in range(nombre*nombre)]
    t0 = t.time()
    for element in liste:
        color(element,0,1)
    print(t.time() - t0)

    liste = [randint(0,100)/100 for i in range(nombre*nombre)]
    t0 = t.time()
    for element in liste:
        coloria(element)
    print(t.time() - t0)
    


def seconds_to_minutes(secondes):
    minutes = secondes//60
    return "{} minutes {} secondes".format(round(minutes), round(secondes - 60*minutes))


def encadrer(indexes, temp):
    i0 = indexes[0][0]
    compteur = 1
    for index in indexes[1:]:
        if index[0] == i0:
            compteur += 1
    ind = list(indexes)
    ind.sort()
    points = np.reshape(ind,(len(indexes)//compteur, compteur, 2))
    points_pyt = points.tolist()
    
    temp_mat = np.zeros((len(indexes)//compteur, compteur))
    for i in range(len(indexes)//compteur):
        for j in range(compteur):
            temp_mat[i,j] = temp[indexes.index(points_pyt[i][j])]
    return points, points_pyt, temp_mat


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
    global Pays, val_Annee, val_Mois, val_Jour, n
    Pays = str(clicked.get())
    val_Annee = str(Champ_Annee.get())
    val_Mois = str(Champ_Mois.get())
    val_Jour = str(Champ_Jour.get())
    n = int(Champ_n.get())
    Pays = ['']*2
    Pays[0] = France.get()
    Pays[1] = Canada.get()
    Fenetre.destroy()
    
    
Fenetre = tk.Tk()
Fenetre.geometry('600x600')
liste_pays = ["France",
              "Canada"
              ]

clicked = tk.StringVar()
clicked.set(liste_pays[0])

drop = tk.OptionMenu(Fenetre, clicked, *liste_pays)
drop.place(x='100', y='350')

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

Canada = IntVar()
boutton_Canada = tk.Checkbutton(Fenetre, text = 'Canada', variable = Canada)
boutton_Canada.place(x = '100', y = '380')

Fenetre.mainloop()


date = val_Annee + val_Mois + val_Jour

if Pays == 'France':
    fchier = lire("Délimitation_France")
    aList = json.loads(fchier)
    lis = aList['geometry']['coordinates'][0][0]
    
elif Pays == 'Canada':
    with open('Délimitation_Canada2.json') as mon_fichier:
        data = json.load(mon_fichier)
    lis = data['features'][0]["geometry"]["coordinates"][10][0]


lf_np = np.array(lis)
long_max = max(lf_np[:, 0]) +0.6
long_min = min(lf_np[:, 0]) -0.6
lat_max = max(lf_np[:, 1]) +0.6
lat_min = min(lf_np[:, 1]) -0.6

print("Création de la carte vierge...")
t0 = time()
presence, lg, lt = Create_map(n,lis)
t1 = time()
print("Done,",seconds_to_minutes(t1 - t0))
print("\nRécupération des données météo...")
coords, temp, _ = get_data(date, long_min, long_max, lat_min, lat_max)
presence = np.array(presence)
t2 = time()
print("Done,",seconds_to_minutes(t2 - t1))
print("\nExtension des données à l'ensemble de la carte...")

presence = np.where(presence == 2, 0, presence)


indexes = []
temperatures = np.zeros((n,n),dtype=np.float16)
for k in range(len(temp)):
    i, j = find_lat(coords[k][1]), find_long(coords[k][0])
    indexes.append([i, j])
points, points_pyt, temp_mat = encadrer(indexes, temp)
liste_deltas = []
liste_ratio = [[],[],[],[]]
num = 0
tot = (len(points)-1)*(len(points[0])-1)
c = 0
for i1 in range(len(points)-1):
    for j1 in range(len(points[0])-1):
        c+= 1
        ctot = round((c/tot)*100)
        if ctot % 3 == 0:
            print(ctot,'%',end = '\r')
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
                    liste_ratio[num].extend([ratio0, ratio1, ratio2, ratio3])
                    temp0 = temp_mat[i1, j1]
                    temp1 = temp_mat[i1+1, j1]
                    temp2 = temp_mat[i1+1, j1+1]
                    temp3 = temp_mat[i1, j1+1]
                    temperatures[i2,j2] = (temp0 * ratio0 + temp1 * ratio1 + temp2 * ratio2 + temp3 * ratio3)
            liste_ratio[num] = np.reshape(liste_ratio[num], (delta_i1, delta_j1,4))
        else:
            num = liste_deltas.index([delta_i1, delta_j1])
            compteur = 0
            temp0 = temp_mat[i1, j1]
            temp1 = temp_mat[i1+1, j1]
            temp2 = temp_mat[i1+1, j1+1]
            temp3 = temp_mat[i1, j1+1]
            temperatures[points[i1,j1,0]: points[i1+1,j1,0], points[i1,j1,1]: points[i1,j1+1,1]] = liste_ratio[num][:,:,0] * temp0 + liste_ratio[num][:,:,1] * temp1+ liste_ratio[num][:,:,2] * temp2 + liste_ratio[num][:,:,3] * temp3



t3 = time()
print("Done,",seconds_to_minutes(t3 - t2))


print("\nConversion au format PNG...")
color_map = np.zeros((len(lg)+299, len(lt)-1, 3), dtype=np.uint8)
t_max = max(temp)
t_min = min(temp)
temp_max = np.max(np.where(presence!=0,temperatures,t_min))
temp_min = np.min(np.where(presence!=0,temperatures,t_max))
dtemp = (temp_max - temp_min)
c= 0
tot = (len(lg)-1) **2
ratio = 1 - (temp_max   - temperatures)/dtemp
RVB = np.zeros((n,n,3),dtype = np.float16)
RVB[:,:,0] = np.where(presence!= 0,np.where((ratio >=0.5) & (ratio <= 0.75),(((ratio - 2*0.25)//0.25) + ((ratio - 2*0.25)%0.25)*4)*255,np.heaviside(ratio - 0.6, 0.5)*255), 0)
RVB[:,:,1] = np.where(presence != 0, np.where((ratio >= 0.25) & (ratio <= 0.75), 255, np.where(ratio < 0.5, ((((ratio)//0.25) + ((ratio)%0.25)*4))*255, ((1 - ((ratio - 3*0.25)//0.25) -((ratio - 3*0.25)%0.25)*4))*255)),0)
RVB[:,:,2] = np.where(presence != 0, np.where((ratio <=0.5) & (ratio >= 0.25),255 - (((ratio - 0.25)//0.25)+((ratio - 0.25)%0.25)*4)*255,np.heaviside(0.3 - ratio, 0.5)*255),0)


color_map[:n] = np.array(RVB,dtype = np.uint8)

    
legende = creer_legende(n, temp_min, temp_max)
color_map[n:] = legende

img = Image.fromarray(color_map, 'RGB')
t4 = time()
print("\nDone,",seconds_to_minutes(t4 - t3))
img.show()
t4 = time()
print("\n\nCarte réalisée en :",seconds_to_minutes(t4 - t0))

sauvegarde = input("\nSauvegarder la carte ? (Y/N)\n>>> ")
while not(sauvegarde in ['Y', 'N']):
    sauvegarde = input("Sauvegarder la carte ? (Y/N)\n>>> ")

if sauvegarde == 'Y':
    if Pays == 'France':
        nom = "C:\\Users\\Tanguy Chatelain\\Documents\\Programmes\\API\\Cartes\\Carte de la France le {}_{}_{}.png".format(date[6:], date[4:6], date[:4])
    elif Pays == 'Canada':
        nom = "C:\\Users\\Tanguy Chatelain\\Documents\\Programmes\\API\\Cartes\\Carte du Canada le {}_{}_{}.png".format(date[6:], date[4:6], date[:4])
    img.save(nom)
