import numpy as np


def Create_map(n, lp):
    """
    Renvoie la carte vierge du pays considéré, ainsi que 2 listes permettant de passer des coordonnées GPS à celles
    en pixels dans lesquelles est définie la carte vierge

    Paramètres
    ----------
    n : int
        La résolution de la carte (en pixels). La carte ne peut être qu'un carré de dimension n²
    lp : list
        Un ensemble de points décrivant la frontière du pays considéré, dans le sens horaire
    """
 
    def Convertisseur(x1, y1, x2, y2):
        """Calcule la distance entre 2 points"""
        return abs(x2 - x1) + abs(y2 - y1)

    def classage(element1, element2, i, j):
        """Renvoie la position (ic, jc) dans la carte d'un point GPS"""
        for ic in range(i-1, i+2):
            if lt[ic] >= element1[1] >= lt[ic+1] and lt[ic] >= element2[1] >= lt[ic+1]:
                for jc in range(j-1, j+2):
                    if lg[jc] <= element1[0] <= lg[jc+1] and lg[jc] <= element2[0] <= lg[jc+1]:
                        return ic, jc

    def classagel(element, i):
        """Renvoie la latitude d'un point GPS"""
        for new_i in range(i-1, i+2):
            if lt[new_i+1] <= element[1] <= lt[new_i]:
                return new_i

    def classage2(element, j):
        """Renvoie la longitude d'un point GPS"""
        for new_j in range(j-1, j+2):
            if lg[new_j] <= element[0] <= lg[new_j+1]:
                return new_j

    def point_bordure(ip, jp, i, j, element, last_element):
        """
        Renvoie la position (i,j) du point situé à l'intersection entre la bordure et le
        segment [ip,jp] - [i,j]
        """
        if i == ip:
            bordure_lat = []
        elif lt[ip] in [lt[i], lt[i+1]]:
            bordure_lat = [lt[ip]]
        else:
            bordure_lat = [lt[ip+1]]

        if j == jp:
            bordure_long = []
        elif lg[jp] in [lg[j], lg[j+1]]:
            bordure_long = [lg[jp]]
        else:
            bordure_long = [lg[jp+1]]

        lat_x1 = last_element[1]
        long_x1 = last_element[0]
        lat_x2 = element[1]
        long_x2 = element[0]
        
        if len(bordure_lat) == 0 and len(bordure_long) != 0:
            # On construit une fonction lat = f(long) = A x long + B
            A = (lat_x2 - lat_x1) / (long_x2 - long_x1)  # long_x2 != long_x1 car on effectue un mvt horizontal
            B = lat_x1 - A * long_x1
            lat_xm = A*bordure_long[0]+B
            return [[bordure_long[0], lat_xm],
                    [bordure_long[0], lat_xm]]  # [[long_ip, lat_ip],[long_i, lati]] (identiques)

        elif len(bordure_lat) != 0 and len(bordure_long) == 0:
            # On construit une fonction long = f(lat) = A x lat+ B
            A = (long_x2 - long_x1) / (lat_x2 - lat_x1)  # lat_x2 != lat_x1 car on effectue un mvt vertical
            B = long_x1 - A * lat_x1
            long_xm = A*bordure_lat[0] + B
            return [[long_xm, bordure_lat[0]],
                    [long_xm, bordure_lat[0]]]  # [[long_ip, lat_ip],[long_i, lat_i]] (identiques)

        else:
            # On construit une fonction lat = f1(long) = A1 x long + B1
            A1 = (lat_x2 - lat_x1) / (long_x2 - long_x1)  # long_x2 != long_x1 car on effectue un mvt horizontal
            B1 = lat_x1 - A1 * long_x1
            # On construit une fonction long = f2(lat) = A2 x lat + B2
            A2 = (long_x2 - long_x1) / (lat_x2 - lat_x1)  # lat_x2 != lat_x1 car on effectue un mvt vertical
            B2 = long_x1 - A2 * lat_x1

            lat_xm = A1 * bordure_long[0]+B1
            long_xm = A2 * bordure_lat[0] + B2

            if abs(lat_x1 - lat_xm) < abs(lat_x1 - bordure_lat[0]):
                
                return [[bordure_long[0], lat_xm],
                        [long_xm, bordure_lat[0]],
                        0]  # [[long_ip,lat_ip],[long_i,lat_i]]
            else:
                return [[long_xm, bordure_lat[0]],
                        [bordure_long[0], lat_xm],
                        1]  # [[long_ip,lat_ip],[long_i,lat_i]]

    def entree_a_sortie(i, j, entree, sortie):
        """Relie une entrée à sa sortie"""
        res = [[0, [0, 0], 0] for _ in range(len(entree) + len(sortie))]
        res[0][1] = entree[0]
        point1 = entree[0]
        lat_haut = lt[i]
        lat_bas = lt[i+1]
        long_gauche = lg[j]
        l_anti_hor = [[lg[j], lt[i]],
                      [lg[j], lt[i+1]],
                      [lg[j+1], lt[i+1]],
                      [lg[j+1], lt[i]],
                      [lg[j], lt[i]],
                      [lg[j], lt[i+1]],
                      [lg[j+1], lt[i+1]],
                      [lg[j+1], lt[i]]]  # sens trigo
        # On définit la position de l'entrée
        if point1[1] == lat_haut:  # anti-hor
            pos_e = 0  # 0 = haut
        elif point1[1] == lat_bas:
            pos_e = 2  # 2 = bas
        elif point1[0] == long_gauche:
            pos_e = 1  # 1 = gauche
        else:
            pos_e = 3  # 3 = droite
        res[0][2] = pos_e

        c = 0
        for point2 in entree[1:] + sortie:
            c += 1
            res[c][1] = point2        
            distance_temp = 0
            # On définit la position de la sortie
            if point2[1] == lat_haut:  # anti-hor
                pos_s = 0  # 0 = haut
            elif point2[1] == lat_bas:
                pos_s = 2  # 2 = bas
            elif point2[0] == long_gauche:
                pos_s = 1  # 1 = gauche
            else:
                pos_s = 3  # 3 = droite

            # On s'assure que la sorite soit située après l'entrée dans le sens trigonométrique
            if pos_e > pos_s:
                pos_s += 4
            if pos_s == pos_e:
                d_e = Convertisseur(point1[0], point1[1], l_anti_hor[pos_e][0], l_anti_hor[pos_e][1])
                d_s = Convertisseur(point2[0], point2[1], l_anti_hor[pos_s][0], l_anti_hor[pos_s][1])
                if d_e < d_s:
                    pos_s += 4

            # On calcule toute les distances entre l'entrée (choisie) et les différentes sorties auxquelles aucune
            # entrée n'a été attribuée
            res[c][2] = pos_s
            if pos_s == pos_e:
                distance_temp += Convertisseur(point1[0], point1[1], point2[0], point2[1])
                
            elif pos_s == pos_e + 1:
                distance_temp += Convertisseur(point1[0], point1[1], l_anti_hor[pos_e][0], l_anti_hor[pos_e][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e][0], l_anti_hor[pos_e][1], point2[0], point2[1])

            elif pos_s == pos_e + 2:
                distance_temp += Convertisseur(point1[0], point1[1], l_anti_hor[pos_e][0], l_anti_hor[pos_e][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e][0], l_anti_hor[pos_e][1], l_anti_hor[pos_e+1][0],
                                               l_anti_hor[pos_e+1][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e+1][0], l_anti_hor[pos_e+1][1], point2[0], point2[1])

            elif pos_s == pos_e + 3:
                distance_temp += Convertisseur(point1[0], point1[1], l_anti_hor[pos_e][0], l_anti_hor[pos_e][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e][0], l_anti_hor[pos_e][1], l_anti_hor[pos_e+1][0],
                                               l_anti_hor[pos_e+1][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e+1][0], l_anti_hor[pos_e+1][1], l_anti_hor[pos_e+2][0],
                                               l_anti_hor[pos_e+2][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e+2][0], l_anti_hor[pos_e+2][1], point2[0], point2[1])

            elif pos_s == pos_e + 4:
                distance_temp += Convertisseur(point1[0], point1[1], l_anti_hor[pos_e][0], l_anti_hor[pos_e][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e][0], l_anti_hor[pos_e][1], l_anti_hor[pos_e+1][0],
                                               l_anti_hor[pos_e+1][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e+1][0], l_anti_hor[pos_e+1][1], l_anti_hor[pos_e+2][0],
                                               l_anti_hor[pos_e+2][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e+2][0], l_anti_hor[pos_e+2][1], l_anti_hor[pos_e+3][0],
                                               l_anti_hor[pos_e+3][1])
                distance_temp += Convertisseur(l_anti_hor[pos_e+3][0], l_anti_hor[pos_e+3][1], point2[0], point2[1])

            res[c][0] = distance_temp
        res.sort()
        return [res[k][1:] for k in range(len(res))]  # La sortie correspondant à l'entrée choisie est celle ayant la
        # distance <entrée-sortie> minimale

    def points_coins(i, j):
        """Détermine quels coins sont 'à l'intérieur du Pays' """
        
        # La carte tourne dans le sens horaire -> on tourne dans le sens trigonométrique pour savoir où est l'intérieur
        # du pays

        entree = [list(liste_entree[i, j, k]) for k in range(len(liste_entree[i, j])) if liste_entree[i, j, k, 0] != 0]
        sortie = [list(liste_sortie[i, j, k]) for k in range(len(liste_sortie[i, j])) if liste_sortie[i, j, k, 0] != 0]
        l_coin_pos = [3, 0, 1, 2, 3, 0, 1, 2]  # 0 = haut guache, 1 = bas gauche, 2 = bas droite, 3 = haut droite
        direction_coin = []
        entree_sortie = entree_a_sortie(i, j, entree, sortie)
        l_pos = [[entree_sortie[k][1], entree_sortie[k+1][1]] for k in range(0, len(entree_sortie), 2)]
        for pos in l_pos:  # On considère chaque couple pos = [entrée,sortie]
            compteur = 0
            for k in range(pos[0], pos[1]):
                compteur += 1
                if compteur > 1:
                    direction_coin.append(l_coin_pos[k])  # On détermine quels coins se situent dans le pays
        return direction_coin




    lp_np = np.array(lp)
    long_max = max(lp_np[:, 0]) + 0.6  # '+- 0.6' Pour éliminer les conditions aux limites dans la suite
    long_min = min(lp_np[:, 0]) - 0.6
    lat_max = max(lp_np[:, 1]) + 0.6
    lat_min = min(lp_np[:, 1]) - 0.6
    km_lg = Convertisseur(long_max, (lat_max+lat_min)/2, long_min, (lat_max+lat_min)/2)
    km_lt = Convertisseur((long_max+long_min)/2, lat_max, (long_max+long_min)/2, lat_min)

    lg_np = np.linspace(long_min, long_max, n+1)  # Est - Ouest
    lt_np = np.linspace(lat_max, lat_min, n+1)  # Nord - Sud
    lg = lg_np.tolist()
    lt = lt_np.tolist()

    liste_entree = np.zeros((n, n, 3, 2), dtype=np.float64)
    liste_sortie = np.zeros((n, n, 3, 2), dtype=np.float64)
    add = np.zeros((n, n, 2), dtype=np.int16)
    max_entree = 3
    max_sortie = 3
    presence = np.zeros((n, n), dtype=np.int8)
    # presence: 0 = indéfini/Mer, 1 = terres, 2 = côtes, 3 = CL

    d_lim = min(km_lt, km_lg)/(n+1)
    bouclage = True
    while bouclage:
        bouclage = False

        p_element = lp[0]
        ajout = 0
        k = -1
        while k + ajout + 1 < len(lp):  # Tant que la résolution de lp doit être augmentée
            k += 1
            d = Convertisseur(p_element[0], p_element[1], lp[k+ajout][0], lp[k+ajout][1])
            if d > d_lim:  # La résolution de la carte doit être inférieure à celle de lp
                nb = round(d/d_lim) + 2
                m_lg = np.linspace(p_element[0], lp[k+ajout][0], nb)
                m_lt = np.linspace(p_element[1], lp[k+ajout][1], nb)
                for m in range(1, nb):
                    lp.insert(k+m-1+ajout, [m_lg[m], m_lt[m]])  # On augmente la résolution de lp
                ajout += nb - 1
                bouclage = True
            p_element = lp[k+ajout]

        d = Convertisseur(p_element[0], p_element[1], lp[0][0], lp[0][1])  # CL entre la fin et le début
        if d > d_lim:
            nb = round(d / d_lim) + 2
            m_lg = np.linspace(p_element[0], lp[0][0], nb)
            m_lt = np.linspace(p_element[1], lp[0][1], nb)
            for m in range(1, nb):
                lp.append([m_lg[m], m_lt[m]])
            ajout += nb - 1
            bouclage = True

    element = lp[0]
    for i in range(n):
        if lt[i+1] <= element[1] <= lt[i]:
            break

    for j in range(n):
        if lg[j] <= element[0] <= lg[j+1]:
            break

    presence[i, j] = 2
    ip = i
    jp = j
    i_init = i
    j_init = j
    ajout = np.zeros((n, n, 1, 2))
    last_element = lp[0]
    for element in lp[1:]:  # On position chaque point de lp dans la carte
        i = classagel(element, i)
        j = classage2(element, j)

        if i != ip or j != jp:  # On ne s'intéresse qu'aux entrées et aux sorties
            res = point_bordure(ip, jp, i, j, element, last_element)
            if add[ip, jp, 1] != max_sortie:
                liste_sortie[ip, jp, add[ip, jp, 1]] = res[0]
                add[ip, jp, 1] += 1
            else:
                ajout[ip, jp] = res[0]
                liste_sortie = np.append(liste_sortie, ajout, axis=2)
                ajout[ip, jp] = 0
                max_sortie += 1

            if add[i, j, 0] != max_entree:
                liste_entree[i, j, add[i, j, 0]] = res[1]
                add[i, j, 0] += 1
            else:
                ajout[i, j] = res[1]
                liste_entree = np.append(liste_entree, ajout, axis=2)
                ajout[i, j] = 0
                max_entree += 1

            if len(res) == 3:
                ic, jc = classage(res[0], res[1], i, j)
                if add[ic, jc, 0] != max_entree:
                    liste_entree[ic, jc, add[ic, jc, 0]] = res[0]
                    add[ic, jc, 0] += 1
                else:
                    ajout[ic, jc] = res[0]
                    liste_entree = np.append(liste_entree, ajout, axis=2)
                    ajout[ic, jc] = 0
                    max_entree += 1
                if add[ic, jc, 1] != max_sortie:
                    liste_sortie[ic, jc, add[ic, jc, 1]] = res[1]
                    add[ic, jc, 1] += 1
                else:
                    ajout[ic, jc] = res[1]
                    liste_sortie = np.append(liste_sortie, ajout, axis=2)
                    ajout[ic, jc] = 0
                    max_sortie += 1
                presence[ic, jc] = 2
                     
            presence[ip, jp] = 2
            
        ip = i
        jp = j
        last_element = element

    # On traite les conditions aux limites
    i_fin = i
    j_fin = j
    
    presence[i_init, j_init] = 3  # coins des CL non fixés
    presence[i_fin, j_fin] = 3
    del lp #  Afin de gagner en place mémoire
    pos_coins = [[0]*n]*n  # Position des coins à l'intérieur du pays pour chaque pixel,
    # 0 = haut gauche, 1 = bas gauche, 2 = bas droite, 3 = haut droite
    presence_2 = np.where(presence == 2)
    for m in range(len(presence_2[0])):
        #On détermine les coins 'à l'intérieur du pays'
        i = presence_2[0][m]
        j = presence_2[1][m]
        direction_coin = points_coins(i, j)
        pos_coins[i][j] = direction_coin
        # Fondamentalement, si le coin d'un pixel est dans le pays, les 3 pixels adjacents sont dans le pays:
        pixels_adjacents = [[[i-1, j], [i-1, j-1], [i, j-1]],
                            [[i, j-1], [i+1, j-1], [i+1, j]],
                            [[i+1, j], [i+1, j+1], [i, j+1]],
                            [[i, j+1], [i-1, j+1], [i-1, j]]]

        for k in pos_coins[i][j]:
                
            for point in pixels_adjacents[k]:
                i_new, j_new = point[0], point[1]
                if presence[i_new, j_new] == 0:
                    presence[i_new, j_new] = 1
                
    del liste_entree
    del liste_sortie  # Pour gagner en mémoire vive

    # On connait la position de des pixels à l'intérieur du pays au niveau de la frontière,
    # il ne reste plus qu'à étendre par segments
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
                    segment = [element1, element2]
                presence[i, segment[0]: segment[1]] = 1

    presence[i_init, j_init] = 2
    presence[i_fin, j_fin] = 2
    return presence, lg, lt
