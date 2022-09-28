import os
import time
import pickle
from Recup_donnees2 import get_data
import numpy as np

os.chdir(r'C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_meteo\Canada')
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
long_min,long_max, lat_min, lat_max= -141.59778,-55.08338,41.075105,72.52053
l_mois = ['01','02','03','04','05','06','07','08','09','10','11','12']
annee = '2021'

t0 = time.time()
for i, mois in enumerate(l_mois):
    for j, jour in enumerate(dates[i]):
        c +=1
        date = annee + mois + jour
        coords, meteo, azimuth = get_data(date, long_min, long_max, lat_min, lat_max)
        nom = jour + '_' + mois + '_' + annee
        enregistrer([coords, meteo, azimuth], nom)
        print('\nTerminé :',nom)
        t1 = time.time()
        l_t.append(t1 - t0)
        t0 = time.time()
        t_moy = np.mean(l_t)
        j_res = 365 - c
        print('Temps restant :', seconds_to_hours(j_res*t_moy))

