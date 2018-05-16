#! /usr/local/bin/python3.6
"""
平均黄道傾斜角の計算

  date          name            version
  2018.04.09    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
引数 : 日時(TT（地球時）)
         書式：YYYYMMDD or YYYYMMDDHHMMSS or YYYYMMDDHHMMSSUUUUUU
         無指定なら現在(システム日時)を地球時とみなす。
"""
from datetime import datetime
import re
import sys
import traceback


class MeanObliquityEcliptic:
    def __init__(self):
        self.__get_arg()

    def exec(self):
        """ 実行 """
        try:
            self.__calc_jd()
            self.__calc_t()
            self.__calc_eps_a()
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
            if re.search(r"^(\d{8}|\d{14}|\d{20})$", sys.argv[1]):
                tt = sys.argv[1].ljust(20, "0")
            else:
                sys.exit(0)
            try:
                self.tt = datetime.strptime(tt, "%Y%m%d%H%M%S%f")
            except ValueError as e:
                print("Invalid date!")
                sys.exit(0)
        except Exception as e:
            raise

    def __calc_jd(self):
        """ ユリウス日の計算
            * 地球時 self.tt のユリウス日を計算し、self.jd に設定
        """
        year, month,  day    = self.tt.year, self.tt.month,  self.tt.day
        hour, minute, second = self.tt.hour, self.tt.minute, self.tt.second
        second += self.tt.microsecond
        try:
            if month < 3:
                year  -= 1
                month += 12
            d = int(365.25 * year) + year // 400  - year // 100 \
              + int(30.59 * (month - 2)) + day + 1721088.5
            t  = (second / 3600 + minute / 60 + hour) / 24
            self.jd = d + t
        except Exception as e:
            raise

    def __calc_t(self):
        """ ユリウス世紀数の計算
            * ユリウス日 self.jd のユリウス世紀数を計算し、 self.t に設定
        """
        try:
            self.t = (self.jd - 2451545) / 36525
        except Exception as e:
            raise

    def __calc_eps_a(self):
        """ 黄道傾斜角(εA)の計算
            * ユリウス世紀数 self.t から黄道傾斜角 ε （単位: rad）を計算し、
              self.eps_a に設定
            * 以下の計算式により求める。
                ε = 84381.406 - 46.836769 * T - 0.0001831 T^2 + 0.00200340 T^3
                  - 5.76 * 10^(-7) * T^4 - 4.34 * 10^(-8) * T^5
              ここで、 T は J2000.0 からの経過時間を 36525 日単位で表したユリウス
              世紀数で、 T = (JD - 2451545) / 36525 である。
        """
        t = self.t
        try:
            self.eps_a = (84381.406      \
                       + (  -46.836769   \
                       + (   -0.0001831  \
                       + (    0.00200340 \
                       + (   -5.76e-7    \
                       + (   -4.34e-8)   \
                       * t) * t) * t) * t) * t) / 3600
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
                datetime.strftime(self.tt, "%Y-%m-%d %H:%M:%S.%f"),
                self.jd, self.t, self.eps_a
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

