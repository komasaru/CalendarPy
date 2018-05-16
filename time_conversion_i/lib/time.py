"""
各種時刻換算用ライブラリ
"""
import datetime


# Constants
J2000   = 2451545          # Reference epoch (J2000.0), Julian Date
JC      = 36525            # Days per Julian century
DAYSEC  = 86400            # Seconds per a day
TT_TAI  = 32.184           # TT - TAI
L_G     = 6.969290134e-10  # for TCG
L_B     = 1.550519768e-8   # for TCB, TDB
T_0     = 2443144.5003725  # for TCG, TDB, TCB
TDB_0   = -6.55e-5         # for TDB
LEAP_SEC = [
    ["19720101", -10],
    ["19720701", -11],
    ["19730101", -12],
    ["19740101", -13],
    ["19750101", -14],
    ["19760101", -15],
    ["19770101", -16],
    ["19780101", -17],
    ["19790101", -18],
    ["19800101", -19],
    ["19810701", -20],
    ["19820701", -21],
    ["19830701", -22],
    ["19850701", -23],
    ["19880101", -24],
    ["19900101", -25],
    ["19910101", -26],
    ["19920701", -27],
    ["19930701", -28],
    ["19940701", -29],
    ["19960101", -30],
    ["19970701", -31],
    ["19990101", -32],
    ["20060101", -33],
    ["20090101", -34],
    ["20120701", -35],
    ["20150701", -36],
    ["20170101", -37],
    ["20190101",   0]  # (<= Provisional end-point)
]
DUT1 = [
    ["19880317",  0.2],
    ["19880512",  0.1],
    ["19880825",  0.0],
    ["19881110", -0.1],
    ["19890119", -0.2],
    ["19890406", -0.3],
    ["19890608", -0.4],
    ["19890921", -0.5],
    ["19891116", -0.6],
    ["19900101",  0.3],
    ["19900301",  0.2],
    ["19900412",  0.1],
    ["19900510",  0.0],
    ["19900726", -0.1],
    ["19900920", -0.2],
    ["19901101", -0.3],
    ["19910101",  0.6],
    ["19910207",  0.5],
    ["19910321",  0.4],
    ["19910425",  0.3],
    ["19910620",  0.2],
    ["19910822",  0.1],
    ["19911017",  0.0],
    ["19911121", -0.1],
    ["19920123", -0.2],
    ["19920227", -0.3],
    ["19920402", -0.4],
    ["19920507", -0.5],
    ["19920701",  0.4],
    ["19920903",  0.3],
    ["19921022",  0.2],
    ["19921126",  0.1],
    ["19930114",  0.0],
    ["19930218", -0.1],
    ["19930401", -0.2],
    ["19930506", -0.3],
    ["19930701",  0.6],
    ["19930819",  0.5],
    ["19931007",  0.4],
    ["19931118",  0.3],
    ["19931230",  0.2],
    ["19940210",  0.1],
    ["19940317",  0.0],
    ["19940421", -0.1],
    ["19940609", -0.2],
    ["19940701",  0.8],
    ["19940811",  0.7],
    ["19941006",  0.6],
    ["19941117",  0.5],
    ["19941222",  0.4],
    ["19950223",  0.3],
    ["19950316",  0.2],
    ["19950413",  0.1],
    ["19950525",  0.0],
    ["19950713", -0.1],
    ["19950907", -0.2],
    ["19951026", -0.3],
    ["19951130", -0.4],
    ["19960101",  0.5],
    ["19960222",  0.4],
    ["19960411",  0.3],
    ["19960516",  0.2],
    ["19960808",  0.1],
    ["19961003",  0.0],
    ["19961205", -0.1],
    ["19970206", -0.2],
    ["19970320", -0.3],
    ["19970508", -0.4],
    ["19970626", -0.5],
    ["19970701",  0.5],
    ["19970918",  0.4],
    ["19971030",  0.3],
    ["19971218",  0.2],
    ["19980219",  0.1],
    ["19980326",  0.0],
    ["19980507", -0.1],
    ["19980813", -0.2],
    ["19981126", -0.3],
    ["19990101",  0.7],
    ["19990304",  0.6],
    ["19990527",  0.5],
    ["19991014",  0.4],
    ["20000106",  0.3],
    ["20000413",  0.2],
    ["20001019",  0.1],
    ["20010301",  0.0],
    ["20011004", -0.1],
    ["20020214", -0.2],
    ["20021024", -0.3],
    ["20030403", -0.4],
    ["20040429", -0.5],
    ["20050317", -0.6],
    ["20060101",  0.3],
    ["20060427",  0.2],
    ["20060928",  0.1],
    ["20061222",  0.0],
    ["20070315", -0.1],
    ["20070614", -0.2],
    ["20071129", -0.3],
    ["20080313", -0.4],
    ["20080807", -0.5],
    ["20081120", -0.6],
    ["20090101",  0.4],
    ["20090312",  0.3],
    ["20090611",  0.2],
    ["20091112",  0.1],
    ["20100311",  0.0],
    ["20100603", -0.1],
    ["20110106", -0.2],
    ["20110512", -0.3],
    ["20111104", -0.4],
    ["20120209", -0.5],
    ["20120510", -0.6],
    ["20120701",  0.4],
    ["20121025",  0.3],
    ["20130131",  0.2],
    ["20130411",  0.1],
    ["20130822",  0.0],
    ["20131121", -0.1],
    ["20140220", -0.2],
    ["20140508", -0.3],
    ["20140925", -0.4],
    ["20141225", -0.5],
    ["20150319", -0.6],
    ["20150528", -0.7],
    ["20150701",  0.3],
    ["20150917",  0.2],
    ["20151126",  0.1],
    ["20160131",  0.0],
    ["20160324", -0.1],
    ["20160519", -0.2],
    ["20160901", -0.3],
    ["20161117", -0.4],
    ["20170101",  0.6],
    ["20170126",  0.5],
    ["20170330",  0.4],
    ["20170629",  0.3],
    ["20171130",  0.2],
    ["20180315",  0.1],
    ["20180615",  0.0]  # (<= Provisional end-point)
]


def gc2jd(gc):
    """ ユリウス日の計算

    :param  datetime gc: グレゴリオ暦
    :return float    jd: ユリウス日
    """
    year, month,  day    = gc.year, gc.month,  gc.day
    hour, minute, second = gc.hour, gc.minute, gc.second
    try:
        if month < 3:
            year  -= 1
            month += 12
        d = int(365.25 * year) + year // 400  - year // 100 \
          + int(30.59 * (month - 2)) + day + 1721088.5
        t  = (second / 3600 + minute / 60 + hour) / 24
        return d + t
    except Exception as e:
        raise

def jd2t(jd):
    """ ユリウス世紀数の計算

    :param  float jd: ユリウス日
    :return float  t: ユリウス世紀数
    """
    try:
        return (jd - J2000) / JC
    except Exception as e:
        raise

def utc2utc_tai(utc):
    """ UTC - TAI (協定世界時と国際原子時の差 = うるう秒の総和)

    :param  datetime  utc: 協定世界時
    :return float utc_tai: 協定世界時と国際原子時の差(うるう秒の総和)
                           (Unit: seconds)
    """
    utc_tai = 0
    target = utc.strftime("%Y%m%d")
    try:
        for date, sec in reversed(LEAP_SEC):
            if date <= target:
                utc_tai = sec
                break
        return utc_tai
    except Exception as e:
        raise

def utc2dut1(utc):
    """ DUT1 (= UT1(世界時1) - UTC(協定世界時)) の取得
        * Ref: http://jjy.nict.go.jp/QandA/data/dut1.html

    :param  datetime utc: 協定世界時
    :return float   dut1: DUT1 (Unit: seconds)
    """
    dut1 = 0
    target = utc.strftime("%Y%m%d")
    try:
        for date, sec in reversed(DUT1):
            if date <= target:
                dut1 = sec
                break
        return dut1
    except Exception as e:
        raise

def utc2dt(utc):
    """ UTC -> ΔT
        * うるう秒調整が明確な場合は、うるう秒総和を使用した計算
        * そうでない場合は、NASA の計算式による計算

    :param  datetime utc: 協定世界時
    :return float     dt: ΔT (Unit: seconds)
    """
    try:
        if                        utc.year <  -500:
            dt = __dt_before_m500(utc)
        elif -500 <= utc.year and utc.year <   500:
            dt = __dt_before_500(utc)
        elif  500 <= utc.year and utc.year <  1600:
            dt = __dt_before_1600(utc)
        elif 1600 <= utc.year and utc.year <  1700:
            dt = __dt_before_1700(utc)
        elif 1700 <= utc.year and utc.year <  1800:
            dt = __dt_before_1800(utc)
        elif 1800 <= utc.year and utc.year <  1860:
            dt = __dt_before_1860(utc)
        elif 1860 <= utc.year and utc.year <  1900:
            dt = __dt_before_1900(utc)
        elif 1900 <= utc.year and utc.year <  1920:
            dt = __dt_before_1920(utc)
        elif 1920 <= utc.year and utc.year <  1941:
            dt = __dt_before_1941(utc)
        elif 1941 <= utc.year and utc.year <  1961:
            dt = __dt_before_1961(utc)
        elif 1961 <= utc.year and utc.year <  1986:
            dt = __dt_before_1986(utc)
        elif 1986 <= utc.year and utc.year <  2005:
            dt = __dt_before_2005(utc)
        elif 2005 <= utc.year and utc.year <  2050:
            dt = __dt_before_2050(utc)
        elif 2050 <= utc.year and utc.year <= 2150:
            dt = __dt_until_2150(utc)
        elif 2150 <  utc.year:
            dt = __dt_after_2150(utc)
        return dt
    except Exception as e:
        raise

def __dt_before_m500(utc):
    """ year < -500    dt: ΔT

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = (y - 1820) / 100
    try:
        return -20 + 32 * t ** 2
    except Exception as e:
        raise

def __dt_before_500(utc):
    """ -500 <= year and year < 500

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y / 100
    try:
        return 10583.6           \
            + (-1014.41          \
            + (   33.78311       \
            + (   -5.952053      \
            + (   -0.1798452     \
            + (    0.022174192   \
            + (    0.0090316521) \
            * t) * t) * t) * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1600(utc):
    """ 500 <= year and year < 1600

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = (y - 1000) / 100
    try:
        return 1574.2           \
            + (-556.01          \
            + (  71.23472       \
            + (   0.319781      \
            + (  -0.8503463     \
            + (  -0.005050998   \
            + (   0.0083572073) \
            * t) * t) * t) * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1700(utc):
    """ 1600 <= year and year < 1700

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1600
    try:
        return 120           \
            + ( -0.9808      \
            + ( -0.01532     \
            + (  1.0 / 7129) \
            * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1800(utc):
    """ 1700 <= year and year < 1800

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1700
    try:
        return 8.83           \
           + ( 0.1603         \
           + (-0.0059285      \
           + ( 0.00013336     \
           + (-1.0 / 1174000) \
           * t) * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1860(utc):
    """ 1800 <= year and year < 1860

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1800
    try:
        return 13.72            \
            + (-0.332447        \
            + ( 0.0068612       \
            + ( 0.0041116       \
            + (-0.00037436      \
            + ( 0.0000121272    \
            + (-0.0000001699    \
            + ( 0.000000000875) \
            * t) * t) * t) * t) * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1900(utc):
    """ 1860 <= year and year < 1900

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1860
    try:
        return 7.62          \
           + ( 0.5737        \
           + (-0.251754      \
           + ( 0.01680668    \
           + (-0.0004473624  \
           + ( 1.0 / 233174) \
           * t) * t) * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1920(utc):
    """ 1900 <= year and year < 1920

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1900
    try:
        return -2.79      \
            + ( 1.494119  \
            + (-0.0598939 \
            + ( 0.0061966 \
            + (-0.000197) \
            * t) * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1941(utc):
    """ 1920 <= year and year < 1941

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1920
    try:
        return 21.20       \
            + ( 0.84493    \
            + (-0.076100   \
            + ( 0.0020936) \
            * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1961(utc):
    """ 1941 <= year and year < 1961

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1950
    try:
        return 29.07        \
            + ( 0.407       \
            + (-1.0 / 233   \
            + ( 1.0 / 2547) \
            * t) * t) * t
    except Exception as e:
        raise

def __dt_before_1986(utc):
    """ 1961 <= year and year < 1986

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 1975
    try:
        if utc < datetime.datetime(1972, 1, 1):
            # 1972年1月より前は NASA 提供の略算式で
            return 45.45       \
                + ( 1.067      \
                + (-1.0 / 260  \
                + (-1.0 / 718) \
                * t) * t) * t
        elif utc < datetime.datetime(1972, 7, 1):
            return TT_TAI + 10
        elif utc < datetime.datetime(1973, 1, 1):
            return TT_TAI + 11
        elif utc < datetime.datetime(1974, 1, 1):
            return TT_TAI + 12
        elif utc < datetime.datetime(1975, 1, 1):
            return TT_TAI + 13
        elif utc < datetime.datetime(1976, 1, 1):
            return TT_TAI + 14
        elif utc < datetime.datetime(1977, 1, 1):
            return TT_TAI + 15
        elif utc < datetime.datetime(1978, 1, 1):
            return TT_TAI + 16
        elif utc < datetime.datetime(1979, 1, 1):
            return TT_TAI + 17
        elif utc < datetime.datetime(1980, 1, 1):
            return TT_TAI + 18
        elif utc < datetime.datetime(1981, 7, 1):
            return TT_TAI + 19
        elif utc < datetime.datetime(1982, 7, 1):
            return TT_TAI + 20
        elif utc < datetime.datetime(1983, 7, 1):
            return TT_TAI + 21
        elif utc < datetime.datetime(1985, 7, 1):
            return TT_TAI + 22
        elif utc < datetime.datetime(1988, 1, 1):
            return TT_TAI + 23
    except Exception as e:
        raise

def __dt_before_2005(utc):
    """ 1986 <= year and year < 2005

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 2000
    try:
        # 以下の7行は NASA 提供の略算式
        #return 63.86           \
        #    + ( 0.3345         \
        #    + (-0.060374       \
        #    + ( 0.0017275      \
        #    + ( 0.000651814    \
        #    + ( 0.00002373599) \
        #    * t) * t) * t) * t) * t
        if utc < datetime.datetime(1988, 1, 1):
            return TT_TAI + 23
        elif utc < datetime.datetime(1990, 1, 1):
            return TT_TAI + 24
        elif utc < datetime.datetime(1991, 1, 1):
            return TT_TAI + 25
        elif utc < datetime.datetime(1992, 7, 1):
            return TT_TAI + 26
        elif utc < datetime.datetime(1993, 7, 1):
            return TT_TAI + 27
        elif utc < datetime.datetime(1994, 7, 1):
            return TT_TAI + 28
        elif utc < datetime.datetime(1996, 1, 1):
            return TT_TAI + 29
        elif utc < datetime.datetime(1997, 7, 1):
            return TT_TAI + 30
        elif utc < datetime.datetime(1999, 1, 1):
            return TT_TAI + 31
        elif utc < datetime.datetime(2006, 1, 1):
            return TT_TAI + 32
    except Exception as e:
        raise

def __dt_before_2050(utc):
    """ 2005 <= year and year < 2050

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = y - 2000
    try:
        if utc < datetime.datetime(2006, 1, 1):
            return TT_TAI + 32
        elif utc < datetime.datetime(2009, 1, 1):
            return TT_TAI + 33
        elif utc < datetime.datetime(2012, 7, 1):
            return TT_TAI + 34
        elif utc < datetime.datetime(2015, 7, 1):
            return TT_TAI + 35
        elif utc < datetime.datetime(2017, 1, 1):
            return TT_TAI + 36
        elif utc < datetime.datetime(2019, 1, 1):
            # 第28回うるう秒実施までの暫定措置
            return TT_TAI + 37
        else:
            # 2019年1月以降は NASA 提供の略算式で
            return 62.92      \
                + ( 0.32217   \
                + ( 0.005589) \
                * t) * t
    except Exception as e:
        raise

def __dt_until_2150(utc):
    """ 2050 <= year and year <= 2150

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    try:
        return - 20 \
               + 32 * ((y - 1820) / 100) ** 2 \
               - 0.5628 * (2150 - y)
    except Exception as e:
        raise

def __dt_after_2150(utc):
    """ 2150 < year

    :param datetime utc: 協定世界時
    :return float    dt: ΔT
    """
    y = utc.year + (utc.month - 0.5) / 12
    t = (y - 1820) / 100
    try:
        return -20 + 32 * t ** 2
    except Exception as e:
        raise

def utc2tai(utc, utc_tai):
    """ UTC(協定世界時) -> TAI(国際原子時)
        * TAI = UTC - UTC_TAI

    :param  datetime     utc: 協定世界時
    :param  datetime utc_tai: 協定世界時と国際原子時の差(うるう秒の総和)
    :return datetime     tai: 国際原子時
    """
    try:
        return utc - datetime.timedelta(seconds=utc_tai)
    except Exception as e:
        raise

def utc2ut1(utc, dut1):
    """ UTC(協定世界時) -> UT1(世界時1)
        * UT1 = UTC + DUT1

    :param  datetime  utc: 協定世界時
    :param  datetime dut1: DUT1
    :return datetime  ut1: 世界時1
    """
    try:
        return utc + datetime.timedelta(seconds=dut1)
    except Exception as e:
        raise

def tai2tt(tai):
    """ TAI(協定世界時) -> TT(地球時) 
        * TT = TAI + TT_TAI
             = UT1 + ΔT

    :param  datetime tai: 国際原子時
    :return datetime  tt: 地球時
    """
    try:
        return tai + datetime.timedelta(seconds=TT_TAI)
    except Exception as e:
        raise

def tt2tcg(tt, jd):
    """ TT(地球時) -> TCG(地球重心座標時)
        * TCG = TT + L_G * (JD - T_0) * 86400
          （JD: ユリウス日,
            L_G = 6.969290134 * 10^(-10), T_0 = 2,443,144.5003725）

    :param  datetime  tt: 地球時
    :param  float     jd: ユリウス日
    :return datetime tcg: 地球重心座標時
    """
    try:
        s = L_G * (jd - T_0) * DAYSEC
        return tt + datetime.timedelta(seconds=s)
    except Exception as e:
        raise

def tt2tcb(tt, jd):
    """ TT(地球時) -> TCB(太陽系重心座標時)
        * TCB = TT + L_B * (JD - T_0) * 86400

    :param  datetime  tt: 地球時
    :param  float     jd: ユリウス日
    :return datetime tcb: 太陽系重心座標時
    """
    try:
        s = L_B * (jd - T_0) * DAYSEC
        return tt + datetime.timedelta(seconds=s)
    except Exception as e:
        raise

def tcb2tdb(tcb, jd_tcb):
    """ TCB(太陽系重心座標時) -> TDB(太陽系力学時)
        * TDB = TCB - L_B * (JD_TCB - T_0) * 86400 + TDB_0

    :param  datetime tcb: 太陽系重心座標時
    :param  float jd_tcb: ユリウス日 (for TCB)
    :return datetime tdb: 太陽系力学時
    """
    try:
        s = L_B * (jd_tcb - T_0) * DAYSEC - TDB_0
        return tcb - datetime.timedelta(seconds=s)
    except Exception as e:
        raise

