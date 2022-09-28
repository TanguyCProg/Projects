###Programme ayant besoin de:
#Radiation solaire en W/m²
#Altitude du soleil en °
#Température de l'air en °C
#Humidité en %
#Couverture nuageuse en dizième (10 = clair, 0 = nuageux)
#Vitesse du vent (en m/s)

from math import log,sin,cos,pi
from pythermalcomfort import solar_gain
from pythermalcomfort.models import utci as ut
import numpy as np
import matplotlib.pyplot as plt
from pythermalcomfort.models import at
import time as t
#from pythermalcomfort.models import heat_index
#from pythermalcomfort.models import humidex


    

def utci(Solar_radiation, Sun_altitude, Sun_azimuth, Dry_bulb_Temperature,
         Humidity, Cloudiness, Wind_speed):
    """
    Args:
    (Solar_radiaton, Sun_altitude, Dry_bulb_Temperature,
    Humidity, Cloudiness, Wind_speed)

    Solar_radiation: Radiation solaire en W/m²
    Sun_altitude: Angle du soleil dans le ciel variant dans la journée, compris
        entre -90 et 90 degrés (0° = au dessus de notre tête)
    Dry_bulb_Temperature: Température de l'air, en degrés celsius
    Humidity: Humidité en %
    
    Cloudiness: Couvertuge nuageuse, varie de 0 à 10. 0 = Nuageux, 10 = clair
    Wind_speed: Vitesse du vent en m/s
    """

    view_angle = 0  

    Temp_dew_point = Dry_bulb_Temperature - ((100 - Humidity)/5) # Moyenne modification (Delta = 10°C)
    Tmrt = MRT(Solar_radiation, Sun_altitude, view_angle, Sun_azimuth,
               Temp_dew_point, Cloudiness, Dry_bulb_Temperature)
    Tutci = ut(tdb=Dry_bulb_Temperature, tr=Tmrt, v=Wind_speed, rh=Humidity)
    return Tutci

def MRT(Solar_radiation, sun_altitude, view_angle, sun_azimuth,
        Temp_dew_point, Cloudiness, Temp_dry_bulb, Ap = 0.7):
    """
    Args:
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
    sigma = 5.670367 * 10**-8
    angle = view_angle * deg_to_rad
    altitude = sun_altitude * deg_to_rad
    azimuth = sun_azimuth * deg_to_rad
    Tdp= Temp_dew_point + 273
    Tdb = Temp_dry_bulb + 273
    Cloud = Cloudiness



    Fsp = 0.0355 * abs(sin(altitude)) + 2.33 * abs(cos(altitude)) * (0.0213*(cos(azimuth)**2) + 0.0091 * (sin(azimuth)**2))**(1/2)
    Skye = (0.787 + 0.764* log(Tdp/273))*(1+0.0224*Cloud - 0.0035*(Cloud ** 2) + 0.00028*(Cloud**3))
    Esky = Skye*sigma*(Tdb**4)
    

    Fskyp = 1 - ((sin(angle)**2) + cos(angle) - 1)*(cos(angle)**-1)

    Tmrt = ((((1/sigma)*((Ap*Solar_radiation*Fsp)+(Skye*Esky*Fskyp))))**(1/4)) - 273
    print((Ap*Solar_radiation*Fsp)+(Skye*Esky*Fskyp))
    return Tmrt


##Solar_radiation = 500
##
##angle = 0 
##altitude = 0 
##azimuth = 0
##
##humidity = 75 # Entre 0% et 100%. Faible modification de T (Delta = 5°C)
##wind_speed = 0.5 #Entre 0.5 et 17 m/s. Forte modifications de T (Delta = 18°C)
##
##Temp_dry_bulb = 16
##Temp_dew_point = Temp_dry_bulb - ((100 - humidity)/5) # Moyenne modification (Delta = 10°C)
##Cloud = 9         # De 0 (opaque) à 10 (ciel clair)
##
##
##X = np.linspace(-90,90,500)
##Y1 = []
##Y2 = []
##
##for altitude in X:
##    Tmrt = MRT(Solar_radiation, altitude, angle, azimuth, Temp_dew_point, Cloud,
##             Temp_dry_bulb)
##    Y2.append(ut(tdb=Temp_dry_bulb, tr=Tmrt, v=wind_speed, rh=humidity))
##
##    Y1.append(Tmrt)
##
##X3 = np.linspace(0.5,17,100)
##Y3 = []
##for wind_speed in X3:
##    Y3.append(ut(tdb=Temp_dry_bulb, tr=max(Y1), v=wind_speed, rh=humidity))
##
##print("Tmrt : {}°C\nutci : {}°C".format(round(max(Y1),1),max(Y2)))
##plt.plot(X, Y1)
##plt.title("Tmrt")
###plt.figure()
##plt.plot(X,Y2)
##plt.title("utci")
##plt.figure()
##plt.plot(X3,Y3)
##plt.title("wind_utci")
##plt.show()


