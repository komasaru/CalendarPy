#! /usr/local/bin/python3.6
"""
黄経一覧

  date          name            version
  2018.05.05    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数: [西暦年(START) [西暦年(END)]]
        ( 西暦年(START, END)の範囲: 0000 - 9999 )
"""
import MySQLdb
import math
import sys
import traceback
from datetime import datetime
from lib import apos


class JplKokei:
    BIN_PATH     = "/home/masaru/src/calendar_py/JPLEPH"
    Y_MIN, Y_MAX = 1899, 2100  #0, 9999
    USAGE        = "[USAGE] ./jpl_kokei.py [YYYY [YYYY]]"
    DAYS         = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    JST_D        = 0.375
    DATABASE     = "calendar"
    HOSTNAME     = "127.0.0.1"
    USERNAME     = "******"
    PASSWORD     = "**********"
    REG          = False  # DB 登録も行う場合は True

    def __init__(self):
        self.__get_arg()
        if self.REG:
            self.conn = MySQLdb.connect(
                db     = self.DATABASE,
                host   = self.HOSTNAME,
                user   = self.USERNAME,
                passwd = self.PASSWORD
            )

    def exec(self):
        """ Execution """
        try:
            for year in range(self.year_s, self.year_e + 1):
                data = []
                for month in range(1, 13):
                    days = self.DAYS[month - 1]
                    if month == 2 and self.__is_leap(year):
                        days += 1
                    for day in range(1, days + 1):
                        jd = self.__gc2jd(year, month, day)
                        kokei_sun, kokei_moon = self.__comp_kokei(jd)
                        print((
                            "* {:04d}-{:02d}-{:02d} "
                            "- {:12.8f} {:12.8f}"
                        ).format(
                            year, month, day, kokei_sun, kokei_moon
                        ))
                        data.append([year, month, day, kokei_sun, kokei_moon])
                if self.REG:
                    self.__del_dat_kokei(self.conn, year)
                    self.__ins_dat_kokei(self.conn, data)
        except Exception as e:
            raise
        finally:
            if self.REG:
                self.conn.close()

    def __get_arg(self):
        """ Argument getting """
        try:
            if len(sys.argv) < 2:
                self.year_s = self.Y_MIN
                self.year_e = self.Y_MAX
            elif len(sys.argv) == 2:
                self.year_s = int(sys.argv[1])
                self.year_e = self.Y_MAX
            elif len(sys.argv) > 2:
                self.year_s = int(sys.argv[1])
                self.year_e = int(sys.argv[2])
            if self.year_s > self.year_e:
                tmp = self.year_s
                self.year_s = self.year_e
                self.year_e = tmp
        except Exception as e:
            raise

    def __is_leap(self, y):
        """ 閏年チェック
              西暦年が4で割り切れる年は閏年
              ただし、西暦年が100で割り切れる年は平年
              ただし、西暦年が400で割り切れる年は閏年

        :param int y
        """
        leap = False
        try:
            if y % 4 == 0 and y % 100 != 0 or y % 400 == 0:
                leap = True
            return leap
        except Exception as e:
            raise

    def __gc2jd(self, year, month, day, hour=0, minute=0, second=0):
        """ グレゴリオ暦 -> ユリウス日

        :param  int   year
        :param  int  month
        :param  int    day
        :param  int   hour: optional
        :param  int minute: optional
        :param  int second: optional
        :return float   jd
        """
        try:
            # 1月,2月は前年の13月,14月とする
            if month < 3:
                year  -= 1
                month += 12
            # 日付(整数)部分計算
            jd  = int(365.25 * year) + year // 400 - year // 100 \
                + int(30.59 * (month - 2)) + day + 1721088.125
            # 時間(小数)部分計算
            t  = (second / 3600 + minute / 60 + hour) / 24
            return jd + t
        except Exception as e:
            raise

    def __jd2gc(self, jd):
        """ ユリウス日 -> グレゴリオ暦

        :param float jd
        :return list ut: [year, month, day, hour, minute, second]
        """
        ut = [0 for _ in range(6)]
        try:
            jd -= 0.125
            x0 = int(jd + 68570)
            x1 = x0 // 36524.25
            x2 = x0 - int(36524.25 * x1 + 0.75)
            x3 = (x2 + 1) // 365.2425
            x4 = x2 - int(365.25 * x3) + 31
            x5 = int(x4) // 30.59
            x6 = int(x5) // 11.0
            ut[2] = x4 - int(30.59 * x5)
            ut[1] = x5 - 12 * x6 + 2
            ut[0] = 100 * (x1 - 49) + x3 + x6
            # 2月30日の補正
            if ut[1] == 2 and ut[2] > 28:
                if ut[0] % 100 == 0 and ut[0] % 400 == 0:
                    ut[2] = 29
                elif ut[0] % 4 == 0:
                    ut[2] = 29
                else:
                    ut[2] = 28
            tm = 86400 * (jd - int(jd))
            ut[3] = tm // 3600.0
            ut[4] = (tm - 3600 * ut[3]) // 60.0
            ut[5] = tm - 3600 * ut[3] - 60 * ut[4]
            return map(lambda x: int(x), ut)
        except Exception as e:
            raise

    def __comp_kokei(self, jd):
        """ 太陽視黄経計算

        :param float jd
        :return list [kokei_sun, kokei_moon]
        """
        try:
            year, month, day, hour, minute, second \
                = self.__jd2gc(jd - self.JST_D)
            utc = datetime(year, month, day, hour, minute, second * 10 ** 6)
            o = apos.Apos(self.BIN_PATH, utc)
            kokei_sun  = o.sun()[1][0] * 180.0 / math.pi
            kokei_moon = o.moon()[1][0] * 180.0 / math.pi
            return [kokei_sun, kokei_moon]
        except Exception as e:
            raise

    def __del_dat_kokei(self, conn, year):
        """ DB DELETE

        :param MySQLdb conn
        :param int     year
        """
        try:
            sql = "DELETE FROM dat_kokeis WHERE gc_year = " + str(year)
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        except Exception as e:
            raise

    def __ins_dat_kokei(self, conn, data):
        """ DB INSERT

        :param MySQLdb conn
        :param list    data
        """
        try:
            sql = """
                INSERT INTO dat_kokeis (
                  gc_year, gc_month, gc_day, kokei_sun, kokei_moon
                ) VALUES 
            """
            sql += ",".join([
                "(" + ",".join(map(lambda x: str(x), row[0:3])) + "," \
                 + ",".join(map(lambda x: str(round(x, 8)), row[3:5])) + ")"
                for row in data
            ])
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplKokei()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

