"""
Class for bpn-rotation.
"""
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import const    as lcst
import matrix   as lmtx
import nutation as lnut
import time_    as ltm


class EphBpn:
    def __init__(self, tt):
        self.tt = tt                              # TT(地球時)
        self.jd  = ltm.gc2jd(self.tt)             # TT -> JD(ユリウス日)
        self.jc  = ltm.jd2jc(self.jd)             # JD -> JC(ユリウス世紀数)
        self.eps = self.__obliquity(self.jc)      # 平均黄道傾斜角
        self.dpsi, self.deps = self.__nutation()  # 章動
        self.r_mtx_b   = self.__r_mtx_b()         # 回転行列（バイアス）
        self.r_mtx_bp  = self.__r_mtx_bp()        # 回転行列（バイアス＆歳差）
        self.r_mtx_bpn = self.__r_mtx_bpn()       # 回転行列（バイアス＆歳差＆章動）
        self.r_mtx_p   = self.__r_mtx_p()         # 回転行列（歳差）
        self.r_mtx_pn  = self.__r_mtx_pn()        # 回転行列（歳差＆章動）
        self.r_mtx_n   = self.__r_mtx_n()         # 回転行列（章動）

    def apply_bias(self, pos):
        """ Bias 適用

        :param  list pos: 適用前直角座標
        :return list    : 適用後直角座標
        """
        try:
            pos_np = np.matrix([pos]).transpose()
            return lmtx.rotate(self.r_mtx_b, pos_np).A1.tolist()
        except Exception as e:
            raise

    def apply_bias_prec(self, pos):
        """ Bias + Precession（歳差） 適用

        :param  list pos: 適用前直角座標
        :return list    : 適用後直角座標
        """
        try:
            pos_np = np.matrix([pos]).transpose()
            return lmtx.rotate(self.r_mtx_bp, pos_np).A1.tolist()
        except Exception as e:
            raise

    def apply_bias_prec_nut(self, pos):
        """ Bias + Precession（歳差） + Nutation（章動） 適用

        :param  list pos: 適用前直角座標
        :return list    : 適用後直角座標
        """
        try:
            pos_np = np.matrix([pos]).transpose()
            return lmtx.rotate(self.r_mtx_bpn, pos_np).A1.tolist()
        except Exception as e:
            raise

    def apply_prec(self, pos):
        """ Precession（歳差） 適用

        :param  list pos: 適用前直角座標
        :return list    : 適用後直角座標
        """
        try:
            pos_np = np.matrix([pos]).transpose()
            return lmtx.rotate(self.r_mtx_p, pos_np).A1.tolist()
        except Exception as e:
            raise

    def apply_prec_nut(self, pos):
        """ Precession（歳差） + Nutation（章動） 適用

        :param  list pos: 適用前直角座標
        :return list    : 適用後直角座標
        """
        try:
            pos_np = np.matrix([pos]).transpose()
            return lmtx.rotate(self.r_mtx_pn, pos_np).A1.tolist()
        except Exception as e:
            raise

    def apply_nut(self, pos):
        """ Nutation（章動） 適用

        :param  list pos: 適用前直角座標
        :return list    : 適用後直角座標
        """
        try:
            pos_np = np.matrix([pos]).transpose()
            return lmtx.rotate(self.r_mtx_n, pos_np).A1.tolist()
        except Exception as e:
            raise

    def __obliquity(self, jc):
        """ 黄道傾斜角計算
            * 黄道傾斜角 ε （単位: rad）を計算する。
              以下の計算式により求める。
                ε = 84381.406 - 46.836769 * T - 0.0001831 T^2 + 0.00200340 T^3
                  - 5.76 * 10^(-7) * T^4 - 4.34 * 10^(-8) * T^5
              ここで、 T は J2000.0 からの経過時間を 36525 日単位で表したユリウス
              世紀数で、 T = (JD - 2451545) / 36525 である。

        :param  float  jc: ユリウス世紀数
        :return float    : 平均黄道傾斜角
        """
        try:
            return (84381.406      \
                 + (  -46.836769   \
                 + (   -0.0001831  \
                 + (    0.00200340 \
                 + (   -5.76e-7    \
                 + (   -4.34e-8 )  \
                 * jc) * jc) * jc) * jc) * jc) * lcst.AS2R
        except Exception as e:
            raise

    def __nutation(self):
        """ 章動計算

        :return list [dpsi, deps]: Δψ, Δε
        """
        try:
            nut = lnut.Nutation(self.jc)
            fj2 = -2.7774e-6 * self.jc
            dpsi_ls, deps_ls = nut.calc_lunisolar()
            dpsi_pl, deps_pl = nut.calc_planetary()
            dpsi, deps = dpsi_ls + dpsi_pl, deps_ls + deps_pl
            dpsi += dpsi * (0.4697e-6 + fj2)
            deps += deps * fj2
            return [dpsi, deps]
        except Exception as e:
            raise

    def __r_mtx_b(self):
        """ Bias 変換行列（一般的な理論）
            * 赤道座標(J2000.0)の極は ICRS の極に対して12時（x軸のマイナス側）の
              方向へ 17.3±0.2 mas、18時（y軸のマイナス側）の方向へ 5.1±0.2 mas
              ズレているので、変換する。
              さらに、平均分点への変換はICRSでの赤経を78±10 mas、天の極を中心に
              回転させる。
                18時の方向の変換はx軸を-5.1mas回転
                            | 1     0      0   |
                  R1(θ ) = | 0   cosθ  sinθ |
                            | 0  -sinθ  cosθ |
                12時の方向の変換はy軸を-17.3mas回転
                            | cosθ  0  -sinθ |
                  R2(θ ) = |   0    1     0   |
                            | sinθ  0   cosθ |
                天の極を中心に78.0mas回転
                            |  cosθ  sinθ  0 |
                  R3(θ ) = | -sinθ  cosθ  0 |
                            |    0      0    1 |

        :return np.matrix r: 回転行列
        """
        try:
            r = lmtx.r_x( -5.1 * lcst.MAS2R)
            r = lmtx.r_y(-17.3 * lcst.MAS2R, r)
            r = lmtx.r_z( 78.0 * lcst.MAS2R, r)
            return r
        except Exception as e:
            raise

    def __r_mtx_bp(self):
        """ Bias + Precession 変換行列
            * IAU 2006 (Fukushima-Williams 4-angle formulation) 理論

        :return np.matrix r: 変換行列
        """
        try:
            gam = self.__gamma_bp()
            phi = self.__phi_bp()
            psi = self.__psi_bp()
            r = lmtx.r_z(gam)
            r = lmtx.r_x(phi,   r)
            r = lmtx.r_z(-psi,  r)
            r = lmtx.r_x(-self.eps, r)
            return r
        except Exception as e:
            raise

    def __r_mtx_bpn(self):
        """ Bias + Precession + Nutation 変換行列
            * IAU 2006 (Fukushima-Williams 4-angle formulation) 理論

        :return np.matrix r: 変換行列
        """
        try:
            gam = self.__gamma_bp()
            phi = self.__phi_bp()
            psi = self.__psi_bp()
            r = lmtx.r_z(gam)
            r = lmtx.r_x(phi, r)
            r = lmtx.r_z(-psi - self.dpsi, r)
            r = lmtx.r_x(-self.eps - self.deps, r)
            return r
        except Exception as e:
            raise

    def __r_mtx_p(self):
        """ precession（歳差）変換行列（J2000.0 用）
            * 歳差の変換行列
                P(ε, ψ, φ, γ) = R1(-ε) * R3(-ψ) * R1(φ) * R3(γ)
              但し、R1, R2, R3 は x, y, z 軸の回転。
                         | 1     0      0   |           |  cosθ  sinθ  0 |
                R1(θ) = | 0   cosθ  sinθ |, R3(θ) = | -sinθ  cosθ  0 |
                         | 0  -sinθ  cosθ |           |    0      0    1 |
                                    | P_11 P_12 P_13 |
                P(ε, ψ, φ, γ) = | P_21 P_22 P_23 | とすると、
                                    | P_31 P_32 P_33 |
                P_11 = cosψcosγ + sinψcosφsinγ
                P_12 = cosψsinγ - sinψcosφcosγ
                P_13 = -sinψsinφ
                P_21 = cosεsinψcosγ - (cosεcosψcosφ + sinεsinφ)sinγ
                P_22 = cosεsinψcosγ + (cosεcosψcosφ + sinεsinφ)cosγ
                P_23 = cosεcosψsinφ - sinεcosφ
                P_31 = sinεsinψcosγ - (sinεcosψcosφ - cosεsinφ)sinγ
                P_32 = sinεsinψcosγ + (sinεcosψcosφ - cosεsinφ)cosγ
                P_33 = sinεcosψsinφ + cosεcosφ

        :return np.matrix r: 変換行列
        """
        try:
            gam = self.__gamma_p()
            phi = self.__phi_p()
            psi = self.__psi_p()
            r = lmtx.r_z(gam)
            r = lmtx.r_x(phi, r)
            r = lmtx.r_z(-psi, r)
            r = lmtx.r_x(-self.eps, r)
            return r
        except Exception as e:
            raise

    def __r_mtx_pn(self):
        """ Precession + Nutation 変換行列
            * IAU 2000A nutation with adjustments to match the IAU 2006 precession.

        :return np.matrix r: 変換行列
        """
        try:
            gam = self.__gamma_p()
            phi = self.__phi_p()
            psi = self.__psi_p()
            r = lmtx.r_z(gam)
            r = lmtx.r_x(phi, r)
            r = lmtx.r_z(-psi - self.dpsi, r)
            r = lmtx.r_x(-self.eps - self.deps, r)
            return r
        except Exception as e:
            raise

    def __r_mtx_n(self):
        """ nutation（章動）変換行列
            * IAU 2000A nutation with adjustments to match the IAU 2006 precession.

        :return np.matrix r: 変換行列
        """
        try:
            r = lmtx.r_x(self.eps)
            r = lmtx.r_z(-self.dpsi, r)
            r = lmtx.r_x(-self.eps - self.deps, r)
            return r
        except Exception as e:
            raise

    def __gamma_p(self):
        """ 歳差変換行列用 gamma 計算

        :return float gamma
        """
        t = self.jc
        try:
            return ((10.556403      \
                  + ( 0.4932044     \
                  + (-0.00031238    \
                  + (-0.000002788   \
                  + ( 0.0000000260) \
                  * t) * t) * t) * t) * t) * lcst.AS2R
        except Exception as e:
            raise

    def __phi_p(self):
        """ 歳差変換行列用 phi 計算

        :return float phi
        """
        t = self.jc
        try:
            return (84381.406000      \
                 + (  -46.811015      \
                 + (    0.0511269     \
                 + (    0.00053289    \
                 + (   -0.000000440   \
                 + (   -0.0000000176) \
                 * t) * t) * t) * t) * t) * lcst.AS2R
        except Exception as e:
            raise

    def __psi_p(self):
        """ 歳差変換行列用 psi 計算

        :return float psi
        """
        t = self.jc
        try:
            return (( 5038.481507      \
                  + (    1.5584176     \
                  + (   -0.00018522    \
                  + (   -0.000026452   \
                  + (   -0.0000000148) \
                  * t) * t) * t) * t) * t) * lcst.AS2R
        except Exception as e:
            raise

    def __gamma_bp(self):
        """ バイアス＆歳差変換行列用 gamma 計算

        :return float gamma
        """
        t = self.jc
        try:
            return (-0.052928      \
                 + (10.556378      \
                 + ( 0.4932044     \
                 + (-0.00031238    \
                 + (-0.000002788   \
                 + ( 0.0000000260) \
                 * t) * t) * t) * t) * t) * lcst.AS2R
        except Exception as e:
            raise

    def __phi_bp(self):
        """ バイアス＆歳差変換行列用 phi 計算

        :return float phi
        """
        t = self.jc
        try:
            return (84381.412819      \
                 + (  -46.811016      \
                 + (    0.0511268     \
                 + (    0.00053289    \
                 + (   -0.000000440   \
                 + (   -0.0000000176) \
                 * t) * t) * t) * t) * t) * lcst.AS2R
        except Exception as e:
            raise

    def __psi_bp(self):
        """ バイアス＆歳差変換行列用 psi 計算

        :return float psi
        """
        t = self.jc
        try:
            return (  -0.041775      \
                  +(5038.481484      \
                  +(   1.5584175     \
                  +(  -0.00018522    \
                  +(  -0.000026452   \
                  +(  -0.0000000148) \
                  * t) * t) * t) * t) * t) * lcst.AS2R
        except Exception as e:
            raise

