#! /usr/local/bin/python3
"""
太陽・月の視位置計算
* JPLEPH(JPL の DE430 バイナリデータ)を読み込み、視位置を計算する

  date          name            version
  2018.05.03    mk-mode.com     1.00 新規作成
  2018.06.08    mk-mode.com     1.01 視半径／（地平）視差を追加

Copyright(C) 2018 mk-mode.com All Rights Reserved.
----------------------------------------------------------------------
# 引数 : 日時(JST)
#          書式：YYYYMMDD or YYYYMMDDHHMMSS or YYYYMMDDHHMMSSffffff
#          無指定なら現在(システム日時)と判断。
"""
import math
import re
import sys
import traceback
from datetime import datetime
from datetime import timedelta
from lib import apos
from lib.const import AU  # 1天文単位 (m)


class ApparentSunMoonJpl:
    USAGE    = "[USAGE] ./apparent_sun_moon_jpl.py [YYYYMMDD|YYYYMMDDHHMMSS|YYYYMMDDHHMMSSffffff]"
    FILE_BIN = "/path/to/JPLEPH"

    def __init__(self):
        self.jst = self.__get_arg()
        self.utc = self.jst - timedelta(hours=9)

    def exec(self):
        """ Execution """
        try:
            ap = apos.Apos(self.FILE_BIN, self.utc)
            self.tdb    = ap.tdb
            self.jd_tdb = ap.jd_tdb
            self.sun  = ap.sun()
            self.moon = ap.moon()
            self.__display()
        except Exception as e:
            raise

    def __get_arg(self):
        """ コマンドライン引数取得
            * 第１引数の値をインスタンス変数 self.jst に設定する
              （但し、第１引数が存在しない場合は現在日時を設定する）
        """
        try:
            if len(sys.argv) < 2:
                return datetime.now()
            if re.search(r"^(\d{8}|\d{14}|\d{20})$", sys.argv[1]):
                dt = "{:<020}".format(sys.argv[1])
            else:
                print(self.USAGE)
                sys.exit(0)
            try:
                return datetime.strptime(dt, "%Y%m%d%H%M%S%f")
            except ValueError as e:
                print(self.USAGE)
                sys.exit(0)
        except Exception as e:
            raise

    def __display(self):
        """ Display """
        try:
            print((
                "* 計算対象時刻 (JST) = {}\n"
                "               (UTC) = {}\n"
                "               (TDB) = {}\n"
                "                (JD) = {}\n"
                "* 視位置：太陽\n"
                "  = [赤経: {:14.10f} rad, 赤緯: {:14.10f} rad]\n"
                "  = [赤経: {:14.10f} deg, 赤緯: {:14.10f} deg]\n"
                "  = [黄経: {:14.10f} rad, 黄緯: {:14.10f} rad]\n"
                "  = [黄経: {:14.10f} deg, 黄緯: {:14.10f} deg]\n"
                "* 視位置：月\n"
                "  = [赤経: {:14.10f} rad, 赤緯: {:14.10f} rad]\n"
                "  = [赤経: {:14.10f} deg, 赤緯: {:14.10f} deg]\n"
                "  = [黄経: {:14.10f} rad, 黄緯: {:14.10f} rad]\n"
                "  = [黄経: {:14.10f} deg, 黄緯: {:14.10f} deg]\n"
                "* 視黄経差：太陽 - 月\n"
                "  = {:.10f} rad\n"
                "  = {:.10f} deg\n"
                "* 距離：太陽\n"
                "  = {:.10f} AU\n"
                "  = {:.2f} km\n"
                "* 距離：月\n"
                "  = {:.10f} AU\n"
                "  = {:.2f} km\n"
                "* 視半径：太陽\n"
                "  = {:.2f} ″\n"
                "* 視半径：月\n"
                "  = {:.2f} ″\n"
                "* （地平）視差：太陽\n"
                "  = {:.2f} ″\n"
                "* （地平）視差：月\n"
                "  = {:.2f} ″"
            ).format(
                self.jst.strftime("%Y-%m-%d %H:%M:%S.%f"),
                self.utc.strftime("%Y-%m-%d %H:%M:%S.%f"),
                self.tdb.strftime("%Y-%m-%d %H:%M:%S.%f"),
                self.jd_tdb,
                self.sun[0][0], self.sun[0][1],
                self.sun[0][0] * 180 / math.pi,
                self.sun[0][1] * 180 / math.pi,
                self.sun[1][0], self.sun[1][1],
                self.sun[1][0] * 180 / math.pi,
                self.sun[1][1] * 180 / math.pi,
                self.moon[0][0], self.moon[0][1],
                self.moon[0][0] * 180 / math.pi,
                self.moon[0][1] * 180 / math.pi,
                self.moon[1][0], self.moon[1][1],
                self.moon[1][0] * 180 / math.pi,
                self.moon[1][1] * 180 / math.pi,
                self.sun[1][0] - self.moon[1][0],
                (self.sun[1][0] - self.moon[1][0]) * 180 / math.pi,
                self.sun[0][2],
                self.sun[0][2] * AU / 1000,
                self.moon[0][2],
                self.moon[0][2] * AU / 1000,
                self.sun[2][0],
                self.moon[2][0],
                self.sun[2][1],
                self.moon[2][1]
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = ApparentSunMoonJpl()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

