#! /usr/local/bin/python3.6
"""
バイアス・歳差・章動適用

  date          name            version
  2018.04.30    mk-mode         1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
引数 : 日時(TDB（太陽系力学時）)
         書式：YYYYMMDD or YYYYMMDDHHMMSS
         無指定なら現在(システム日時)を太陽系力学時とみなす。
"""
from datetime import datetime
import re
import sys
import traceback
from lib import eph_bpn as lbpn


class BpnRotation:
    COORD = [-1.0020195, 0.0660430, 0.0286337]

    def __init__(self):
        self.__get_arg()

    def exec(self):
        try:
            bpn = lbpn.EphBpn(self.tdb)
            self.jd  = bpn.jd
            self.jc  = bpn.jc
            self.eps = bpn.eps
            self.pos_b = bpn.apply_bias(self.COORD)
            self.pos_p = bpn.apply_prec(self.pos_b)
            self.pos_n = bpn.apply_nut(self.pos_p)
            self.pos_bp = bpn.apply_bias_prec(self.COORD)
            self.__display()
        except Exception as e:
            raise

    def __get_arg(self):
        """ コマンドライン引数の取得
            * コマンドライン引数で指定した日時を self.tdb に設定
            * コマンドライン引数が存在しなければ、現在時刻を self.tdb に設定
        """
        try:
            if len(sys.argv) < 2:
                self.tdb = datetime.now()
                return
            if re.search(r"^\d{8}$", sys.argv[1]) is not(None):
                dt = sys.argv[1] + "000000"
            elif re.search(r"^\d{14}$", sys.argv[1]) is not(None):
                dt = sys.argv[1]
            else:
                sys.exit(0)
            try:
                self.tdb = datetime.strptime(dt, "%Y%m%d%H%M%S")
            except ValueError as e:
                print("Invalid date!")
                sys.exit(0)
        except Exception as e:
            raise

    def __display(self):
        """ 結果出力 """
        try:
            tdb  = self.tdb.strftime('%Y-%m-%d %H:%M:%S')
            tdb += ".{:06d}".format(self.tdb.microsecond)
            print((
                "TDB: {}\n"
                " JD: {}\n"
                " JC: {}\n"
                "EPS: {}\n"
                "  元の GCRS 座標: {}\n"
                "  バイアス適用後: {}\n"
                "      歳差適用後: {}\n"
                "      章動適用後: {}\n"
                "* 元の GCRS 座標にバイアス＆歳差同時適用後:\n"
                "                  {})"
            ).format(
                tdb,
                self.jd,
                self.jc,
                self.eps,
                self.COORD,
                self.pos_b,
                self.pos_p,
                self.pos_n,
                self.pos_bp
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = BpnRotation()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

