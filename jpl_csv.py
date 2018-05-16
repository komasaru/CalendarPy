#! /usr/local/bin/python3.6
"""
カレンダーデータ CSV 出力

  date          name            version
  2018.05.07    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数: [西暦年(START) [西暦年(END)]]
        ( 西暦年(START, END)の範囲: 0000 - 9999 )
"""
import MySQLdb
import os
import re
import sys
import traceback
import time


class JplCsv:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_csv.py [YYYY [YYYY]]"
    DATABASE     = "calendar"
    HOSTNAME     = "127.0.0.1"
    USERNAME     = "******"
    PASSWORD     = "**********"

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
            self.__gen_kanshi()
            for year in range(self.year_s, self.year_e + 1):
                print("*", year)
                data = self.__get_data(year)
                self.__write_csv(year, data)
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

    def __gen_kanshi(self):
        """ 干支一覧生成 """
        self.kanshis = []
        try:
            kans = self.__get_kanshi(0) * 6
            shis = self.__get_kanshi(1) * 5
            for k, s in zip(kans, shis):
                self.kanshis.append(str(k) + str(s))
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
                SELECT d.gc_year, d.gc_month, d.gc_day,
                       m_y.name, IFNULL(m_h.name, ''),
                       jd, kokei_sun, kokei_moon, moon_age,
                       oc_year, oc_leap, oc_month, oc_day, m_r.name,
                       kanshi, IFNULL(m_s_1.name, ''), IFNULL(m_s_2.name, ''),
                       IFNULL(m_z_1.name, ''), IFNULL(m_z_2.name, '')
                  FROM (SELECT gc_year, gc_month, gc_day, jd, yobi, holiday,
                               kokei_sun, kokei_moon, moon_age,
                               oc_year, oc_leap, oc_month, oc_day, rokuyo,
                               kanshi, sekki_24, zassetsu_1, zassetsu_2, sekku
                          FROM dat_calendars
                         WHERE gc_year = {}) AS d
                       INNER JOIN
                       (SELECT code, name
                          FROM mst_yobis) AS m_y
                       ON d.yobi = m_y.code
                       LEFT OUTER JOIN
                       (SELECT code, name
                          FROM mst_holidays) AS m_h
                       ON d.holiday = m_h.code
                       INNER JOIN
                       (SELECT code, name
                          FROM mst_rokuyos) AS m_r
                       ON d.rokuyo = m_r.code
                       LEFT OUTER JOIN
                       (SELECT kokei, name
                          FROM mst_sekki24s) AS m_s_1
                       ON d.sekki_24 = m_s_1.kokei
                       LEFT OUTER JOIN
                       (SELECT code, name
                          FROM mst_zassetsus) AS m_z_1
                       ON d.zassetsu_1 = m_z_1.code
                       LEFT OUTER JOIN
                       (SELECT code, name
                          FROM mst_zassetsus) AS m_z_2
                       ON d.zassetsu_2 = m_z_2.code
                       LEFT OUTER JOIN
                       (SELECT code, name
                          FROM mst_sekkus) AS m_s_2
                       ON d.sekku = m_s_2.code
            """.format(year)
            with self.con.cursor() as cur:
                cur.execute(sql)
                for row in cur.fetchall():
                    zassetsu = row[17]
                    if row[18] != "":
                        zassetsu += "・" + row[18]
                    data.append([
                        row[0], row[1], row[2], row[3], row[4],
                        "{:.3f}".format(float(row[5])),
                        "{:.8f}".format(float(row[6])),
                        "{:.8f}".format(float(row[7])),
                        "{:.8f}".format(float(row[8])),
                        row[9], row[10], row[11], row[12], row[13],
                        self.kanshis[row[14]], row[15], row[16], zassetsu
                    ])
            return data
        except Exception as e:
            raise

    def __get_kanshi(self, kbn):
        """ 干支一覧取得

        :param  int   kbn
        :return list data
        """
        data = []
        try:
            sql ="""
                SELECT name
                  FROM mst_kanshis
                 WHERE kbn = {}
              ORDER BY id
            """.format(str(kbn))
            with self.con.cursor() as cur:
                cur.execute(sql)
                for row in cur.fetchall():
                    data.append(row[0])
            return data
        except Exception as e:
            raise

    def __write_csv(self, year, data):
        """ CSV 出力

        :param int  year
        :param list data
        """
        dir_csv  = os.path.dirname(os.path.abspath(__file__)) + "/csv"
        file_csv = "{}/{}.csv".format(dir_csv, year)
        try:
            head = (
                "年,月,日,曜日,休日,ユリウス通日,黄経/太陽,黄経/月,月齢,"
                "旧暦/年,旧暦/閏月FLAG,旧暦/月,旧暦/日,六曜,"
                "干支(日),二十四節気,節句,雑節\n"
            )
            with open(file_csv, "w") as f:
                f.write(head)
                for row in data:
                    row[-1] = re.sub(',', "・", row[-1])  # 雑節複数対応
                    f.write(",".join(map(lambda x: str(x), row)) + "\n")
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplCsv()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

