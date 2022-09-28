import numpy as np
from scipy.special import comb as combinaison  # k parmi n
import matplotlib.pyplot as plt
    

def comparer(results, l_presence, liste_Pays, liste_models):
    for p, Pays in enumerate(liste_Pays):

        presence = l_presence[p]
        Di, Dj = np.shape(presence)
        presence_flat = np.reshape(presence, Di * Dj)
        i = 0
        j = 0
        maxi = len(liste_models) - 1
        print("\n\n{} : \n".format(liste_Pays[p]))
        mod_temperatures = results[p]
        for m in range(int(combinaison(len(liste_models), 2))):
            j += 1
            if j > maxi:
                i += 1
                j = i + 1
            
            arr1 = np.reshape(mod_temperatures[i], Di * Dj).astype(np.float64)
            arr1 = np.delete(arr1, np.where(presence_flat == 0))
            arr2 = np.reshape(mod_temperatures[j], Di * Dj).astype(np.float64)
            arr2 = np.delete(arr2, np.where(presence_flat == 0))
            r = np.cov(arr1, arr2)[0][1] / (np.std(arr1) * np.std(arr2))
            print("Corrélation {} - {} :".format(liste_models[i], liste_models[j]), round(r, 3))
