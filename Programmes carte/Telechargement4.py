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

n = 2000

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


def lire(nom):
    nom = nom + '.txt'
    if nom in os.listdir('.'):
        fichier = open(nom, 'rb')
        liste = pickle.load(fichier)
        fichier.close()
        return liste

os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_Temp_ress\Tdb\France")

nom = '18_04_2021'
date = "20211220"
temperatures = lire(nom)

os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_coords")
presence = lire('France')[0]


color_map = np.zeros((2000+300, 2000, 3), dtype=np.uint8)
t_max = np.max(temperatures)
t_min = np.min(temperatures)
temp_max = np.max(np.where(presence!=0,temperatures,t_min))
temp_min = np.min(np.where(presence!=0,temperatures,t_max))
dtemp = (temp_max - temp_min)
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

legende = creer_legende(n, temp_min, temp_max, 0, 'Tdb', ['France'], date)
color_map[n:] = legende
img = Image.fromarray(color_map, 'RGB')
img.show()











