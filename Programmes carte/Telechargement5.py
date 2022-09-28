import numpy as np
import os
import pickle
from time import time
from copy import deepcopy
from scipy.special import comb as combinaison  # k parmi n
    

def comparer(results, l_presence, liste_Pays, liste_models):
    for p, Pays in enumerate(liste_Pays):

        presence = l_presence[p]
        Di,Dj = np.shape(presence)
        presence_flat = np.reshape(presence, Di * Dj)
        i = 0
        j = 0
        maxi = len(liste_models) - 1
        #print("\n\n{} : \n".format(liste_Pays[p]))
        mod_temperatures = results[p]
        for m in range(int(combinaison(len(liste_models),2))):
            j += 1
            if j > maxi:
                i += 1
                j = i + 1
            
            arr1 = np.reshape(mod_temperatures[i], Di * Dj).astype(np.float64)
            arr1 = np.delete(arr1, np.where(presence_flat == 0))
            arr2 = np.reshape(mod_temperatures[j], Di * Dj).astype(np.float64)
            arr2 = np.delete(arr2, np.where(presence_flat == 0))
            r = np.cov(arr1, arr2)[0][1] / (np.std(arr1) * np.std(arr2))
            data[p, c-1, m] = r
            #print("Corrélation {} - {} :".format(liste_models[i], liste_models[j]), round(r, 3))





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

def lire(nom):
    nom = nom + '.txt'
    if nom in os.listdir('.'):
        fichier = open(nom, 'rb')
        liste = pickle.load(fichier)
        fichier.close()
        return liste

def seconds_to_hours(secondes):
    minutes = secondes/60
    heures = (secondes/60)//60
    return "{} heures {} minutes".format(round(heures), round(minutes - 60*heures))


liste_Pays = ["France", "Canada", "Inde", "Somalie"]
liste_models = ["at","humidex","Modèle personnel", "Tdb", "utci", "Wind Chill"]
l_presence = [0] * len(liste_Pays)
os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_coords")
for compteur_Pays, Pays in enumerate(liste_Pays):
    presence = lire(Pays)[0]
    l_presence[compteur_Pays] = presence
l_t = []
c= 0
l_mois = ['01','02','03','04','05','06','07','08','09','10','11','12']
annee = '2021'
t0 = time()
data = np.zeros((4, 365, 15))
for i, mois in enumerate(l_mois):
    for j, jour in enumerate(dates[i]):
        results = np.zeros((len(liste_Pays), len(liste_models), 2000, 2000), dtype=np.float32)
        c +=1
        date = annee + mois + jour
        nom = jour + '_' + mois + '_' + annee
        for compteur_Pays, Pays in enumerate(liste_Pays):
            for compteur_models, model in enumerate(liste_models):
                os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API\data_Temp_ress\{}\{}".format(model,Pays))
                Tr = lire(nom)
                results[compteur_Pays][compteur_models] = deepcopy(Tr)
        comparer(results, l_presence, liste_Pays, liste_models)
                #enregistrer(Tr, nom)
        print('\nTerminé :',nom)
        t1 = time()
        l_t.append(t1 - t0)
        t0 = time()
        t_moy = np.mean(l_t)
        j_res = 365 - c
        print('Temps restant :', seconds_to_hours(j_res*t_moy))
        if "Stop.txt" in os.listdir(r"C:\Users\Tanguy Chatelain\Desktop"):
            raise ValueError(nom)
os.chdir(r"C:\Users\Tanguy Chatelain\Documents\Programmes\API")
enregistrer(data, "corrélation")
