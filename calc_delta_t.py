#! /usr/local/bin/python3
"""
地球自転速度の補正値 delta T(ΔT)の計算
: [NASA - Polynomial Expressions for Delta T]
  (http://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html)
  の計算式を使用する。
  1972年 - 2018年は、比較対象として「うるう年総和 + 32.184(TT - TAI)」
  の値も計算する。

  date          name            version
  2018.04.29    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数 : YYYYMM
         * YYYYMM は UTC
         * 無指定なら現在年月を UTC とみなす。
"""
import re
import sys
import traceback
from datetime import datetime
from lib import delta_t as ldt


class CalcDeltaT:
    USAGE     = "[USAGE] ./calc_delta_t.py [[+-]YYYYMM]"
    MSG_ERR_1 = "[ERROR] Year must be between -1999 and 3000!"
    MSG_ERR_2 = "[ERROR] Month must be between 1 and 12!"

    def __init__(self):
        self.__get_arg()

    def exec(self):
        try:
            obj = ldt.DeltaT(self.year, self.month)
            dt = obj.delta_t()
            print("[{:04d}-{:02d}] ".format(self.year, self.month))
            print("delta T =", dt)
        except Exception as e:
            raise

    def __get_arg(self):
        """ Argument getting """
        try:
            if len(sys.argv) > 1:
                ym = sys.argv[1]
            else:
                ym = datetime.now().strftime("%Y%m")
            if re.search(r"^[+-]?\d{6}$", ym) is None:
                print(self.USAGE)
                sys.exit(0)
            m = re.findall(r"([+-]?\d{4})(\d{2})", ym)[0]
            self.year, self.month = int(m[0]), int(m[1])
            if self.year < -1999 or self.year > 3000:
                print(self.MSG_ERR_1)
                sys.exit(0)
            if self.month < 1 or self.month > 12:
                print(self.MSG_ERR_2)
                sys.exit(0)
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = CalcDeltaT()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

