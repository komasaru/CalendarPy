#! /usr/local/bin/python3
"""
平均黄道傾斜角の計算

  date          name            version
  2018.04.09    mk-mode.com     1.00 新規作成

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
from lib import const   as lcst
from lib import eph_bpn as lbpn
from lib import time_   as ltm


class MeanObliquityEcliptic:
    def __init__(self):
        self.__get_arg()

    def exec(self):
        """ 実行 """
        try:
            self.jd = ltm.gc2jd(self.tt)
            self.jc = ltm.jd2jc(self.jd)
            bpn = lbpn.EphBpn(self.tt)
            self.eps_a = bpn.eps
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
        """ 結果表示 """
        try:
            print((
                "           地球時(TT): {}\n"
                "       ユリウス日(JD): {}\n"
                "   ユリウス世紀数(JC): {}\n"
                "平均黄道傾斜角(eps_a): {} °"
            ).format(
                datetime.strftime(self.tt, "%Y-%m-%d %H:%M:%S"),
                self.jd, self.jc, self.eps_a * lcst.R2D  # R2D: Rad -> Deg
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = MeanObliquityEcliptic()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

