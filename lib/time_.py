"""
各種時刻換算用ライブラリ
"""
import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import const as lcst


def gc2jd(gc):
    """ ユリウス日の計算

    :param  datetime gc: グレゴリオ暦
    :return float    jd: ユリウス日
    """
    year, month,  day    = gc.year, gc.month,  gc.day
    hour, minute, second = gc.hour, gc.minute, gc.second
    second += gc.microsecond * 1e-6
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

def jd2gc(jd):
    """ ユリウス日 -> グレゴリオ暦

    :param float jd
    :return list ut: [year, month, day, hour, minute, second]
    """
    ut = [0 for _ in range(6)]
    try:
        jd -= 0.125
        x0 = int(jd + 68570)
        x1 = x0 // 36524.25
        x2 = x0 - int(36524.25 * x1 + 0.75)
        x3 = (x2 + 1) // 365.2425
        x4 = x2 - int(365.25 * x3) + 31
        x5 = int(x4) // 30.59
        x6 = int(x5) // 11.0
        ut[2] = x4 - int(30.59 * x5)
        ut[1] = x5 - 12 * x6 + 2
        ut[0] = 100 * (x1 - 49) + x3 + x6
        # 2月30日の補正
        if ut[1] == 2 and ut[2] > 28:
            if ut[0] % 100 == 0 and ut[0] % 400 == 0:
                ut[2] = 29
            elif ut[0] % 4 == 0:
                ut[2] = 29
            else:
                ut[2] = 28
        tm = 86400 * (jd - int(jd))
        ut[3] = tm // 3600.0
        ut[4] = (tm - 3600 * ut[3]) // 60.0
        ut[5] = tm - 3600 * ut[3] - 60 * ut[4]
        return list(map(lambda x: int(x), ut))
    except Exception as e:
        raise

def jd2jc(jd):
    """ ユリウス世紀数の計算

    :param  float jd: ユリウス日
    :return float  t: ユリウス世紀数
    """
    try:
        return (jd - lcst.J2000) / lcst.JC
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
        for date, sec in reversed(lcst.LEAP_SEC):
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
        for date, sec in reversed(lcst.DUT1):
            if date <= target:
                dut1 = sec
                break
        return dut1
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
        return tai + datetime.timedelta(seconds=lcst.TT_TAI)
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
        s = lcst.L_G * (jd - lcst.T_0) * lcst.DAYSEC
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
        s = lcst.L_B * (jd - lcst.T_0) * lcst.DAYSEC
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
        s = lcst.L_B * (jd_tcb - lcst.T_0) * lcst.DAYSEC - lcst.TDB_0
        return tcb - datetime.timedelta(seconds=s)
    except Exception as e:
        raise

