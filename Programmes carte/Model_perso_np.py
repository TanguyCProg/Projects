import numpy as np


def Temp_ress(Ta, v, Psueur=1.1*10**-5, clo=0.4):
    """
    Parameters:
    -----------
    Ta: température ambiante (°C)
    v: vitesse du vent (m/s)
    Psueur: Débit de sueur: Moyen = 1.1 * 10 ** -5 / Maxi = 1.1 * 10 ** -4 (L/s)
    clo: caractérise la couche de vêtements (0 à 8)
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
    S = 1.8  # m²
    h = hc(Ts, Ta, v)  # Coefficient de conducto-convection
    ### VARIBLES ###

    ### CONSTANTES ###
    # Rajouter k après température siignifie quelle est en Kelvin
    Tsk = Ts + 273.15
    Tak = Ta + 273.15
    Hvap = 44500  # J/mol Enthalpie d'évaporation de l'eau
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

    ### FLUX ###
    Ray = sigma * eps * ((Tsk**4) - (Tak ** 4)) * S  # Rayonnement infrarouge émis par le corps
    Cond = (Ts - Ta) / R_tot  # Conducto-convection 2 car recto verso
    Evap = (Hvap * Psueur * peau/Meau)  # Evaporation
    Flux = Ray + Cond + Evap  # Flux total (compté sortant positif)
    ### FLUX ###
    
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
        return ((T ** 4) + T / Cst) - res

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
