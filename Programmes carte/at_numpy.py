import math
import numpy as np

c_to_k = 273.15
cp_vapour = 1805.0
cp_water = 4186
cp_air = 1004
h_fg = 2501000
r_air = 287.055



def p_sat(tdb):
    """Calculates vapour pressure of water at different temperatures

    Parameters
    ----------
    tdb: float
        air temperature, [°C]

    Returns
    -------
    p_sat: float
        operative temperature, [Pa]
    """

    ta_k = tdb + c_to_k
    c1 = -5674.5359
    c2 = 6.3925247
    c3 = -0.9677843 * math.pow(10, -2)
    c4 = 0.62215701 * math.pow(10, -6)
    c5 = 0.20747825 * math.pow(10, -8)
    c6 = -0.9484024 * math.pow(10, -12)
    c7 = 4.1635019
    c8 = -5800.2206
    c9 = 1.3914993
    c10 = -0.048640239
    c11 = 0.41764768 * math.pow(10, -4)
    c12 = -0.14452093 * math.pow(10, -7)
    c13 = 6.5459673
    R1 = np.exp(
        c1 / ta_k
        + c2
        + ta_k * (c3 + ta_k * (c4 + ta_k * (c5 + c6 * ta_k)))
        + c7 * np.log(ta_k)
    )

    R2 = np.exp(
        c8 / ta_k
        + c9
        + ta_k * (c10 + ta_k * (c11 + ta_k * c12))
        + c13 * np.log(ta_k)
    )
    
    pascals = np.where(ta_k < c_to_k, R1, R2)


    return np.round(pascals, 1)


def t_dp(tdb, rh):
    """Calculates the dew point temperature.

    Parameters
    ----------
    tdb: float
        dry bulb air temperature, [°C]
    rh: float
        relative humidity, [%]

    Returns
    -------
    t_dp: float
        dew point temperature, [°C]
    """

    c = 257.14
    b = 18.678
    d = 234.5

    gamma_m = np.log(rh / 100 * np.exp((b - tdb / d) * (tdb / (c + tdb))))

    return np.round(c * gamma_m / (b - gamma_m), 1)


def t_wb(tdb, rh):
    """Calculates the wet-bulb temperature using the Stull equation [6]_

    Parameters
    ----------
    tdb: float
        air temperature, [°C]
    rh: float
        relative humidity, [%]

    Returns
    -------
    tdb: float
        wet-bulb temperature, [°C]
    """
    twb = np.round(
        tdb * np.arctan(0.151977 * (rh + 8.313659) ** (1 / 2))
        + np.arctan(tdb + rh)
        - np.arctan(rh - 1.676331)
        + 0.00391838 * rh ** (3 / 2) * np.arctan(0.023101 * rh)
        - 4.686035,
        1,
    )
    return twb


def enthalpy(tdb, hr):
    """Calculates air enthalpy

    Parameters
    ----------
    tdb: float
        air temperature, [°C]
    hr: float
        humidity ratio, [kg water/kg dry air]

    Returns
    -------
    enthalpy: float
        enthalpy [J/kg dry air]
    """

    h_dry_air = cp_air * tdb
    h_sat_vap = h_fg + cp_vapour * tdb
    h = h_dry_air + hr * h_sat_vap

    return np.round(h, 2)



def psy_ta_rh(tdb, rh, patm=101325):
    """Calculates psychrometric values of air based on dry bulb air temperature and
    relative humidity.
    For more accurate results we recommend the use of the the Python package
    `psychrolib`_.

    .. _psychrolib: https://pypi.org/project/PsychroLib/

    Parameters
    ----------
    tdb: float
        air temperature, [°C]
    rh: float
        relative humidity, [%]
    patm: float
        atmospheric pressure, [Pa]

    Returns
    -------
    p_vap: float
        partial pressure of water vapor in moist air, [Pa]
    hr: float
        humidity ratio, [kg water/kg dry air]
    t_wb: float
        wet bulb temperature, [°C]
    t_dp: float
        dew point temperature, [°C]
    h: float
        enthalpy [J/kg dry air]
    """
    p_saturation = p_sat(tdb)
    p_vap = rh / 100 * p_saturation
    hr = 0.62198 * p_vap / (patm - p_vap)
    tdp = t_dp(tdb, rh)
    twb = t_wb(tdb, rh)
    h = enthalpy(tdb, hr)

    return {
        "p_sat": p_saturation,
        "p_vap": p_vap,
        "hr": hr,
        "t_wb": twb,
        "t_dp": tdp,
        "h": h,
    }



def at_np(tdb, rh, v, q=None, **kwargs):
    """
    Calculates the Apparent Temperature (AT). The AT is defined as the temperature at the
    reference humidity level producing the same amount of discomfort as that experienced
    under the current ambient temperature, humidity, and solar radiation [17]_. In other
    words, the AT is an adjustment to the dry bulb temperature based on the relative
    humidity value. Absolute humidity with a dew point of 14°C is chosen as a
    reference [16]_. It includes the chilling effect of the wind at lower temperatures.

    Two formulas for AT are in use by the Australian Bureau of Meteorology: one includes
    solar radiation and the other one does not (http://www.bom.gov.au/info/thermal_stress/
    , 29 Sep 2021). Please specify q if you want to estimate AT with solar load.

    Parameters
    ----------
    tdb : float
        dry bulb air temperature,[°C]
    rh : float
        relative humidity, [%]
    v : float
        wind speed 10m above ground level, [m/s]
    q : float
        Net radiation absorbed per unit area of body surface [W/m2]

    Other Parameters
    ----------------
    round: boolean, default True
        if True rounds output value, if False it does not round it

    Returns
    -------
    at: float
        apparent temperature, [°C]

    Examples
    --------
    .. code-block:: python

        >>> from pythermalcomfort.models import at
        >>> at(tdb=25, rh=30, v=0.1)
        24.1
    """
    default_kwargs = {
        "round": True,
    }
    kwargs = {**default_kwargs, **kwargs}

    # dividing it by 100 since the at eq. requires p_vap to be in hPa
    p_vap = psy_ta_rh(tdb, rh)["p_vap"] / 100

    # equation sources [16] and http://www.bom.gov.au/info/thermal_stress/#apparent
    if q:
        t_at = tdb + 0.348 * p_vap - 0.7 * v + 0.7 * q / (v + 10) - 4.25
    else:
        t_at = tdb + 0.33 * p_vap - 0.7 * v - 4.00

    if kwargs["round"]:
        t_at = np.round(t_at, 1)

    return t_at
