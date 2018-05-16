"""
Modules for trigonometrics
"""
import math
import numpy as np


def comp_lambda(alp, dlt, eps):
    """ λ の計算
        * λ = arctan((sinδ sinε + cosδ sinα cosε ) / cosδ cosα)

    :param  float alp: α (Unit: rad)
    :param  float dlt: δ (Unit: rad)
    :param  float eps: ε (Unit: rad)
    :return float lmd: λ (Unit: rad)
    """
    try:
        a = math.sin(dlt) * math.sin(eps) \
          + math.cos(dlt) * math.sin(alp) * math.cos(eps)
        b = math.cos(dlt) * math.cos(alp)
        lmd = math.atan2(a, b)
        if lmd < 0:
            lmd %= math.pi * 2
        return lmd
    except Exception as e:
        raise

def comp_beta(alp, dlt, eps):
    """ β の計算
        * β = arcsisn((sinδ cosε - cosδ sinα sinε)

    :param  float alp: α (unit: rad)
    :param  float dlt: δ (unit: rad)
    :param  float eps: ε (unit: rad)
    :return float bet: β (unit: rad)
    """
    try:
        a = math.sin(dlt) * math.cos(eps) \
          - math.cos(dlt) * math.sin(alp) * math.sin(eps)
        return math.asin(a)
    except Exception as e:
        raise

def comp_alpha(lmd, bet, eps):
    """ α の計算
        * α = arctan((-sinβ sinε + cosβ sinλ cosε ) / cosβ cosλ)

    :param  float lmd: λ (unit: rad)
    :param  float bet: β (unit: rad)
    :param  float eps: ε (unit: rad)
    :return float alp: α (unit: rad)
    """
    try:
        a = -math.sin(bet) * math.sin(eps) \
          +  math.cos(bet) * math.sin(lmd) * math.cos(eps)
        b =  math.cos(bet) * math.cos(lmd)
        alp = math.atan2(a, b)
        if a < 0:
            alp %= math.pi * 2
        return alp
    except Exception as e:
        raise

def comp_delta(lmd, bet, eps):
    """ δ の計算
        * δ = arcsisn((sinβ cosε + cosβ sinλ sinε)

    :param  float lmd: λ (unit: rad)
    :param  float bet: β (unit: rad)
    :param  float eps: ε (unit: rad)
    :return float dlt: δ (unit: rad)
    """
    try:
        a = math.sin(bet) * math.cos(eps) \
          + math.cos(bet) * math.sin(lmd) * math.sin(eps)
        return math.asin(a)
    except Exception as e:
        raise

