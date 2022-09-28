import numpy as np


def MRT(Solar_radiation, sun_altitude, view_angle, sun_azimuth,
        Temp_dew_point, Cloudiness, Temp_dry_bulb, Ap = 0.7):
    """
    Paramètres
    ----------
    (Solar_radiaton, sun_altitude, view_angle, sun_azimuth, Temp_dew_point,
    Cloudiness, Temp_dry_bulb, Ap = 0.7)

    Solar_radiation: Radiation solaire en W/m²
    Sun_altitude: angle du soleil dans le ciel variant dans la journée, compris
        entre -90 et 90 degrés (0° = au dessus de notre tête)
    view_angle: Angle minimale à partir duquel le soleil peut nous voir, en
        espace ouvert vaut 0, et augmente si un bâtiment fait de l'ombre,
        varie entre 0 et 90 degrés
    sun_azimuth: angle du soleil par rapport à en face de nous, phi en coord sphériques, en degrés, de 0 à 360
    Temp_dew_point: Température de rosée, en dégrés celsius
    Cloudiness: Couvertuge nuageuse, varie de 0 à 10. 0 = Nuageux, 10 = clair
    Temp_dry_bulb: Température de l'air, en degrés celsius
    Ap: Absorption du rayonnement par le corps humain, vaut 0.7
    """
    deg_to_rad = 0.0174532925
    sigma = 5.670367 * 10 ** -8
    angle = view_angle * deg_to_rad
    altitude = sun_altitude * deg_to_rad
    azimuth = sun_azimuth * deg_to_rad
    Tdp= Temp_dew_point + 273
    Tdb = Temp_dry_bulb + 273
    Cloud = Cloudiness

    Fsp = 0.0355 * np.abs(np.sin(altitude)) + 2.33 * np.abs(np.cos(altitude)) * (0.0213 * (np.cos(azimuth) ** 2) + 0.0091 * (np.sin(azimuth) ** 2)) ** 0.5
    Skye = (0.787 + 0.764 * np.log(Tdp / 273)) * (1 + 0.0224 * Cloud - 0.0035 * (Cloud ** 2) + 0.00028 * (Cloud ** 3))
    Esky = Skye * sigma * (Tdb ** 4)
    
    Fskyp = 1 - ((np.sin(angle) ** 2) + np.cos(angle) - 1) * (np.cos(angle) ** -1)

    Tmrt = ((((1 / sigma) * ((Ap * Solar_radiation * Fsp) + (Skye * Esky * Fskyp)))) ** 0.25) - 273

    return Tmrt

def Temp_ress(Ta, Sol_rad, v, Rh):
    """
    Parameters:
    -----------
    Ta: température ambiante (°C)
    Sol_rad: radiation solaire (W/m²)
    v: vitesse du vent (m/s)
    position: 'standing', 'supine' ou 'seated'
    """

    def clo_to_R(clo):
        return clo * 0.155 / S

    def hc(ts, ta, v):
        h = np.where(v > 1, 8.7 * v ** 0.6, 0)
        h = np.where(v <= 1, 3.5 + 5.2 * v, h)
        h = np.where(v < 0.25, np.sign(Ts - Ta) * 2.38 * (np.abs(Ts - Ta)) ** 0.25, h)
        h = np.where(ts == ta, 1, h)
        return h

    shape = np.shape(Ta)

    ### VARIABLES ###
    Ts = 32  # Température de surface
    Tint = 37  # Température du corps
    S = 1.8  # m²
    clo = 0.4  # Caractérise la couche de vêtement
    h = hc(Ts, Ta, v)  # Coefficient de conducto-convection
    ### VARIBLES ###

    ### CONSTANTES ###
    # Rajouter k après température siignifie quelle est en Kelvin
    Tsk = Ts + 273.15
    Tak = Ta + 273.15
    Hvap = 44500  # J/mol Enthalpie d'évaporation de l'eau
    Psueur = 1.1*10**-5  #  Débit de sueur: Moyen = 1.1 * 10 ** -5 / Maxi = 1.1 * 10 ** -4 (L/s)
    Meau = 0.018  # kg/mol Masse molaire de l'eau
    peau = 1  # densité de l'eau
    sigma = 5.67 * 10 ** -8  # Constante de Boltzman
    eps = 0.98  # absorption du rayonnement du corps humain
    lambda_epiderme = 0.21
    e_epiderme = 0.0025
    R_cond_conv = 1/(h*S)
    R_epiderme = e_epiderme/(lambda_epiderme * S)
    R_vet = clo_to_R(clo)
    R_tot = R_cond_conv + R_vet + R_epiderme
    ### CONSTANTES ###

    Temp_dew_point = Ta - ((100 - Rh)/5)
    Cloudiness = 10
    sun_azimuth = view_angle = sun_altitude = 0
    Tmrt = MRT(Sol_rad, sun_altitude, view_angle, sun_azimuth,
        Temp_dew_point, Cloudiness, Ta)
    

    ### FLUX ###
    #Ray = sigma * eps * ((Tsk**4) - (Tak ** 4)) * S #Rayonnement infrarouge émis par le corps
    Ray1 = sigma * eps * (Tsk**4) * S
    Ray2 = sigma * eps * (Tmrt**4) * S
    Ray = Ray1 - Ray2
    Cond = (Ts - Ta) / R_tot  # Conducto-convection 2 car recto verso
    Evap = (Hvap * Psueur * peau/Meau)  # Evaporation
    ### FLUX ###

    Flux = Ray + Cond + Evap  # Flux total (compté sortant positif)
    Flux_2 = Ray + Cond + Evap  # Flux sortant uniquement
##
##    print("Rayonnement infrarouge :",round(Ray,1),"W")
##    print("Rayonnement solaire :",round(Sol,1),"W")
##    print("Conducto-Convection :",round(Cond,1),"W")
##    print("Evaporation :",round(Evap,1),"W")
##    print("\nFlux sortant total :",round(Flux,1),"W\n\n")
##
##    print("Rayonnement :",round(100*(Ray)/Flux_2,1),"%")
##    print("Conducto-Convection :",round(100*Cond/Flux_2,1),"%")
##    print("Evaporation :",round(100*Evap/Flux_2,1),"%")
    
    ### TEMPERATURE RESSENTIE ###
    h = hc(Ts, Ta, 0)
    Psueur = 1.1 * 10 ** -5
    clo = 0.4

    R_cond_conv = 1 / (h * S)
    R_vet = clo_to_R(clo)
    R_tot = R_cond_conv + R_vet + R_epiderme

    Evap = (Hvap * Psueur * peau/Meau)

    res = (-Flux + Evap + (Tsk / R_tot) + sigma * eps * (Tsk ** 4) * S) / (sigma * eps * S)

    ### dichotomie matricielle ###
    Cst = R_tot * sigma * eps * S

    def f(T, res):
        return (0 + T/Cst) - res

    if len(shape) == 0:
        shape = 1
    ep = 0.09
    a = (np.ones(shape) * -200) + 273
    b = (np.ones(shape) * 200) + 273
    c = (a + b) / 2
    Mata = f(a, res)
    Matb = f(b, res)
    Matc = f(c, res)
    while len(np.where(np.abs(Matc) >= ep)[0]) != 0:
        condition = Mata * Matc > 0
        a = np.where(condition, c, a)
        b = np.where(condition, b, c)
        c = (a + b) / 2
        x = np.where(condition, a, b)
        Matx = f(x, res)
        Mata = np.where(condition, Matx, Mata)
        Matb = np.where(condition, Matb, Matx)
        Matc = f(c, res)
    ### dichotomie matricielle ###

    ### TEMPRERATURE RESSENTIE ###

    return np.round(c, 3) - 273.15

Ta = np.array([25.5,
25.5,
25.5,
25.5,
25.5,
25.5,
25.3,
25.3,
25.3,
25.3,
26,
26,
26,
26])


v = np.array([0,
2.5,
0,
1.5,
7,
9.2,
0,
2,
0,
2,
0,
0,
0,
0])

Sol = np.array([1.7,
1.7,
1.7,
1.7,
1.7,
1.7,
80,
750,
80,
750,
3,
3,
3,
3])

Rh = np.array([44,
44,
44,
44,
44,
44,
43,
43,
43,
43,
77,
77,
98,
98])
print(Temp_ress(Ta, Sol, v, Rh))
#print(Temp_ress(25.3,750, 2, position='standing'))
