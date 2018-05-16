"""
Class for Nutation.

: IAU2000A 章動理論(MHB2000, IERS2003)による
  黄経における章動(Δψ), 黄道傾斜における章動(Δε) の計算

* IAU SOFA(International Astronomical Union, Standards of Fundamental Astronomy)
  の提供する C ソースコード "nut00a.c" で実装されているアルゴリズムを使用する。
* 係数データの項目について
  - 日月章動(luni-solar nutation)
    (左から) L L' F D Om PS PST PC EC ECT ES
  - 惑星章動(planetary nutation)
    (左から) L L' F D Om Lm Lv Le LM Lj Ls Lu Ln Pa PS PC ES EC
* 参考サイト
  - [SOFA Library Issue 2012-03-01 for ANSI C: Complete List](http://www.iausofa.org/2012_0301_C/sofa/)
  - [USNO Circular 179](http://aa.usno.navy.mil/publications/docs/Circular_179.php)
  - [IERS Conventions Center](http://62.161.69.131/iers/conv2003/conv2003_c5.html)
"""
import math
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import const as lcst
import fundamental_argument as lfa


class Nutation:
    def __init__(self, jc):
        """ Initialization

        :param float jc: ユリウス世紀数
        """
        self.jc = jc
        self.__get_data()

    def __get_data(self):
        """ 定数(NUT_LS, NUT_PL)からデータ取得
            * luni-solar の最初の5列、planetary の最初の14列は整数に、
              残りの列は浮動小数点*10000にする
            * 読み込みデータは self.dat_ls, self.dat_pl に格納
        """
        try:
            self.dat_ls = [
                l[:5] + [x * 10000 for x in l[5:]]
                for l in lcst.NUT_LS
            ]
            self.dat_pl =[
                l[:14] + [x * 10000 for x in l[14:]]
                for l in lcst.NUT_PL
            ]
        except Exception as e:
            raise

    def calc_lunisolar(self):
        """ 日月章動(luni-solar nutation)の計算
            * ユリウス世紀数と定数(NUT_LS)から日月章動を計算

        :return list: [黄経における章動(Δψ), 黄道傾斜における章動(Δε)]
        """
        dp, de = 0.0, 0.0
        try:
            l  = lfa.l_iers2003(self.jc)
            lp = lfa.lp_mhb2000(self.jc)
            f  = lfa.f_iers2003(self.jc)
            d  = lfa.d_mhb2000(self.jc)
            om = lfa.om_iers2003(self.jc)
            for x in reversed(self.dat_ls):
                arg = (x[0] * l + x[1] * lp + x[2] * f \
                     + x[3] * d + x[4] * om) % lcst.PI2
                sarg, carg = math.sin(arg), math.cos(arg)
                dp += (x[5] + x[6] * self.jc) * sarg + x[ 7] * carg
                de += (x[8] + x[9] * self.jc) * carg + x[10] * sarg
            return [dp * lcst.U2R, de * lcst.U2R]
        except Exception as e:
            raise

    def calc_planetary(self):
        """ 惑星章動(planetary nutation)
            * ユリウス世紀数と定数(NUT_PL)から惑星章動を計算

        :return list    : [黄経における章動(Δψ), 黄道傾斜における章動(Δε)]
        """
        dp, de = 0.0, 0.0
        try:
            l  = lfa.l_mhb2000(self.jc)
            f  = lfa.f_mhb2000(self.jc)
            d  = lfa.d_mhb2000_2(self.jc)
            om = lfa.om_mhb2000(self.jc)
            pa = lfa.pa_iers2003(self.jc)
            me = lfa.lme_iers2003(self.jc)
            ve = lfa.lve_iers2003(self.jc)
            ea = lfa.lea_iers2003(self.jc)
            ma = lfa.lma_iers2003(self.jc)
            ju = lfa.lju_iers2003(self.jc)
            sa = lfa.lsa_iers2003(self.jc)
            ur = lfa.lur_iers2003(self.jc)
            ne = lfa.lne_mhb2000(self.jc)
            for x in reversed(self.dat_pl):
                arg = (x[ 0] * l  + x[ 2] * f  + x[ 3] * d  + x[ 4] * om \
                     + x[ 5] * me + x[ 6] * ve + x[ 7] * ea + x[ 8] * ma \
                     + x[ 9] * ju + x[10] * sa + x[11] * ur + x[12] * ne \
                     + x[13] * pa) % lcst.PI2
                sarg, carg = math.sin(arg), math.cos(arg)
                dp += x[14] * sarg + x[15] * carg
                de += x[16] * sarg + x[17] * carg
            return [dp * lcst.U2R, de * lcst.U2R]
        except Exception as e:
            raise

