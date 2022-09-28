import matplotlib.pyplot as plt
import pickle
import os
import numpy as np
from scipy.special import comb as combinaison

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
    
path = os.getcwd()
path = os.path.dirname(path)
os.chdir(path)
data = lire("corrélation")

#data[i,j,k]
#i désigne le pays:
#0 = France
#1 = Canada
#2 = Inde
#3 = Somalie
#j désigne le jour de l'année 2021 (de 0 à 364)
#k désigne la corrélation -> va de 0 à 14
#L'ordre de k est le même que celui qui est print quand on lance le programme


X = np.arange(365)
#plt.plot(X, data[3,:, 7],label="Humidex - UTCI", color = 'blue')
plt.plot(X, data[1,:,10],label="Modèle créé - UTCI", color = 'blue')
plt.plot(X, data[1,:, 5],label="Modèle créé - Humidex", color = 'red')
plt.xlabel("Jour")
plt.ylabel("Coefficient de corrélation")
plt.title("Evolution du coefficient de corrélation au Canada en 2021")
plt.legend()
plt.show()

liste_Pays = ["France", "Canada", "Inde", "Somalie"]
liste_models = ["at","humidex","Modèle personnel", "Tdb", "utci", "Wind Chill"]
for p, Pays in enumerate(liste_Pays):
    print('\n\n',Pays,'\n')
    i = 0
    j = 0
    maxi = len(liste_models) - 1
    for m in range(int(combinaison(len(liste_models),2))):
        j += 1
        if j > maxi:
            i += 1
            j = i + 1
        r = np.mean(data[p,:,m])
        print("Corrélation {} - {} :".format(liste_models[i], liste_models[j]), round(r, 3))
