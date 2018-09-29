#! /usr/local/bin/python3
"""
章動の計算
: IAU2000A 章動理論(MHB2000, IERS2003)による
  黄経における章動(Δψ), 黄道傾斜における章動(Δε) の計算

* IAU SOFA(International Astronomical Union, Standards of Fundamental Astronomy)
  の提供する C ソースコード "nut00a.c" で実装されているアルゴリズムを使用する。
* 参考サイト
  - [SOFA Library Issue 2012-03-01 for ANSI C: Complete List](http://www.iausofa.org/2012_0301_C/sofa/)
  - [USNO Circular 179](http://aa.usno.navy.mil/publications/docs/Circular_179.php)
  - [IERS Conventions Center](http://62.161.69.131/iers/conv2003/conv2003_c5.html)

  Date          Author          Version
  2018.04.28    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
引数 : 日時(TT（地球時）)
         書式：YYYYMMDD or YYYYMMDDHHMMSS
         無指定なら現在(システム日時)を地球時とみなす。
"""
from datetime import datetime
import re
import sys
import traceback
from lib import const    as lcst
from lib import nutation as lnt
from lib import time_    as ltm

class NutationModel:
    def __init__(self):
        self.__get_arg()

    def exec(self):
        """ 実行 """
        try:
            jd = ltm.gc2jd(self.tt)
            jc = ltm.jd2jc(jd)
            nt = lnt.Nutation(jc)
            dpsi_ls, deps_ls = nt.calc_lunisolar()
            dpsi_pl, deps_pl = nt.calc_planetary()
            self.dpsi = dpsi_ls + dpsi_pl
            self.deps = deps_ls + deps_pl
            # IAU 2000A nutation with adjustments to match 
            # the IAU 2006 precession.
            # * 以下3行は、「IAU 2006 歳差」理論を適用する場合の微調整
            #fj2 = -2.7774e-6 * jc
            #self.dpsi += self.dpsi * (0.4697e-6 + fj2)
            #self.deps += self.deps * fj2
            self.dpsi_d = self.dpsi * lcst.R2D
            self.deps_d = self.deps * lcst.R2D
            self.dpsi_s = self.dpsi_d * lcst.D2S
            self.deps_s = self.deps_d * lcst.D2S
            self.__display()
        except Exception as e:
            raise

    def __get_arg(self):
        """ コマンドライン引数の取得
            * コマンドライン引数で指定した日時を self.tt に設定
            * コマンドライン引数が存在しなければ、現在時刻を self.tt に設定
        """
        try:
            if len(sys.argv) < 2:
                self.tt = datetime.now()
                return
            if re.search(r"^\d{8}$", sys.argv[1]) is not(None):
                dt = sys.argv[1] + "000000"
            elif re.search(r"^\d{14}$", sys.argv[1]) is not(None):
                dt = sys.argv[1]
            else:
                print("Invalid date!")
                sys.exit(0)
            try:
                self.tt = datetime.strptime(dt, "%Y%m%d%H%M%S")
            except ValueError as e:
                print("Invalid date!")
                sys.exit(0)
        except Exception as e:
            raise

    def __display(self):
        """ Display """
        try:
            print((
                "  [{} TT]\n"
                "  DeltaPsi = {} rad\n"
                "           = {} °\n"
                "           = {} ″\n"
                "  DeltaEps = {} rad\n"
                "           = {} °\n"
                "           = {} ″"
            ).format(
                self.tt.strftime("%Y-%m-%d %H:%M:%S"),
                self.dpsi, self.dpsi_d, self.dpsi_s,
                self.deps, self.deps_d, self.deps_s
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = NutationModel()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

