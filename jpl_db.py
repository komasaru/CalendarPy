#! /usr/local/bin/python3.6
"""
カレンダーデータ DB 登録
: 各種データを統合して dat_calendars テーブルへ登録する

  date          name            version
  2018.05.07    mk-mode.com     1.00 新規作成

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


class JplDb:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_db.py [YYYY [YYYY]]"
    SEKKU        = ["人日", "上巳", "端午", "七夕", "重陽"]
    DATABASE     = "calendar"
    HOSTNAME     = "127.0.0.1"
    USERNAME     = "masaru"
    PASSWORD     = "MkMk*/7621"
    REG          = False  # DB 登録も行う場合は True

    def __init__(self):
        self.__get_arg()
        self.con = MySQLdb.connect(
            db     = self.DATABASE,
            host   = self.HOSTNAME,
            user   = self.USERNAME,
            passwd = self.PASSWORD,
            charset = "utf8"  # 日本語対応
        )

    def exec(self):
        """ Execution """
        try:
            for year in range(self.year_s, self.year_e + 1):
                print("*", str(year))
                data = self.__get_data(year)
                if self.REG:
                    self.__del_dat_calendar(self.con, year)
                    self.__ins_dat_calendar(self.con, data)
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

    def __get_data(self, year):
        """ データ取得

        :param  int  year
        :return list data
        """
        data = []
        try:
            sql = """
                SELECT e.gc_year, e.gc_month, e.gc_day,
                       e.jd, e.yobi, IFNULL(h.holiday, 99),
                       k.kokei_sun, k.kokei_moon, e.moon_age,
                       o.oc_year, o.oc_leap, o.oc_month, o.oc_day, o.rokuyo,
                       e.kanshi, IFNULL(s.kokei, 999),
                       IFNULL(z.zassetsu_1, 99), IFNULL(z.zassetsu_2, 99),
                       IFNULL(m_s.name, '')
                  FROM (SELECT gc_year, gc_month, gc_day,
                               jd, yobi, kanshi, moon_age
                          FROM dat_etcs
                         WHERE gc_year = {}) AS e
                       INNER JOIN
                       (SELECT gc_year, gc_month, gc_day,
                               oc_year, oc_leap, oc_month, oc_day, rokuyo
                          FROM dat_old_calendars
                         WHERE gc_year = {}) AS o
                       ON e.gc_year  = o.gc_year  AND
                          e.gc_month = o.gc_month AND
                          e.gc_day   = o.gc_day
                       INNER JOIN
                       (SELECT gc_year, gc_month, gc_day,
                               kokei_sun, kokei_moon
                          FROM dat_kokeis
                         WHERE gc_year = {}) AS k
                       ON e.gc_year  = k.gc_year  AND
                          e.gc_month = k.gc_month AND
                          e.gc_day   = k.gc_day
                       LEFT OUTER JOIN
                       (SELECT gc_year, gc_month, gc_day,
                               kokei
                          FROM dat_sekki24s
                         WHERE gc_year = {}) AS s
                       ON e.gc_year  = s.gc_year  AND
                          e.gc_month = s.gc_month AND
                          e.gc_day   = s.gc_day
                       LEFT OUTER JOIN
                       (SELECT gc_year, gc_month, gc_day,
                               holiday
                          FROM dat_holidays
                         WHERE gc_year = {}) AS h
                       ON e.gc_year  = h.gc_year  AND
                          e.gc_month = h.gc_month AND
                          e.gc_day   = h.gc_day
                       LEFT OUTER JOIN
                       (SELECT gc_year, gc_month, gc_day,
                               zassetsu_1, zassetsu_2
                          FROM dat_zassetsus
                         WHERE gc_year = {}) AS z
                       ON e.gc_year  = z.gc_year  AND
                          e.gc_month = z.gc_month AND
                          e.gc_day   = z.gc_day
                       LEFT OUTER JOIN
                       (SELECT gc_month, gc_day,
                               name
                          FROM mst_sekkus) AS m_s
                       ON e.gc_month = m_s.gc_month AND
                          e.gc_day   = m_s.gc_day
            """.format(year, year, year, year, year, year)
            with self.con.cursor() as cur:
                cur.execute(sql)
                for row in cur.fetchall():
                    sekku = 9 if row[18] == "" else self.SEKKU.index(row[18])
                    data.append([
                        row[0], row[1], row[2], float(row[3]), row[4],
                        row[5], float(row[6]), float(row[7]), float(row[8]),
                        row[9], row[10], row[11], row[12], row[13],
                        row[14],row[15], row[16], row[17], sekku
                    ])
            return data
        except Exception as e:
            raise

    def __del_dat_calendar(self, con, year):
        """ DB DELETE

        :param MySQLdb con
        :param int    year
        """
        try:
            sql = "DELETE FROM dat_calendars WHERE gc_year = " + str(year)
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise

    def __ins_dat_calendar(self, con, data):
        """ DB INSERT

        :param MySQLdb con
        :param list   data
        """
        try:
            sql = """
                INSERT INTO dat_calendars (
                  gc_year, gc_month, gc_day, jd, yobi, holiday,
                  kokei_sun, kokei_moon, moon_age,
                  oc_year, oc_leap, oc_month, oc_day, rokuyo,
                  kanshi, sekki_24, zassetsu_1, zassetsu_2, sekku
                ) VALUES 
            """
            sql += ",".join([
                "(" + ",".join(map(lambda x: str(x), row)) + ")"
                for row in data
            ])
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplDb()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

