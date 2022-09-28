import sys
import numpy as np
lien = r"C:\Users\Tanguy Chatelain\AppData\Local\Programs\Python\Python39\Lib\site-packages\pythermalcomfort"
sys.path.append(lien)
from optimized_functions import utci_optimized


def utci_np(tdb, tr, v, rh):
    """Determines the Universal Thermal Climate Index (UTCI). The UTCI is the
    equivalent temperature for the environment derived from a reference environment.
    It is defined as the air temperature of the reference environment which produces
    the same strain index value in comparison with the reference individual's response
    to the real
    environment. It is regarded as one of the most comprehensive indices for
    calculating heat stress in outdoor spaces. The parameters that are taken into
    account for calculating
    UTCI involve dry bulb temperature, mean radiation temperature, the pressure of
    water vapor or relative humidity, and wind speed (at the elevation of 10 m above the
    ground) [7]_.

    Parameters
    ----------
    tdb : float
        dry bulb air temperature, default in [°C] in [°F] if `units` = 'IP'
    tr : float
        mean radiant temperature, default in [°C] in [°F] if `units` = 'IP'
    v : float
        wind speed 10m above ground level, default in [m/s] in [fps] if `units` = 'IP'
    rh : float
        relative humidity, [%]

    Returns
    -------
    utci : float
         Universal Thermal Climate Index, [°C] or in [°F]

    Notes
    -----
    You can use this function to calculate the Universal Thermal Climate Index (`UTCI`)
    The applicability wind speed value must be between 0.5 and 17 m/s.

    .. _UTCI: http://www.utci.org/utcineu/utcineu.php

    Examples
    --------
    .. code-block:: python

        >>> from pythermalcomfort.models import utci
        >>> utci(tdb=25, tr=25, v=1.0, rh=50)
        24.6

    Raises
    ------
    ValueError
        Raised if the input are outside the Standard's applicability limits

    """



    def exponential(t_db):
        g = [
            -2836.5744,
            -6028.076559,
            19.54263612,
            -0.02737830188,
            0.000016261698,
            (7.0229056 * (10 ** (-10))),
            (-1.8680009 * (10 ** (-13))),
        ]
        tk = t_db + 273.15  # air temp in K
        es = 2.7150305 * np.log1p(tk)
        for count, i in enumerate(g):
            es = es + (i * (tk ** (count - 2)))
        es = np.exp(es) * 0.01  # convert Pa to hPa
        return es

    eh_pa = exponential(tdb) * (rh / 100.0)
    delta_t_tr = tr - tdb
    pa = eh_pa / 10.0  # convert vapour pressure to kPa

    utci_approx = utci_optimized(tdb, v, delta_t_tr, pa)

    return np.round(utci_approx, 1)


