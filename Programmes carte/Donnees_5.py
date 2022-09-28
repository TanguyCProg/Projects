import sys
import numpy as np
import os,pickle,json
import threading
import time as t
from math import radians,cos,sin,asin,sqrt
import matplotlib.pyplot as plt
from PIL import Image,ImageGrab

n = 5000
#def Create_map(n,lis):
t0 = t.time()
def aff_carte():
    france = np.zeros((n,n,3),dtype=np.uint8)
    for i in range(n):
        for j in range(n):
            if presence[i,j] == 1:
                france[i][j][0] = 1
            elif presence[i,j] == 2:
                france[i][j][1] = 1
    france *= 255
    img = Image.fromarray(france, 'RGB')
    img.show()
    answer = input("Enregistrer les données ? [Y/N]\n>>> ")
    if answer == "Y":
        img.save('imagees.png')
        return True
    return False

    
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
##def Convertisseur2(lon1, lat1, lon2, lat2):
##    """
##    Calculate the great circle distance between two points 
##    on the earth (specified in decimal degrees)
##    """
##    # convert decimal degrees to radians
##    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
##    # haversine formula 
##    dlon = lon2 - lon1 
##    dlat = lat2 - lat1 
##    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
##    c = 2 * asin(sqrt(a)) 
##    # Radius of earth in kilometers is 6371
##    km = 6371* c
##    return km   

def Convertisseur(x1,y1,x2,y2):
    return abs(x2 - x1) + abs(y2 - y1)

def classage(element1,element2):
    for ic in range(n):
        if lt[ic] >= element1[1] >= lt[ic+1] and lt[ic] >= element2[1] >= lt[ic+1]:
            for jc in range(n):
                if lg[jc] <= element1[0] <= lg[jc+1] and lg[jc] <= element2[0] <= lg[jc+1]:
                    return ic,jc
    

def classagel(element, i):
    for new_i in range(i-1,i+2):
        if lt[new_i+1] <= element[1] <= lt[new_i]:
            return new_i


def classage2(element, j):
    for new_j in range(j-1,j+2):
        if lg[new_j] <= element[0] <= lg[new_j+1]:
            return new_j


def point_bordure(ip,jp,i,j, element, last_element):
    if i == ip:
        bordure_lat = []
    elif lt[ip] in [lt[i],lt[i+1]]:
        bordure_lat = [lt[ip]]
    else:
        bordure_lat = [lt[ip+1]]

    if j == jp:
        bordure_long = []
    elif lg[jp] in [lg[j],lg[j+1]]:
        bordure_long = [lg[jp]]
    else:
        bordure_long = [lg[jp+1]]

    lat_x1 = last_element[1]
    long_x1 = last_element[0]
    lat_x2 = element[1]
    long_x2 = element[0]
    
    if len(bordure_lat) == 0 and len(bordure_long) != 0:
        #On construit une fonction lat = f(long) = A x long + B
        A = (lat_x2 - lat_x1)/(long_x2 - long_x1) # long_x2 != long_x1 car on effectue un mvt horizontal
        B = lat_x1 - A*long_x1
        lat_xm = A*bordure_long[0]+B
        return [[bordure_long[0], lat_xm],[bordure_long[0], lat_xm]] #[[long_ip, lat_ip],[long_i, lati]] (identiques)

    elif len(bordure_lat) != 0 and len(bordure_long) == 0:
        #On construit une fonction long = f(lat) = A x lat+ B
        A = (long_x2 - long_x1)/(lat_x2 - lat_x1) #lat_x2 != lat_x1 car on effectue un mvt vertical
        B = long_x1 - A*lat_x1
        long_xm = A*bordure_lat[0] + B
        return [[long_xm,bordure_lat[0]],[long_xm,bordure_lat[0]]] #[[long_ip, lat_ip],[long_i, lati]] (identiques)

    else:
        #On construit une fonction lat = f1(long) = A1 x long + B1
        A1 = (lat_x2 - lat_x1)/(long_x2 - long_x1) # long_x2 != long_x1 car on effectue un mvt horizontal
        B1 = lat_x1 - A1*long_x1
        #On construit une fonction long = f2(lat) = A2 x lat + B2
        A2 = (long_x2 - long_x1)/(lat_x2 - lat_x1) #lat_x2 != lat_x1 car on effectue un mvt vertical
        B2 = long_x1 - A2*lat_x1

        lat_xm = A1*bordure_long[0]+B1
        long_xm = A2*bordure_lat[0] + B2

        if abs(lat_x1 - lat_xm) < abs(lat_x1 - bordure_lat[0]):
            
            return [[bordure_long[0],lat_xm],[long_xm,bordure_lat[0]],0] #[[long_ip,lat_ip],[long_i,lat_i]]
        else:
            return [[long_xm,bordure_lat[0]], [bordure_long[0], lat_xm],1] #[[long_ip,lat_ip],[long_i,lat_i]]


def entree_a_sortie(i,j,point,sortie):
    point1 = point
    l_pos_s = []
    distance = []
    lat_haut = lt[i]
    lat_bas = lt[i+1]
    long_gauche = lg[j]
    long_droite = lg[j+1]
    l_anti_hor = [[lg[j],lt[i]],[lg[j],lt[i+1]],[lg[j+1],lt[i+1]],[lg[j+1],lt[i]],[lg[j],lt[i]],[lg[j],lt[i+1]],[lg[j+1],lt[i+1]],[lg[j+1],lt[i]]] #sens trigo
    #On définit la position de l'entrée
    if point1[1] == lat_haut: # anti-hor
        pos_e = 0 # 0 = haut
    elif point1[1] == lat_bas:
        pos_e = 2 # 2 = bas
    elif point1[0] == long_gauche:
        pos_e = 1 # 1 = gauche
    else:
        pos_e = 3 # 3 = droite
    
    for point2 in sortie:
        distance_temp = 0
        #On définit la position de la sortie
        if point2[1] == lat_haut: # anti-hor
            pos_s = 0 # 0 = haut
        elif point2[1] == lat_bas:
            pos_s = 2 # 2 = bas
        elif point2[0] == long_gauche:
            pos_s = 1 # 1 = gauche
        else:
            pos_s = 3 # 3 = droite

        # On s'assure que la sorite soit située après l'entrée dans le sens trigonométrique
        if pos_e > pos_s:
            pos_s += 4
        if pos_s == pos_e:
            d_e = Convertisseur(point1[0],point1[1],l_anti_hor[pos_e][0],l_anti_hor[pos_e][1])
            d_s = Convertisseur(point2[0],point2[1],l_anti_hor[pos_s][0],l_anti_hor[pos_s][1])
            if d_e < d_s:
                pos_s += 4

        #On calcule toute les distances entre l'entrée (choisie) et les différentes sorties auxquelles aucune entrée n'a été attribuée        
        l_pos_s.append(pos_s)
        if pos_s == pos_e:
            distance_temp += Convertisseur(point1[0],point1[1],point2[0],point2[1])
        elif pos_s == pos_e + 1:
            distance_temp += Convertisseur(point1[0],point1[1],l_anti_hor[pos_e][0],l_anti_hor[pos_e][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e][0],l_anti_hor[pos_e][1],point2[0],point2[1])
        elif pos_s == pos_e + 2:
            distance_temp += Convertisseur(point1[0],point1[1],l_anti_hor[pos_e][0],l_anti_hor[pos_e][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e][0],l_anti_hor[pos_e][1],l_anti_hor[pos_e+1][0],l_anti_hor[pos_e+1][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e+1][0],l_anti_hor[pos_e+1][1],point2[0],point2[1])
        elif pos_s == pos_e + 3:
            distance_temp += Convertisseur(point1[0],point1[1],l_anti_hor[pos_e][0],l_anti_hor[pos_e][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e][0],l_anti_hor[pos_e][1],l_anti_hor[pos_e+1][0],l_anti_hor[pos_e+1][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e+1][0],l_anti_hor[pos_e+1][1],l_anti_hor[pos_e+2][0],l_anti_hor[pos_e+2][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e+2][0],l_anti_hor[pos_e+2][1],point2[0],point2[1])
        elif pos_s == pos_e + 4:
            distance_temp += Convertisseur(point1[0],point1[1],l_anti_hor[pos_e][0],l_anti_hor[pos_e][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e][0],l_anti_hor[pos_e][1],l_anti_hor[pos_e+1][0],l_anti_hor[pos_e+1][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e+1][0],l_anti_hor[pos_e+1][1],l_anti_hor[pos_e+2][0],l_anti_hor[pos_e+2][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e+2][0],l_anti_hor[pos_e+2][1],l_anti_hor[pos_e+3][0],l_anti_hor[pos_e+3][1])
            distance_temp += Convertisseur(l_anti_hor[pos_e+3][0],l_anti_hor[pos_e+3][1],point2[0],point2[1])
        distance.append(distance_temp)

    #La sortie correspondant à l'entrée choisie est celle ayant la distance <entrée-sortie> minimale
    mini = min(distance)
    return distance.index(mini), pos_e, l_pos_s
            
        
        
            

def points_coins(i,j):
    #La carte tourne dans le sens horaire -> on tourne dans le sens trigonométrique pour savoir où est l'intérieur du pays

    entree = [list(liste_entree[i,j,k]) for k in range(len(liste_entree[i,j])) if liste_entree[i,j,k,0] != 0]
    sortie = [list(liste_sortie[i,j,k]) for k in range(len(liste_sortie[i,j])) if liste_sortie[i,j,k,0] != 0]
    l_coin_pos = [3, 0, 1, 2, 3, 0, 1, 2] #0 = haut guache, 1 = bas gauche, 2 = bas droite, 3 = haut droite
    l_pos = [] #Liste des positions (haut,gauche,bas,droite) des couples [entrée,sortie]
    direction_coin = []
    for point in entree:
        k,pos_e,l_pos_s = entree_a_sortie(i,j,point,sortie)
        sortie.remove(list(sortie[k])) #sortie[k] vient d'être associée à une entrée, on ne doit plus la prendre en compte pour les prochains calculs
        l_pos.append([pos_e,l_pos_s[k]])

    for pos in l_pos: #On considère chaque couple pos = [entrée,sortie]
        compteur = 0
        for k in range(pos[0],pos[1]):
            compteur += 1
            if compteur > 1:
                direction_coin.append(l_coin_pos[k]) #On détermine quels coins se situent dans le pays
    return direction_coin
        
    

    



def propagation():
    ajout_i = [1, 0] #bas, droite
    ajout_j = [0, 1] #bas, droite
    for i in range(n):
        for j in range(n):
            if presence[i,j] == 1:
                for k in range(2):
                    new_i = i + ajout_i[k]
                    new_j = j + ajout_j[k]
                    try:
                        if presence[new_i,new_j] == 0:
                            presence[new_i,new_j] = 1
                    except:
                        aff_carte()
    return presence

            

fchier = lire("Délimitation_France")
aList = json.loads(fchier)
lis = aList['geometry']['coordinates'][0][0]

lf_np = np.array(lis)
long_max = max(lf_np[:,0]) + 0.6 # Pour éliminer les conditiions aux limites dans completion
long_min = min(lf_np[:,0]) - 0.6
lat_max = max(lf_np[:,1]) + 0.6
lat_min = min(lf_np[:,1]) - 0.6
lf = lf_np.tolist()
km_lg = Convertisseur(long_max,(lat_max+lat_min)/2,long_min,(lat_max+lat_min)/2)
km_lt = Convertisseur((long_max+long_min)/2,lat_max,(long_max+long_min)/2,lat_min)
while False:#abs(km_lt - km_lg) > 1: # On ajuste les dimensions pour ne pas avoir une carte étirée
    if km_lg > km_lt: 
        lat_min -= 0.001
        lat_max += 0.001
    else:
        long_min -= 0.001
        long_max += 0.001

    km_lg = Convertisseur(long_max,(lat_max+lat_min)/2,long_min,(lat_max+lat_min)/2)
    km_lt = Convertisseur((long_max+long_min)/2,lat_max,(long_max+long_min)/2,lat_min)

lg_np = np.linspace(long_min, long_max, n+1) #Est - Ouest
lt_np = np.linspace(lat_max, lat_min, n+1) #Nord - Sud
lg = lg_np.tolist()
lt = lt_np.tolist()

t1 = t.time()
print("Création des listes basiques : ",t1 - t0)
liste_entree = np.zeros((n,n,3,2), dtype= np.float64) #   [[[] for _ in range(n)] for _ in range(n)]
liste_sortie =np.zeros((n,n,3,2), dtype = np.float64)# [[[] for _ in range(n)] for _ in range(n)]
add = np.zeros((n,n,2),dtype = np.int16)
max_entree = 3
max_sortie = 3
t2 = t.time()
print("Création de liste : ", t2-t1)
presence = np.zeros((n,n),dtype=np.int16) #[[0 for _ in range(n)] for _ in range(n)]
t3 = t.time()
print("Création de la liste presence : ", t3 - t2)

d_lim = min(km_lt,km_lg)/(n+1)
lg_lim = lg[1] - lg[0]
lt_lim = lt[0] - lt[1]
bouclage = True
while bouclage:
    bouclage = False

    p_element = lf[0]
    ajout = 0
    k= -1
    while k+ajout+1 < len(lf):
        k += 1
        d = Convertisseur(p_element[0],p_element[1],lf[k+ajout][0],lf[k+ajout][1])
        if d > d_lim:
            nb = round(d/d_lim) + 2
            m_lg = np.linspace(p_element[0],lf[k+ajout][0],nb)
            m_lt = np.linspace(p_element[1],lf[k+ajout][1],nb)
            for m in range(1, nb):
                lf.insert(k+m-1+ajout,[m_lg[m],m_lt[m]])
            ajout += nb - 1
            bouclage = True
        p_element = lf[k+ajout]

    d = Convertisseur(p_element[0],p_element[1],lf[0][0],lf[0][1]) #cond limite entre la fin et le début
    if d > d_lim:
        nb = round(d/d_lim) + 2
        m_lg = np.linspace(p_element[0],lf[0][0],nb)
        m_lt = np.linspace(p_element[1],lf[0][1],nb)
        for m in range(1, nb):
            lf.append([m_lg[m],m_lt[m]])
        ajout += nb -1
        bouclage = True

t4 = t.time()
print("Rajout de points : ",t4-t3)
element = lf[0]
for i in range(n):
    if lt[i+1] <= element[1] <= lt[i]:
        break

for j in range(n):
    if lg[j] <= element[0] <= lg[j+1]:
        break


presence[i,j] = 2
ip = i
jp = j
i_init = i
j_init = j
ajout = np.zeros((n,n,1,2))
last_element = lf[0]
for element in lf[1:]:
    i = classagel(element, i)
    j = classage2(element, j)

        
    if i != ip or j != jp:
        res = point_bordure(ip,jp,i,j,element,last_element)
        if add[ip,jp,1] != max_sortie:
            liste_sortie[ip,jp,add[ip,jp,1]] = res[0]
            add[ip,jp,1] += 1
        else:
            ajout[ip,jp] = res[0]
            liste_sortie = np.append(liste_sortie, ajout, axis = 2)
            ajout[ip,jp] = 0
            max_sortie += 1

        if add[i,j,0] != max_entree:
            liste_entree[i,j,add[i,j,0]] = res[1]
            add[i,j,0] += 1
        else:
            ajout[i,j] = res[1]
            liste_entree = np.append(liste_entree, ajout, axis = 2)
            ajout[i,j] = 0
            max_entree += 1
        

        if len(res) == 3:
            ic,jc= classage(res[0],res[1])
            if add[ic,jc,0] != max_entree:
                liste_entree[ic,jc,add[ic,jc,0]] = res[0]
                add[ic,jc,0] += 1
            else:
                ajout[ic,jc] = res[0]
                liste_entree = np.append(liste_entree, ajout, axis = 2)
                ajout[ic,jc] = 0
                max_entree += 1
            if add[ic,jc,1] != max_sortie:
                liste_sortie[ic,jc,add[ic,jc,1]] = res[1]
                add[ic,jc,1] += 1
            else:
                ajout[ic,jc] = res[1]
                liste_sortie = np.append(liste_sortie, ajout, axis = 2)
                ajout[ic,jc] = 0
                max_sortie += 1
            presence[ic,jc] = 2
                 
        presence[ip,jp] = 2
            
    ip = i
    jp = j
    last_element = element
i_fin = i
j_fin = j
presence[i_init,j_init] = 3 #coins des CL non fixés
presence[i_fin,j_fin] = 3
del lf
t5=t.time()
print("Positionnement des bords : ", t5-t4)
pos_coins = [[0]*n]*n #np.zeros((n,n), dtype= np.int8) # position des coins à l'intérieur du pays pour chaque pixel, 0 = haut gauche, 1 = bas gauche, 2 = bas droite, 3 = haut droite
for i in range(n):
    for j in range(n):
        if presence[i,j] == 2:
            direction_coin = points_coins(i,j)
            pos_coins[i][j] = direction_coin
            points = [[[i-1,j], [i-1, j-1], [i, j-1]],[[i,j-1], [i+1, j-1], [i+1, j]],[[i+1, j], [i+1, j+1], [i, j+1]],[[i, j+1], [i-1, j+1], [i-1, j]]]

            for k in pos_coins[i][j]:
##                if k == 0:
##                    points = [[i-1,j], [i-1, j-1], [i, j-1]]
##                elif k == 1:
##                    points = [[i,j-1], [i+1, j-1], [i+1, j]]
##                elif k == 2:
##                    points = [[i+1, j], [i+1, j+1], [i, j+1]]
##                elif k == 3:
##                    points = [[i, j+1], [i-1, j+1], [i-1, j]]
                    
                for point in points[k]:
                    i_new, j_new = point[0], point[1]
                    if presence[i_new,j_new] == 0:
                        presence[i_new,j_new] = 1
            
t6 = t.time()
print("Recherche des coins : ",t6-t5)
del liste_entree
del liste_sortie #liste_entree/sortie consomme beaucoup de mémoire vive et ralentit considérablement le programme, on la supprime dès que possible


segments = []
for i in range(n):
    presence_1 = np.where(presence[i] == 1)[0]
    presence_2 = np.where(presence[i] == 2)[0]
    if len(presence_1) != 0:
        for k in range(len(presence_1)-1):
            element1 = presence_1[k]
            element2 = presence_1[k+1]
            if len(presence_2) != 0:
                for element3 in presence_2:
                    if element1 <= element3 <= element2:
                        segment = [element1, element3]
                        break
                    else:
                        segment = [element1, element2]
            else:
                segment = [element1,element2]
            presence[i,segment[0]: segment[1]] = 1
            
        
    

    

##encadrement = np.zeros((n,2), dtype = np.int16)
##for i in range(n):
##    enc_j = np.where(presence[i] == 1)[0]
##    if len(enc_j) == 0:
##        enc_j = [0,n-1]
##    encadrement[i,0] = min(enc_j)
##    encadrement[i,1] = max(enc_j)
##for i in range(n):
##    for j in range(encadrement[i,0],encadrement[i,1]):
##        if presence[i,j] == 1 and presence[i,j+1] == 0:
##            presence[i,j+1] = 1


t7 = t.time()
print("Propagation : ",t7-t6)
presence[i_init,j_init] = 2
presence[i_fin,j_fin] = 2
    #return presence, lg, lt


#if aff_carte():
#    enregistrer(presence, 'couleurs_carte')
#    enregistrer([lg,lt], 'lg_lt')

