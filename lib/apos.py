"""
Class for apparent position of Sun/Moon.

  date          name            version
  2018.05.01    mk-mode.com     1.00 新規作成
  2018.06.08    mk-mode.com     1.01 視半径／（地平）視差の計算処理を追加

Copyright(C) 2018 mk-mode.com All Rights Reserved.
"""
import math
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import const   as lcst
import coord   as lcd
import eph_bpn as lbpn
import eph_jpl as ljpl
import time_   as ltm


class Apos:
    def __init__(self, file_bin, utc):
        """ Initialization

        :param string file_bin: バイナリファイルのフルパス
        :param datetime    utc: UTC（協定世界時）
        """
        self.file_bin = file_bin
        self.utc = utc
        # === t1(= TDB), t2(= TDB) における位置・速度（ICRS 座標）用 Dict
        self.icrs_1, self.icrs_2 = {}, {}
        # === 時刻 t2 の変換（UTC（協定世界時） -> TDB（太陽系力学時））
        self.tdb = self.__utc2tdb(utc)
        # === 時刻 t2 のユリウス日
        self.jd_tdb = ltm.gc2jd(self.tdb)
        # === 時刻 t2(= TDB) におけるの位置・速度（ICRS 座標）の計算 (地球, 月, 太陽)
        #Const::BODIES.each { |k, v| @icrs_2[k] = get_icrs(v, @jd_tdb) }
        for k, v in lcst.BODIES.items():
            self.icrs_2[k] = self.__get_icrs(v, self.jd_tdb)
        # === 時刻 t2(= TDB) における地球と太陽・月の距離
        self.r_e = self.__get_r_e()
        # === 太陽／月／地球の半径取得
        de = ljpl.EphJpl(self.file_bin, 11, 3, self.jd_tdb)
        self.asun = de.cvals[de.cnams.index("ASUN")]
        self.am   = de.cvals[de.cnams.index("AM")]
        self.re   = de.cvals[de.cnams.index("RE")]

    def sun(self):
        """ Computation of Sun position

        :return list: [
                          [視赤経, 視赤緯, 地心距離],
                          [視黄経, 視黄緯, 地心距離],
                          [視半径, 視差]
                      ]
        """
        try:
            # === 太陽が光を発した時刻 t1(JD) の計算
            t_1_jd = self.__calc_t1("sun", self.tdb)
            # === 時刻 t1(= TDB) におけるの位置・速度（ICRS 座標）の計算 (地球, 月, 太陽)
            for k, v in lcst.BODIES.items():
                self.icrs_1[k] = self.__get_icrs(v, t_1_jd)
            # === 時刻 t2 における地球重心から時刻 t1 における太陽への方向ベクトルの計算
            v_12 = self.__calc_unit_vector(
                self.icrs_2["earth"][0:3], self.icrs_1["sun"][0:3]
            )
            # === GCRS 座標系: 光行差の補正（方向ベクトルの Lorentz 変換）
            dd = self.__conv_lorentz(v_12)
            pos_sun = [d * self.r_e["sun"] for d in dd]
            # === 瞬時の真座標系: GCRS への bias & precession（歳差） & nutation（章動）の適用
            bpn = lbpn.EphBpn(self.tdb)
            pos_sun_bpn = bpn.apply_bias_prec_nut(pos_sun)
            # === 座標変換
            eq_pol_s, eq_r = lcd.rect2pol(pos_sun_bpn)
            ec_rect_s      = lcd.rect_eq2ec(pos_sun_bpn, bpn.eps)
            ec_pol_s, ec_r = lcd.rect2pol(ec_rect_s)
            # === 視半径／（地平）視差計算
            radius = math.asin(self.asun / (eq_r * lcst.AU / 1000))
            radius *= 180 / math.pi * 3600
            parallax = math.asin(self.re / (eq_r * lcst.AU / 1000))
            parallax *= 180 / math.pi * 3600
            return [eq_pol_s + [eq_r], ec_pol_s + [ec_r], [radius, parallax]]
        except Exception as e:
            raise

    def moon(self):
        """ Computation of Moon position

        :return list: [
                          [視赤経, 視赤緯, 地心距離],
                          [視黄経, 視黄緯, 地心距離],
                          [視半径, 視差]
                      ]
        """
        try:
            pass
            # === 月が光を発した時刻 t1(jd) の計算
            t_1_jd = self.__calc_t1("moon", self.tdb)
            # === 時刻 t1(= TDB) におけるの位置・速度（ICRS 座標）の計算 (地球, 月, 太陽)
            for k, v in lcst.BODIES.items():
                self.icrs_1[k] = self.__get_icrs(v, t_1_jd)
            # === 時刻 t2 における地球重心から時刻 t1 における月への方向ベクトルの計算
            v_12 = self.__calc_unit_vector(
                self.icrs_2["earth"][0:3], self.icrs_1["moon"][0:3]
            )
            # === GCRS 座標系: 光行差の補正（方向ベクトルの Lorentz 変換）
            dd = self.__conv_lorentz(v_12)
            pos_moon = [d * self.r_e["moon"] for d in dd]
            # === 瞬時の真座標系: GCRS への bias & precession（歳差） & nutation（章動）の適用
            bpn = lbpn.EphBpn(self.tdb)
            pos_moon_bpn = bpn.apply_bias_prec_nut(pos_moon)
            # === 座標変換
            eq_pol_m, eq_r = lcd.rect2pol(pos_moon_bpn)
            ec_rect_m      = lcd.rect_eq2ec(pos_moon_bpn, bpn.eps)
            ec_pol_m, ec_r = lcd.rect2pol(ec_rect_m)
            # === 視半径／（地平）視差計算
            radius = math.asin(self.am / (eq_r * lcst.AU / 1000))
            radius *= 180 / math.pi * 3600
            parallax = math.asin(self.re / (eq_r * lcst.AU / 1000))
            parallax *= 180 / math.pi * 3600
            return [eq_pol_m + [eq_r], ec_pol_m + [ec_r], [radius, parallax]]
        except Exception as e:
            raise

    def __utc2tdb(self, utc):
        """ UTC（協定世界時） -> TDB（太陽系力学時）

        :param  datetime utc: 協定世界時
        :return datetime tdb: 太陽系力学時
        """
        try:
            utc_tai = ltm.utc2utc_tai(utc)
            tai     = ltm.utc2tai(utc, utc_tai)
            tt      = ltm.tai2tt(tai)
            jd      = ltm.gc2jd(utc)
            tcb     = ltm.tt2tcb(tt, jd)
            jd_tcb  = ltm.gc2jd(tcb)
            tdb     = ltm.tcb2tdb(tcb, jd_tcb)
            return tdb
        except Exception as e:
            raise

    def __get_icrs(self, target, jd):
        """ ICRS 座標取得
            * JPL DE430 データを自作 RubyGems ライブラリ eph_jpl を使用して取得

        :param  string target: 対象天体
        :param  float      jd: ユリウス日
        :return list [pos_x, pos_y, pos_z, vel_x, vel_y, vel_z]
                             : 位置・速度(単位: AU, AU/day)
        """
        try:
            de = ljpl.EphJpl(self.file_bin, target, 12, jd)
            return de.calc()
        except Exception as e:
            raise

    def __get_r_e(self):
        """ t2(= TDB) における地球と太陽・月の距離

        :return dict r_e: 地球と太陽・月の距離
        """
        r_e = {}
        try:
            for k, v in self.icrs_2.items():
                if k == "earth":
                    continue
                r_e[k] = self.__calc_dist(self.icrs_2["earth"][0:3], v[0:3])
            return r_e
        except Exception as e:
            raise

    def __calc_t1(self, target, tdb):
        """ 対象天体が光を発した時刻 t1 の計算（太陽・月専用）
            * 計算式： c * (t2 - t1) = r12  (但し、 c: 光の速度。 Newton 法で近似）
            * 太陽・月専用なので、太陽・木星・土星・天王星・海王星の重力場による
              光の曲がりは非考慮。

        :param  int   target: 対象天体(0:Sun, 1:Moon)
        :param  datetime tdb: 観測時刻(TDB)
        :return float    t_1: Julian Day
        """
        t_1 = ltm.gc2jd(tdb)
        t_2 = t_1
        pv_1 = self.icrs_2[target]
        df, m = 1.0, 0
        try:
            while df > 1.0e-10:
                r_12 = [pv_1[i] - self.icrs_2["earth"][i] for i in range(3)]
                r_12_d = self.__calc_dist(pv_1, self.icrs_2["earth"])
                df = (lcst.C * lcst.DAYSEC / lcst.AU) * (t_2 - t_1) - r_12_d
                df_wk = sum([
                    r_12[i] * self.icrs_2[target][i + 3]
                    for i in range(3)
                ])
                df /= (lcst.C * lcst.DAYSEC / lcst.AU) + df_wk / r_12_d
                t_1 += df
                m += 1
                if m > 10:
                    raise "[ERROR] Newton method error!"
                pv_1 = self.__get_icrs(lcst.BODIES[target], t_1)
            return t_1
        except Exception as e:
            raise

    def __calc_dist(self, pos_a, pos_b):
        """ 天体Aと天体Bの距離計算

        :param   list pos_a: 位置ベクトル
        :param   list pos_b: 位置ベクトル
        :return  float    r: 距離
        """
        try:
            r = sum([(pos_b[i] - pos_a[i]) ** 2 for i in range(3)])
            return math.sqrt(r)
        except Exception as e:
            raise

    def __calc_unit_vector(self, pos_a, pos_b):
        """ 天体Aから見た天体Bの方向ベクトル計算（太陽・月専用）
            * 太陽・月専用なので、太陽・木星・土星・天王星・海王星の重力場による
              光の曲がりは非考慮。

        :param   list pos_a: 位置ベクトル(天体A)
        :param   list pos_b: 位置ベクトル(天体B)
        :return  list   vec: 方向(単位)ベクトル
        """
        vec = [0.0, 0.0, 0.0]
        try:
            w = self.__calc_dist(pos_a, pos_b)
            if w == 0.0:
                return vec
            vec = [pos_b[i] - pos_a[i] for i in range(3)]
            return [v / w for v in vec]
        except Exception as e:
            raise

    def __conv_lorentz(self, vec_d):
        """ 光行差の補正（方向ベクトルの Lorentz 変換）
            * vec_dd = f * vec_d + (1 + g / (1 + f)) * vec_v
              但し、 f = vec_v * vec_d  (ベクトル内積)
                     g = sqrt(1 - v^2)  (v: 速度)

        :param  list  v_d: 方向（単位）ベクトル
        :return list v_dd: 補正後ベクトル
        """
        try:
            vec_v = [
                (v / lcst.DAYSEC) / (lcst.C / lcst.AU)
                for v in self.icrs_2["earth"][3:6]
            ]
            g = sum([vec_v[i] * vec_d[i] for i in range(3)])
            f = math.sqrt(1.0 - math.sqrt(sum([v * v for v in vec_v])))
            vec_dd_1 = [d * f for d in vec_d]
            vec_dd_2 = [(1.0 + g / (1.0 + f)) * v for v in vec_v]
            vec_dd = [vec_dd_1[i] + vec_dd_2[i] for i in range(3)]
            vec_dd = [a / (1.0 + g) for a in vec_dd]
            return vec_dd
        except Exception as e:
            raise

