#! /usr/local/bin/python3.6
"""
その他（曜日、JD、月齢、干支、節句）一覧

  date          name            version
  2018.05.06    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数: [西暦年(START) [西暦年(END)]]
        ( 西暦年(START, END)の範囲: 0000 - 9999 )
"""
import MySQLdb
import re
import sys
import traceback
import time


class JplZassetsu:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_etc.py [YYYY [YYYY]]"
    DAYS         = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    DATABASE     = "calendar"
    HOSTNAME     = "127.0.0.1"
    USERNAME     = "******"
    PASSWORD     = "**********"
    REG          = False  # DB 登録も行う場合は True

    def __init__(self):
        self.__get_arg()
        self.con = MySQLdb.connect(
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
                        jd       = self.__gc2jd(year, month, day)
                        yobi     = self.__yobi(int(jd))
                        kanshi   = self.__kanshi(int(jd))
                        moon_age = self.__moon_age(self.con, year, month, day)
                        print((
                            "* {:04d}-{:02d}-{:02d} "
                            "- {:11.3f}, {:1d}, {:2d}, {:11.8f}"
                        ).format(
                            year, month, day, jd, yobi, kanshi, moon_age
                        ))
                        data.append(
                            [year, month, day, jd, yobi, kanshi, moon_age]
                        )
                if self.REG:
                    self.__del_dat_etc(self.con, year)
                    self.__ins_dat_etc(self.con, data)
        except Exception as e:
            raise
        finally:
            self.con.close()

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

    def __yobi(self, jd):
        """ 曜日計算

        :param  float jd
        :return int
        """
        try:
            return (int(jd) + 2) % 7
        except Exception as e:
            raise

    def __kanshi(self, jd):
        """ 干支計算

        :param  float jd
        :return int
        """
        try:
            return (int(jd) - 10) % 60
        except Exception as e:
            raise

    def __moon_age(self, con, year, month, day):
        """ 月齢計算

        :param  MySQLdb con
        :param  int    year
        :param  int   month
        :param  int     day
        :return float
        """
        try:
            jd = self.__gc2jd(year, month, day, 12)
            datetime = "{:04d}-{:02d}-{:02d} 12:00:00".format(year, month, day)
            sql = """
                SELECT gc_datetime
                  FROM dat_moons
                 WHERE diff_kokei = 0
                   AND gc_datetime < '{}'
              ORDER BY gc_datetime DESC
                 LIMIT 1
            """.format(datetime)
            with con.cursor() as cur:
                cur.execute(sql)
                rs = cur.fetchone()
                saku = rs[0] if rs else "0000-00-00 00:00:00"
                saku = list(map(lambda x: int(x), re.split(r'\D', str(saku))))
            return jd - self.__gc2jd(*saku)
        except Exception as e:
            raise

    def __del_dat_etc(self, con, year):
        """ DB DELETE

        :param MySQLdb con
        :param int    year
        """
        try:
            sql = "DELETE FROM dat_etcs WHERE gc_year = " + str(year)
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise

    def __ins_dat_etc(self, con, data):
        """ DB INSERT

        :param MySQLdb con
        :param list   data
        """
        try:
            sql = """
                INSERT INTO dat_etcs (
                  gc_year, gc_month, gc_day, jd, yobi, kanshi, moon_age
                ) VALUES 
            """
            sql += ",".join([
                "(" \
                + ",".join(map(lambda x: str(x), row[0:3])) \
                + "," + str(round(row[3], 3)) + "," \
                + ",".join(map(lambda x: str(x), row[4:6])) \
                + "," + str(round(row[6] ,8)) + ")"
                for row in data
            ])
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplZassetsu()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

