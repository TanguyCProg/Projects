from Tmrt import MRT
import matplotlib.pyplot as plt
import numpy as np
from pythermalcomfort.models import solar_gain, at, humidex

def clo_to_R(clo):
    return clo * 0.155/S

def hc(ts, ta, v):
    if v < 0.25:
        h = np.sign(ts-ta)*2.38 * np.abs((ts - ta))**0.25
    if v <= 1:
        h =  3.5 + 5.2 * v
    if v > 1:
        h = 8.7 * v**0.6
    return h

    
### VARIABLES ###
Ts = 32.0 # Température de surface
Tint = 37 # Température du corps
Ta = 22 # Température de l'air
S = 1.8 #m²
#https://fr.wikipedia.org/wiki/Isolation_vestimentaire
clo = 0.4 # Caractérise la couche de vêtement
v = 0 #m/s vitesse du vent
h = hc(Ts, Ta, v) # Coeff conducto convection (caractérise le vent)
x_body = 0.3 # Fraction of the possible body surface exposed to sun, ranges from 0 to 1
x_sky = 0.8 # Fraction of sky-vault view fraction exposed to body, ranges from 0 to 1
position = "standing" #'standing', 'supine' or 'seated'

Sol_rad = 0 #W/m² Radiation solaire 200 à 1000
sun_alt = 0 #Altitude du soleil
sun_az = 0 #Azimuth du soleil
view_angle = 5 # Angle à partir duquel le soleil nous voit (ie augmente si il y a un mur à côté)
T_dew = 12.93 #Température du point de rosée (°C)
Cloudiness = 8 #Taux de nuage (10 = clair, 0 = nuageux)
### VARIBLES ###

### CONSTANTES ###
#Rajouter k après température siignifie quelle est en Kelvin
Tsk = Ts + 273.15
Tak = Ta + 273.15
Tintk = Tint + 273.15
Hvap = 44500 #J/mol Enthalpie d'évaporation de l'eau
Psueur =1.1*10**-5# 5.79*10**-6 #L/s Débit de sueur Maxi = 1.1*10**-4
Meau = 0.018 #kg/mol Masse molaire de l'eau
peau = 1 # densité de l'eau
sigma = 5.67 * 10**-8 # Constante de Boltzman
eps = 0.98 #absorption du rayonnement du corps humain
if v < 0.2:
    A = 0.5
elif v <= 0.6:
    A = 0.6
elif v <= 1:
    A = 0.7
else:
    A = 0.7

#lambda = lambda de la conduction thermique
lambda_epiderme = 0.24 
lambda_derme = 0.45
lambda_hypoderme = 0.69
#e = épaisseur des différentes couches de la peau
e_epiderme = 0.00008
e_derme = 0.002
e_hypoderme = 0.004
#R = résistances thermiques pour une surface de 1,8 m²
R_cond_conv = 1/(h*S)
R_epiderme = e_epiderme/(lambda_epiderme * S)
R_derme = e_derme/(lambda_derme * S)
R_hypoderme = e_hypoderme/(lambda_hypoderme * S)
R_vet = clo_to_R(clo)
R_tot = R_epiderme * R_derme * R_hypoderme / (R_epiderme * R_derme + R_derme * R_hypoderme + R_epiderme * R_hypoderme)
R_tot = R_cond_conv + R_vet + R_epiderme + R_derme + R_hypoderme
tmrt = MRT(Sol_rad, sun_alt,view_angle, sun_az, T_dew, Cloudiness, Ta) #Température moyenne de radiation
### CONSTANTES ###

###ANNEXES###
#hr = sigma * eps * 0.6 * ((Tsk**4) - (tmrt + 273.15)**4)/(Tsk - (tmrt + 273.15))
#hr = 5.5
#Fcl = 1/((h + hr)*clo + 1/(1+1.97*clo))



#Flux_soleil = sigma * ?eps? * ( (( tmrtk**4 ) - ( Tsk ** 4 )) )

### CALCULS ###
Ray = sigma * eps * ( ( Tsk**4 ) - ( Tak ** 4 ) ) * S #Rayonnement infrarouge émis par le corps
Sol = -( A*Ta + (1 - A)*tmrt ) / 2 #Rayonnement du soleil reçu par le corps
Sol = -solar_gain(sol_altitude = 90, #0 = down, 90 = up (°)
                 sharp = 0, #Sun azimuth 0 (front) to 180 (back) (°)
                 sol_radiation_dir = Sol_rad,
                 sol_transmittance = 1, # 1 outside
                 f_svv = x_sky, 
                 f_bes = x_body,
                 posture= position,
                 floor_reflectance=0.4,
                 )['erf']
Cond = (Ts - Ta)/ R_tot
Evap = (Hvap * Psueur * peau/Meau) #Evaporation
Flux = Ray + Sol + Cond + Evap #Flux total (compté sortant positif)
Flux_2 = Ray + Cond + Evap # Flux sortant uniquement
### CALCULS ###
##plt.plot(Ta,Flux,color='blue')
##plt.plot(Ta, Ray, color = 'green')
##plt.plot(Ta, Sol, color = 'red')
##plt.plot(Ta, Cond, color = 'cyan')
##plt.plot(Ta, Evap, color = 'magenta')
##plt.show()
print("Rayonnement infrarouge :",round(Ray,1),"W")
print("Rayonnement solaire :",round(Sol,1),"W")
print("Conducto-Convection :",round(Cond,1),"W")
print("Evaporation :",round(Evap,1),"W")
print("\nFlux sortant total :",round(Flux,1),"W\n\n")

print("Rayonnement :",round(100*(Ray)/Flux_2,1),"%")
print("Conducto-Convection :",round(100*Cond/Flux_2,1),"%")
print("Evaporation :",round(100*Evap/Flux_2,1),"%")



### TEMPERATURE RESSENTIE ###

h = hc(Ts,Ta,0)
Psueur = 1.1*10**-5
clo = 0.4


R_cond_conv = 1/(h*S)
R_epiderme = e_epiderme/(lambda_epiderme * S)
R_derme = e_derme/(lambda_derme * S)
R_hypoderme = e_hypoderme/(lambda_hypoderme * S)
R_vet = clo_to_R(clo)
R_tot = R_cond_conv + R_vet + R_epiderme + R_derme + R_hypoderme


Ray = sigma * eps * ( ( Tsk**4 ) - ( Tak ** 4 ) ) * S
Cond = (Ts - Ta)/ R_tot
Evap = (Hvap * Psueur * peau/Meau)

res = (-Flux + Evap + (Tsk / R_tot) + sigma * eps * (Tsk ** 4)  *S) / (sigma * eps * S)
Takx = np.linspace(-100,100,2012) + 273

eq = (Takx**4) + Takx/(R_tot*sigma*eps*S)
mini = np.min(np.abs(eq - res))
indice = np.where(np.abs(eq -res) == mini)
Tr = Takx[indice] -273

print("\n\nTempérature ressentie :",round(Tr[0],1),"°C")

print(at(Ta, 60, v))
