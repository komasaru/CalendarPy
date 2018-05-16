#! /usr/local/bin/python3.6
"""
朔望一覧

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
import time
from datetime import datetime
from datetime import timedelta
from lib import apos


class JplMoon:
    BIN_PATH     = "/home/masaru/src/calendar_py/JPLEPH"
    Y_MIN, Y_MAX = 1899, 2100  #0, 9999
    USAGE        = "[USAGE] ./jpl_sekki_24.py [YYYY [YYYY]]"
    LOOP_LIMIT   = 50
    EPS          = 0.1  # unit: second
    DATABASE     = "calendar"
    HOSTNAME     = "127.0.0.1"
    USERNAME     = "******"
    PASSWORD     = "**********"
    REG          = False  # DB 登録も行う場合は True

    def __init__(self):
        self.__get_arg()

    def exec(self):
        """ Execution """
        data = []
        try:
            time_l  = datetime(self.year_s, 1, 1, 0, 0, 0)
            time_h = time_l + timedelta(days=10)
            lmds = self.__comp_lambda(time_l - timedelta(hours=9))
            kokei_sun, kokei_moon = lmds
            diff = kokei_moon - kokei_sun
            if diff < 0.0:
                diff += 360.0
            target = (diff // 90) * 90 + 90
            if target == 360.0:
                target = 0.0
            while True:
                time_x = self.__bisection(
                    time_l - timedelta(hours=9),
                    time_h - timedelta(hours=9),
                    target
                ) + timedelta(hours=9)
                if time_x.year > self.year_e:
                    break
                str_jst = time_x.strftime("%Y-%m-%d %H:%M:%S")
                print(
                    "* {:04d}:{:3d} - {}"
                    .format(time_x.year, int(target), str_jst)
                )
                data.append([
                    time_x.year, time_x.month, time_x.day,
                    int(target), str_jst
                ])
                time_l = time_x
                time_h = time_l + timedelta(days=10)
                target += 90.0
                if target == 360.0:
                    target = 0.0
            if self.REG:
                conn = self.__db_connect()
                for year in range(self.year_s, self.year_e + 1):
                    self.__del_dat_moon(conn, year)
                self.__ins_dat_moon(conn, data)
                conn.close()
        except Exception as e:
            raise

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

    def __bisection(self, time_l, time_h, target):
        """ Bisection method

        :param  datetime time_l
        :param  datetime time_h
        :param  float   sekki_x
        :return datetime time_x
        """
        time_x = None
        try:
            t_l = time.mktime(time_l.timetuple()) \
                + time_l.microsecond * 1e-6
            t_h = time.mktime(time_h.timetuple()) \
                + time_h.microsecond * 1e-6
            for _ in range(self.LOOP_LIMIT):
                time_x = datetime.fromtimestamp((t_l + t_h) / 2)
                lmd_sun, lmd_moon = self.__comp_lambda(time_x)
                diff_x = lmd_moon - lmd_sun
                if diff_x < 0.0:
                    diff_x += 360
                if diff_x > target:
                    if diff_x - target < 90.0:
                        time_h = time_x
                    else:
                        time_l = time_x
                else:
                    if diff_x - target < 90.0:
                        time_l = time_x
                    else:
                        time_h = time_x
                if diff_x == target:
                    break
                t_l = time.mktime(time_l.timetuple()) \
                    + time_l.microsecond * 1e-6
                t_h = time.mktime(time_h.timetuple()) \
                    + time_h.microsecond * 1e-6
                if t_h - t_l < self.EPS:
                    break
            return time_x
        except Exception as e:
            raise

    def __comp_lambda(self, tm):
        """ 太陽視黄経計算

        :param float jd
        :return list [kokei_sun, kokei_moon]
        """
        try:
            o = apos.Apos(self.BIN_PATH, tm)
            lambda_sun  = o.sun()[1][0] * 180.0 / math.pi
            lambda_moon = o.moon()[1][0] * 180.0 / math.pi
            return [lambda_sun, lambda_moon]
        except Exception as e:
            raise

    def __db_connect(self):
        """ Establishment of DB connection """
        try:
            return MySQLdb.connect(
                db     = self.DATABASE,
                host   = self.HOSTNAME,
                user   = self.USERNAME,
                passwd = self.PASSWORD
            )
        except Exception as e:
            raise

    def __del_dat_moon(self, conn, year):
        """ DB DELETE

        :param MySQLdb conn
        :param int     year
        """
        try:
            sql = "DELETE FROM dat_moons WHERE gc_year = " + str(year)
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        except Exception as e:
            raise

    def __ins_dat_moon(self, conn, data):
        """ DB INSERT

        :param MySQLdb conn
        :param list    data
        """
        try:
            sql = """
                INSERT INTO dat_moons (
                  gc_year, gc_month, gc_day, diff_kokei, gc_datetime
                ) VALUES 
            """
            sql += ",".join([
                "(" + ",".join(map(lambda x: str(x), row[0:3])) + "," \
                + str(round(row[3], 8)) + ", '" + row[4] + "')"
                for row in data
            ])
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplMoon()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

