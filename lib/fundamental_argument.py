"""
Modules for fundamental arguments.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import const as lcst


def l_iers2003(t):
    """ Mean anomaly of the Moon (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Mean anomaly of the Moon
    """
    try:
        return ((    485868.249036    \
              + (1717915923.2178      \
              + (        31.8792      \
              + (         0.051635    \
              + (        -0.00024470) \
              * t) * t) * t) * t) % lcst.TURNAS) * lcst.AS2R
    except Exception as e:
        raise

def lp_mhb2000(t):
    """ Mean anomaly of the Sun (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Mean anomaly of the Sun
    """
    try:
        return ((  1287104.79305     \
              + (129596581.0481      \
              + (       -0.5532      \
              + (        0.000136    \
              + (       -0.00001149) \
              * t) * t) * t) * t) % lcst.TURNAS) * lcst.AS2R
    except Exception as e:
        raise

def f_iers2003(t):
    """ Mean longitude of the Moon minus that of the ascending node
        (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Mean longitude of the Moon minus that of the
                     ascending node
    """
    try:
        return ((     335779.526232   \
              + (1739527262.8478      \
              + (       -12.7512      \
              + (        -0.001037    \
              + (         0.00000417) \
              * t) * t) * t) * t) % lcst.TURNAS) * lcst.AS2R
    except Exception as e:
        raise

def d_mhb2000(t):
    """ Mean elongation of the Moon from the Sun (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Mean elongation of the Moon from the Sun
    """
    try:
        return ((   1072260.70369     \
              + (1602961601.2090      \
              + (        -6.3706      \
              + (         0.006593    \
              + (        -0.00003169) \
              * t) * t) * t) * t) % lcst.TURNAS) * lcst.AS2R
    except Exception as e:
        raise

def om_iers2003(t):
    """ Mean longitude of the ascending node of the Moon
        (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Mean longitude of the ascending node of the
                     Moon
    """
    try:
        return ((    450160.398036    \
              + (  -6962890.5431      \
              + (         7.4722      \
              + (         0.007702    \
              + (        -0.00005939) \
              * t) * t) * t) * t) % lcst.TURNAS) * lcst.AS2R
    except Exception as e:
        raise

def l_mhb2000(t):
    """ Mean anomaly of the Moon (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Mean anomaly of the Moon
    """
    try:
        return (2.35555598 + 8328.6914269554 * t) % lcst.PI2
    except Exception as e:
        raise

def f_mhb2000(t):
    """ Mean longitude of the Moon minus that of the ascending node
        (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Mean longitude of the Moon minus that of the
                     ascending node
    """
    try:
        return (1.627905234 + 8433.466158131 * t) % lcst.PI2
    except Exception as e:
        raise

def d_mhb2000_2(t):
    """ Mean elongation of the Moon from the Sun (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Mean elongation of the Moon from the Sun
    """
    try:
        return (5.198466741 + 7771.3771468121 * t) % lcst.PI2
    except Exception as e:
        raise

def om_mhb2000(t):
    """ Mean longitude of the ascending node of the Moon (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Mean longitude of the ascending node of the
                     Moon
    """
    try:
        return (2.18243920 - 33.757045 * t) % lcst.PI2
    except Exception as e:
        raise

def pa_iers2003(t):
    """ General accumulated precession in longitude (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : General accumulated precession in longitude
    """
    try:
        return (0.024381750 + 0.00000538691 * t) * t
    except Exception as e:
        raise

def lme_iers2003(t):
    """ Mercury longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Mercury longitudes
    """
    try:
        return (4.402608842 + 2608.7903141574 * t) % lcst.PI2
    except Exception as e:
        raise

def lve_iers2003(t):
    """ Venus longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Venus longitudes
    """
    try:
        return (3.176146697 + 1021.3285546211 * t) % lcst.PI2
    except Exception as e:
        raise

def lea_iers2003(t):
    """ Earth longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Earth longitudes
    """
    try:
        return (1.753470314 + 628.3075849991 * t) % lcst.PI2
    except Exception as e:
        raise

def lma_iers2003(t):
    """ Mars longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Mars longitudes
    """
    try:
        return (6.203480913 + 334.0612426700 * t) % lcst.PI2
    except Exception as e:
        raise

def lju_iers2003(t):
    """ Jupiter longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Jupiter longitudes
    """
    try:
        return (0.599546497 + 52.9690962641 * t) % lcst.PI2
    except Exception as e:
        raise

def lsa_iers2003(t):
    """ Saturn longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Saturn longitudes
    """
    try:
        return (0.874016757 + 21.3299104960 * t) % lcst.PI2
    except Exception as e:
        raise

def lur_iers2003(t):
    """ Uranus longitudes (IERS 2003)

    :param  float t: ユリウス世紀数
    :return float  : Uranus longitudes
    """
    try:
        return (5.481293872 + 7.4781598567 * t) % lcst.PI2
    except Exception as e:
        raise

def lne_mhb2000(t):
    """ Neptune longitude (MHB2000)

    :param  float t: ユリウス世紀数
    :return float  : Neptune longitude
    """
    try:
        return (5.321159000 + 3.8127774000 * t) % lcst.PI2
    except Exception as e:
        raise

