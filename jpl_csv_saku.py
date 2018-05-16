#! /usr/local/bin/python3.6
"""
朔（新月）データ CSV 出力

  date          name            version
  2018.05.10    mk-mode.com     1.00 新規作成

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


class JplCsvSaku:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_csv_saku.py [YYYY [YYYY]]"
    FILE_CSV     = "saku.csv"
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
            passwd = self.PASSWORD
        )

    def exec(self):
        """ Execution """
        try:
            self.__write_csv(self.__get_data())
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

    def __get_data(self):
        """ データ取得

        :return list data
        """
        data = []
        try:
            sql = """
                SELECT gc_datetime
                  FROM dat_moons
                 WHERE diff_kokei = 0
              ORDER BY id
            """
            with self.con.cursor() as cur:
                cur.execute(sql)
                for row in cur.fetchall():
                    dt = list(
                        map(lambda x: int(x), re.split(r'\D', str(row[0])))
                    )
                    data.append(dt)
            return data
        except Exception as e:
            raise

    def __write_csv(self, data):
        """ CSV 出力

        :param list data
        """
        dir_csv  = os.path.dirname(os.path.abspath(__file__)) + "/csv"
        file_csv = "{}/{}".format(dir_csv, self.FILE_CSV)
        try:
            with open(file_csv, "w") as f:
                for row in data:
                    f.write(
                        "{:4d},{:2d},{:2d},{:2d},{:2d},{:2d}\n" \
                        .format(*row)
                    )
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = JplCsvSaku()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

