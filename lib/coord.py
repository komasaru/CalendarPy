"""
Modules for coordinates
"""
import math
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import matrix        as lmtx
import trigonometric as ltrg


def rect_eq2ec(rect, eps):
    """ 直交座標：赤道座標 -> 黄道座標.

    :param  list rect: 赤道直交座標
    :param  float eps: 黄道傾斜角 (Unit: rad)
    :return list     : 黄道直交座標
    """
    try:
        mtx_rect = np.matrix([rect]).transpose()
        r_mtx = lmtx.r_x(eps)
        return lmtx.rotate(r_mtx, mtx_rect).A1.tolist()
    except Exception as e:
        raise

def rect_ec2eq(rect, eps):
    """ 直交座標：黄道座標 -> 赤道座標.

    :param  list rect: 黄道直交座標
    :param  float eps: 黄道傾斜角 (Unit: rad)
    :return list     : 赤道直交座標
    """
    try:
        mtx_rect = np.matrix([rect]).transpose()
        r_mtx = lmtx.r_x(-eps)
        return lmtx.rotate(r_mtx, mtx_rect).A1.tolist()
    except Exception as e:
        raise

def pol_eq2ec(pol, eps):
    """ 極座標：赤道座標 -> 黄道座標.

    :param  list  pol: 赤道極座標
    :param  float eps: 黄道傾斜角 (Unit: rad)
    :return list     : 黄道極座標 [λ, β]
    """
    try:
        alp, dlt = pol
        lmd = ltrg.comp_lambda(alp, dlt, eps)
        bet = ltrg.comp_beta(alp, dlt, eps)
        return [lmd, bet]
    except Exception as e:
        raise

def pol_ec2eq(pol, eps):
    """ 極座標：赤道座標 -> 黄道座標.

    :param  list  pol: 赤道極座標
    :param  float eps: 黄道傾斜角 (Unit: rad)
    :return list     : 黄道極座標 [α, δ]
    """
    try:
        lmd, bet = pol
        alp = ltrg.comp_alpha(lmd, bet, eps)
        dlt = ltrg.comp_delta(lmd, bet, eps)
        return [alp, dlt]
    except Exception as e:
        raise

def rect2pol(rect):
    """ 直交座標 -> 極座標

    :param  list rect: 直交座標
    :return list     : 極座標 [[λ, φ], 距離]
    """
    try:
        x, y, z = rect
        r = math.sqrt(x * x + y * y)
        lmd = math.atan2(y, x)
        phi = math.atan2(z, r)
        if lmd < 0:
            lmd %= math.pi * 2
        d = math.sqrt(x * x + y * y + z * z)
        return [[lmd, phi], d]
    except Exception as e:
        raise

def pol2rect(pol, r):
    """ 極座標 -> 直交座標

    :param  list pol: 極座標
    :return list    : 直交座標
    """
    try:
        lmd, phi = pol
        r_mtx = lmtx.r_y(phi)
        r_mtx = lmtx.r_z(-lmd, r_mtx)
        return lmtx.rotate(
            r_mtx, np.matrix([[r], [0.0], [0.0]])
        ).A1.tolist()
    except Exception as e:
        raise

