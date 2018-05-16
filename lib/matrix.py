"""
Modules for matrixes
"""
import numpy as np


R_UNIT = np.eye(3, dtype="float64")


def r_x(phi, r_src=R_UNIT):
    """ 回転行列生成(x軸中心)
          ( 1      0          0     )
          ( 0  +cos(phi)  +sin(phi) )
          ( 0  -sin(phi)  +cos(phi) )

    :param  np.matrix r_src: Rotation matrix
    :param  float       phi: Angle (Unit: rad)
    :return np.matrix r_dst: Rotated matrix
    """
    try:
        s, c = np.sin(phi), np.cos(phi)
        r_mx = np.matrix([
            [1,  0, 0],
            [0,  c, s],
            [0, -s, c]
        ], dtype="float64")
        return r_mx * r_src
    except Exception as e:
        raise

def r_y(theta, r_src=R_UNIT):
    """ 回転行列生成(y軸中心)
          ( +cos(theta)  0  -sin(theta) )
          (     0        1      0       )
          ( +sin(theta)  0  +cos(theta) )

    :param  np.matrix r_src: Rotation matrix
    :param  float     theta: Angle (Unit: rad)
    :return np.matrix r_dst: Rotated matrix
    """
    try:
        s, c = np.sin(theta), np.cos(theta)
        r_mx = np.matrix([
            [c, 0, -s],
            [0, 1,  0],
            [s, 0,  c]
        ], dtype="float64")
        return r_mx * r_src
    except Exception as e:
        raise

def r_z(psi, r_src=R_UNIT):
    """ 回転行列生成(z軸中心)
          ( +cos(psi)  +sin(psi)  0 )
          ( -sin(psi)  +cos(psi)  0 )
          (     0          0      1 )

    :param  np.matrix r_src: Rotation matrix
    :param  float       psi: Angle (Unit: rad)
    :return np.matrix r_dst: Rotated matrix
    """
    try:
        s, c = np.sin(psi), np.cos(psi)
        r_mx = np.matrix([
            [ c, s, 0],
            [-s, c, 0],
            [ 0, 0, 1]
        ], dtype="float64")
        return r_mx * r_src
    except Exception as e:
        raise

def rotate(r, pos):
    """ 座標回転

    :param  np.matrix r    : 回転行列
    :param  np.matrix pos  : 回転前直交座標
    :return np.matrix pos_r: 回転後直交座標
    """
    try:
        return r * pos
    except Exception as e:
        raise

