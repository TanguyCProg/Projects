from math import exp
from Tmrt import MRT


def f_Qsw(Beta, Icl, hc, Tbarre_r, mswb):
    res = ((0.675*Beta) / (1 + 0.155 * Icl * (4.6 + 0.046 * Tbarre_r))) * mswb + 0.42 * ( (M - W) - 58.15)
    return res

def f_mswb(Eet_req, Eet_max):
    res = 36.75 + 0.3818 * Eet_req - Eet_max
    return res

def f_Eet_req(fcl, hc, Tet_cl, Ta, Tbarre_r):
    res = 232.6 - fcl * hc * (Tet_cl - Ta) - 3.96 * (10**-8) * fcl * ( (Tet_cl + 273)**4 - (Tbarre_r + 273)**4)
    return res

def f_Tet_cl(Pv, Ta):
    res = 29.187 - Icl * (11.447 + 0.0011 * Pv + 0.0504 * Ta)
    return Ta

def f_Eet_max(Icl, hcl, Pv):
    res = (16.7 + 0.371 * Icl * (hcl**2)) * (4.13 - 0.001 * Pv)
    return res

def f_Beta(mswb):
    if 200 <= mswb:
        res = 1
    elif 150 < mswb < 200:
        res = 0.5
    elif 0 <= mswb < 150:
        res = 0.333
    return res

def f_Pv(RH, Ta):
    res = 1000 * RH * exp(18.6686 - (4030.183 / (Ta + 235)))
    return res

def f_hcl(Icl):
    res = 6.45 / Icl
    return res

def f_fcl(Icl):
    if 0.5 <= Icl:
        res = 1.05 + 0.1 * Icl
    elif Icl < 0.5:
        res = 1 + 0.2 * Icl
    return res

def f_hc(hcfree, hcforced):
    res = max(hcfree, hcforced)
    return res

def f_hcfree(Tcl, Ta):
    res = 2.38 * (Tcl - Ta)**0.25
    return res

def f_hcforced(Va):
    res = 12.1 * (Va**0.5)
    return res

def f_Tcl(M, W, calc, Icl):
    res = 35.7 - 0.028 * (M - W) - 0.155 * calc * Icl
    print(res)
    return res

def f_calc(M,W, Pv, Ta):
    s1 = M - W
    s2 = - 3.05 * (10**-3) * (5733 - 6.99 * (M - W) - Pv)
    s3 = - 0.42 * ( (M - W) - 58.15)
    s4 = - 1.7 * (10**-5) * M * (5867 - Pv)
    s5 = - 0.0014 * M * (34 - Ta)
    res =  s1 + s2 + s3 + s4 + s5
    print(s1, s2, s3, s4, s5)
    print(res)
    print(Pv)
    return res


Solar_radiation = 800
sun_altitude = 10
view_angle = 10
sun_azimuth = 20
Temp_dew_point = 4
Cloudiness = 8


RH = 50 # Humidité relative
Ta = 21 # Température ambiante (°C)
M = 58.15 # Metabolic rate, 1 met = 58.15 W/m² (W/m²)
#Icl Thermal resistance of clothing
W = 0 #External work
Tbarre_r = MRT(Solar_radiation, sun_altitude, view_angle,
               sun_azimuth, Temp_dew_point, Cloudiness, Ta) # Température moyenne radiative
Va = 0.2 # Vitesse de l'air (m/s)
Icl = 0.56# 0 m² - K/W to 0.310 m² - K/W (0 clo to 2 clo)

Pv = f_Pv(RH, Ta)
Pv = 1200
calc = f_calc(M, W, Pv, Ta) # 0 m² - K/W to 0.310 m² - K/W (0 clo to 2 clo)
Tcl = f_Tcl(M, W, calc, Icl)
hcforced = f_hcforced(Va)
hcfree = f_hcfree(Tcl, Ta)
hc = f_hc(hcfree, hcforced)
fcl = f_fcl(Icl)
hcl = f_hcl(Icl)
Tet_cl = f_Tet_cl(Pv, Ta)
Eet_max = f_Eet_max(Icl, hcl, Pv)
Eet_req = f_Eet_req(fcl, hc, Tet_cl, Ta, Tbarre_r)
mswb = f_mswb(Eet_req, Eet_max)
Beta = f_Beta(mswb)
Qsw = f_Qsw(Beta, Icl, hc, Tbarre_r, mswb)

print(Qsw)



