#! /usr/local/bin/python3.6
"""
カレンダー
: 高野氏のプログラムのアルゴリズムを使用。
  但し、天体の正確な位置データは JPL DE430 から取得

  date          name            version
  2018.05.07    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
引数 : JST（日本標準時）
         書式：YYYYMMDD
         無指定なら現在(システム日時)と判断。
"""
from datetime import datetime
import re
import sys
import traceback
from lib import calendar as lcal


class JplCal:
    USAGE    = "[USAGE] ./jpl_cal.py [YYYYMMDD]"
    BIN_PATH = "/home/masaru/src/calendar_py/JPLEPH"

    def __init__(self):
        self.__get_arg()

    def exec(self):
        """ Execution """
        try:
            cal = lcal.Calendar(self.BIN_PATH, self.jst)
            self.jst    = cal.jst
            self.jd     = cal.jd
            self.jd_jst = cal.jd_jst
            self.yobi         = cal.yobi()
            self.holiday      = cal.holiday()
            self.kanshi       = cal.kanshi()
            self.sekki_24     = cal.sekki_24()
            self.sekku        = cal.sekku()
            self.zassetsu     = cal.zassetsu()
            self.kokei_sun    = cal.kokei_sun()
            self.kokei_moon   = cal.kokei_moon()
            self.moonage      = cal.moonage()
            self.oc           = cal.oc()
            self.__display()

            # 年間休日一覧も計算・出力する場合
            #self.holiday_year = cal.holiday_year()
            #print(self.holiday_year)

            # 月相も計算・出力する場合
            #diff = self.kokei_moon - self.kokei_sun
            #if diff < 0:
            #    diff += 360
            #moonphase = round(diff / 360 * 28)
            #print("---\n月相: " + str(moonphase))
        except Exception as e:
            raise

    def __get_arg(self):
        """ Argument getting """
        try:
            if len(sys.argv) < 2:
                now = datetime.now()
                self.jst = datetime(now.year, now.month, now.day)
                return
            if re.search(r"^\d{8}$", sys.argv[1]):
                dt = sys.argv[1]
            else:
                print("Invalid date!")
                sys.exit(0)
            try:
                self.jst = datetime.strptime(dt, "%Y%m%d")
            except ValueError as e:
                print("Invalid date!")
                sys.exit(0)
        except Exception as e:
            raise

    def __display(self):
        """ Display """
        try:
            leap = "(閏)" if self.oc[1] == 1 else ""
            print((
                "{},{}曜日,{},{}UTC({}JST),{},"
                "{:04d}-{:02d}-{:02d}{},{},"
                "{},{},{},"
                "{},{},{}"
            ).format(
                self.jst.strftime("%Y-%m-%d"),
                self.yobi, self.holiday, self.jd, self.jd_jst, self.kanshi,
                self.oc[0], self.oc[2], self.oc[3], leap, self.oc[4],
                self.sekki_24, self.zassetsu, self.sekku,
                self.kokei_sun, self.kokei_moon, self.moonage
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplCal()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

