import numpy as np
from utci_numpy import utci_np
from at_numpy import at_np
from Model_perso_np import Temp_ress


def thermal_model(data, azimuth, model):

    if model == "utci":
        Cloudiness = (100 - np.array(data[:, :, 0], dtype=np.float16)) / 10
        Wind_Speed = np.array(data[:, :, 1], dtype=np.float64) + 0.5
        Tdb = np.array(data[:, :, 2],  dtype=np.float64)
        Humidity = np.array(data[:, :, 3], dtype=np.float64)
        Tdw = np.array(data[:, :, 4], dtype=np.float64)
        ALL_Solar_radiation = np.array(data[:, :, 5], dtype=np.float64)
        Tmrt = MRT(ALL_Solar_radiation, 0, 10, azimuth, Tdw, Cloudiness, Tdb)
        Tr = utci_np(Tdb, Tmrt, Wind_Speed, Humidity)

    elif model == "Tdb":
        Tr = np.array(data[:, :, 2], dtype=np.float16)

    elif model == "at":  # Apparent temperature
        Tdb = np.array(data[:, :, 2], dtype=np.float64)
        Humidity = np.array(data[:, :, 3], dtype=np.float64)
        Humidity = np.where(Humidity == 0, 0.01, Humidity)
        Wind_Speed = np.array(data[:, :, 1], dtype=np.float64)
        Tr = at_np(Tdb, Humidity, Wind_Speed)

    elif model == "humidex":
        Tdb = np.array(data[:, :, 2], dtype=np.float64)
        Humidity = np.array(data[:, :, 3], dtype=np.float64)
        Tr = Tdb + 5 / 9 * ((6.112 * 10 ** (7.5 * Tdb / (237.7 + Tdb)) * Humidity / 100) - 10)
        
    elif model == "Modèle personnel":
        Tdb = np.array(data[:, :, 2], dtype=np.float64)
        Wind_Speed = np.array(data[:, :, 1], dtype=np.float64)
        Tr = Temp_ress(Tdb, Wind_Speed)

    elif model == "Wind Chill":
        Tdb = np.array(data[:, :, 2], dtype=np.float64)
        Wind_Speed = np.array(data[:, :, 1], dtype=np.float64)
        Tr = 13.12 + 0.6215 * Tdb - 11.37 * (Wind_Speed ** 0.16) + 0.3965 * Tdb * (Wind_Speed ** 0.16)
        
    return Tr.astype(np.float16)
               

def MRT(Solar_radiation, sun_altitude, view_angle, sun_azimuth,
        Temp_dew_point, Cloudiness, Temp_dry_bulb, Ap=0.7):
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
    Tdp = Temp_dew_point + 273
    Tdb = Temp_dry_bulb + 273
    Cloud = Cloudiness

    Fsp = 0.0355 * np.abs(np.sin(altitude)) + 2.33 * np.abs(np.cos(altitude)) * (0.0213 * (np.cos(azimuth) ** 2)
                                                                                 + 0.0091 * (np.sin(azimuth) ** 2))**0.5
    Skye = (0.787 + 0.764 * np.log(Tdp / 273)) * (1 + 0.0224 * Cloud - 0.0035 * (Cloud ** 2) + 0.00028 * (Cloud ** 3))
    Esky = Skye * sigma * (Tdb ** 4)
    
    Fskyp = 1 - ((np.sin(angle) ** 2) + np.cos(angle) - 1) * (np.cos(angle) ** -1)

    Tmrt = (((1 / sigma) * ((Ap * Solar_radiation * Fsp) + (Skye * Esky * Fskyp))) ** 0.25) - 273

    return Tmrt
