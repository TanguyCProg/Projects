import sys
import numpy as np
import os,pickle,json
import threading
from math import radians,cos,sin,asin,sqrt
import matplotlib.pyplot as plt
from PIL import Image,ImageGrab


def Create_map(n,lis):
    def aff_carte():
        france = np.zeros((n,n,3),dtype=np.uint8)
        for i in range(n):
            for j in range(n):
                if presence[i][j] == 1:
                    france[i][j][0] = 1
                elif presence[i][j] == 2:
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
    def Convertisseur2(lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula 
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        # Radius of earth in kilometers is 6371
        km = 6371* c
        return km   

    def Convertisseur(x1,y1,x2,y2):
        return (((x2 - x1)**2) + (y2 - y1)**2)**(1/2)

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


    def point_bordure(ip,jp,i,j):
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

        lat_x1 = liste[ip][jp][-1][-1][1]
        long_x1 = liste[ip][jp][-1][-1][0]
        lat_x2 = liste[i][j][-1][0][1]
        long_x2 = liste[i][j][-1][0][0]
        
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
            if point2[1] == lat_haut: # anti-hor
                pos_s = 0 # 0 = haut
            elif point2[1] == lat_bas:
                pos_s = 2 # 2 = bas
            elif point2[0] == long_gauche:
                pos_s = 1 # 1 = gauche
            else:
                pos_s = 3 # 3 = droite

            if pos_e > pos_s:
                pos_s += 4
            if pos_s == pos_e:
                d_e = Convertisseur(point1[0],point1[1],l_anti_hor[pos_e][0],l_anti_hor[pos_e][1])
                d_s = Convertisseur(point2[0],point2[1],l_anti_hor[pos_s][0],l_anti_hor[pos_s][1])
                if d_e < d_s:
                    pos_s += 4
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

        mini = min(distance)
        return distance.index(mini), pos_e,l_pos_s
                    
                    
                
                
            
            
                

    def points_coins(i,j):
        
        #La carte tourne en sens horaire -> on tourne en sens horaire pour savoir où est la France

        point1 = liste[i][j][-1][0]
        point2 = liste[i][j][-1][-1]
        entree = [liste[i][j][k][0] for k in range(len(liste[i][j])) if liste[i][j][k] != []]
        sortie = [liste[i][j][k][-1] for k in range(len(liste[i][j])) if liste[i][j][k] != []]
        l_anti_hor = [[lg[j],lt[i]],[lg[j],lt[i+1]],[lg[j+1],lt[i+1]],[lg[j+1],lt[i]],[lg[j],lt[i]],[lg[j],lt[i+1]],[lg[j+1],lt[i+1]],[lg[j+1],lt[i]]] #sens trigo
        l_anti_hor_cote = [1,2,3,0,1,2,3,0]
        p_coins = []
        couples = []
        l_pos = []
        direction_case = [] #haut,gauche,bas,droite (0,1,2,3)
        for point in entree:
            k,pos_e,l_pos_s = entree_a_sortie(i,j,point,sortie)
            couples.append([point,sortie[k]])
            sortie.remove(sortie[k])
            l_pos.append([pos_e,l_pos_s[k]])
        for couple, pos in zip(couples,l_pos):
            compteur = 0
            for k in range(pos[0],pos[1]):
                compteur += 1
                if compteur > 1:
                    direction_case.append(l_anti_hor_cote[k])
                p_coins.append(l_anti_hor[k])
        return p_coins, direction_case
            
        

        
    def les_4_coins(ligne,colonne):
        h_g = [lg[colonne],lt[ligne]]
        b_g = [lg[colonne+1],lt[ligne]]
        b_d = [lg[colonne+1],lt[ligne+1]]
        h_d = [lg[colonne],lt[ligne+1]]
        return [h_g,b_g,b_d,h_d]


    def propagation(sens):
        ajout_i = [-1, 0, 1, 0]
        ajout_j = [0, -1, 0, 1]
        if sens == 1:
            debut = 0
            fin = n
            pas = 1
        elif sens == 2:
            debut = n-1
            fin = -1
            pas = -1
        for i in range(debut,fin,pas):
            for j in range(debut,fin,pas):
                if presence[i][j] == 1:
                    for k in range(4):
                        new_i = i + ajout_i[k]
                        new_j = j + ajout_j[k]
                        if presence[new_i][new_j] == 0:
                            presence[new_i][new_j] = 1
        return presence

                    
    def progression(i,j,dir2):
        ajout_i = [-1, 0, 1, 0]
        ajout_j = [0, -1, 0, 1]
        for cote in dir2[i][j]:
            new_i = i + ajout_i[cote]
            new_j = j + ajout_j[cote]
            if presence[new_i][new_j] == 0:
                presence[new_i][new_j] = 1
        return presence

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

        
    liste = [[[[]] for _ in range(n)] for _ in range(n)]
    coins = [[[] for _ in range(n)] for _ in range(n)]
    presence = [[0 for _ in range(n)] for _ in range(n)]



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

        
    lf = list(lf[8513:]) + list(lf[:8513])            

    element = lf[0]
    for i in range(n):
        if lt[i+1] <= element[1] <= lt[i]:
            break

    for j in range(n):
        if lg[j] <= element[0] <= lg[j+1]:
            break


    liste[i][j][0].append(list(element))
    presence[i][j] = 2
    coins[i][j].append([lg[j+1],lt[i]])
    coins[i][j].append([lg[j+1],lt[i]])
    ip = i
    i_init = i
    j_init = j
    jp = j
    i1 = i
    j1 = j
    for element in lf[1:]:
        i = classagel(element, i)
        j = classage2(element, j)

            
        if i == ip and j == jp:
            liste[i][j][-1].append(list(element))
        else:
            liste[i][j].append([])
            liste[i][j][-1].append(list(element))
            res = point_bordure(ip,jp,i,j)
            liste[ip][jp][-1].append(res[0])
            liste[i][j][-1].insert(0,res[1])

            if len(res) == 3:
                ic,jc= classage(res[0],res[1])
                liste[ic][jc].append([])
                liste[ic][jc][-1].append(res[0])
                liste[ic][jc][-1].append(res[1])
                presence[ic][jc] = 2
                     
            presence[ip][jp] = 2
                
        ip = i
        jp = j
    i_fin = i
    j_fin = j
    dir2 = [[[] for _ in range(n)] for _ in range(n)] #haut,gauche,bas,droite (0,1,2,3)
    for i in range(n):
        for j in range(n):
            if presence[i][j] == 2:
                coin, direction_case = points_coins(i,j)
                coins[i][j].extend(coin)
                dir2[i][j].extend(direction_case)
                presence = progression(i,j,dir2)
                
    presence[i_init][j_init] = 3 #coins des CL non fixés
    presence[i_fin][j_fin] = 3
    presence = propagation(1)
    presence = propagation(2)
       
    presence[i_init][j_init] = 2
    presence[i_fin][j_fin] = 2
    return presence, lg, lt
    #if aff_carte():
    #    enregistrer(presence, 'couleurs_carte')
    #    enregistrer([lg,lt], 'lg_lt')
