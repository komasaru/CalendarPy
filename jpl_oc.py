#! /usr/local/bin/python3.6
"""
旧暦一覧

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


class JplOc:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_oc.py [YYYY [YYYY]]"
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
                        jd = self.__gc2jd(year, month, day)
                        res = self.__comp_oc(year, month, day)
                        oc_year, oc_leap, oc_month, oc_day, rokuyo = res
                        print((
                            "* {:04d}-{:02d}-{:02d} "
                            "- {:04d}, {:1d}, {:02d}, {:02d}, {:1d}"
                        ).format(
                            year, month, day,
                            oc_year, oc_leap, oc_month, oc_day, rokuyo
                        ))
                        data.append([
                            year, month, day,
                            oc_year, oc_leap, oc_month, oc_day, rokuyo
                        ])
                if self.REG:
                    self.__del_dat_old_calendar(self.con, year)
                    self.__ins_dat_old_calendar(self.con, data)
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

    def __comp_oc(self, year, month, day):
        """ 旧暦計算

        :param  int  year
        :param  int month
        :param  int   day
        :return list oc: [year, leap, month, day, rokuyo]
        """
        chu, saku = [], []
        m = [[0 for _ in range(3)] for _ in range(5)]
        oc = [0 for _ in range(5)]
        try:
            jd = self.__gc2jd(year, month, day)
            # 計算対象の直前にあたる二分二至の時刻を計算
            res = self.__last_nibun(year, month, day)
            chu.append([self.__gc2jd(*res[0]), res[1]])
            # 中気の時刻を計算 ( 3回計算する )
            for i in range(1, 4):
                res = self.__last_chu(*self.__jd2gc(chu[i - 1][0] + 32))
                chu.append([self.__gc2jd(*res[0]), res[1]])
            # 計算対象の直前にあたる二分二至の直前の朔の時刻を求める
            saku.append(
                self.__gc2jd(
                    *self.__last_saku(*self.__jd2gc(chu[0][0]))
                ) - 0.125
            )
            # 朔の時刻を求める
            for i in range(1, 5):
                jd_saku = saku[i - 1] + 30
                saku.append(
                    self.__gc2jd(*self.__last_saku(*self.__jd2gc(jd_saku))) - 0.125
                )
                # 前と同じ時刻を計算した場合( 両者の差が26日以内 )には、初期値を
                # +33日にして再実行させる。
                if abs(int(saku[i - 1]) - int(saku[i])) <= 26:
                    saku[i] = self.__gc2jd(
                        *self.__last_saku(*self.__jd2gc(saku[i - 1] + 35))
                    ) - 0.125
            # saku[1]が二分二至の時刻以前になってしまった場合には、朔をさかのぼり過ぎ
            # たと考えて、朔の時刻を繰り下げて修正する。
            # その際、計算もれ（saku[4]）になっている部分を補うため、朔の時刻を計算
            # する。（近日点通過の近辺で朔があると起こる事があるようだ...？）
            if int(saku[1]) <= int(chu[0][0]):
                for i in range(4):
                    saku[i] = saku[i + 1]
                saku[4] = self.__gc2jd(
                    *self.__last_saku(*self.__jd2gc(saku[3] + 35))
                ) - 0.125
            # saku[0]が二分二至の時刻以後になってしまった場合には、朔をさかのぼり足
            # りないと見て、朔の時刻を繰り上げて修正する。
            # その際、計算もれ（saku[0]）になっている部分を補うため、朔の時刻を計算
            # する。（春分点の近辺で朔があると起こる事があるようだ...？）
            elif int(saku[0]) > int(chu[0][0]):
                for i in range(4, 0, -1):
                    saku[i] = saku[i - 1]
                saku[0] = self.__gc2jd(
                    *self.__last_saku(*self.__jd2gc(saku[0] + 27))
                ) - 0.125
            # 閏月検索Flagセット
            # （節月で４ヶ月の間に朔が５回あると、閏月がある可能性がある。）
            # leap=0:平月  leap=1:閏月
            leap = 0
            if int(saku[4]) <= int(chu[3][0]):
                leap = 1
            # 朔日行列の作成
            # m[i][0] ... 月名 ( 1:正月 2:２月 3:３月 .... )
            # m[i][1] ... 閏フラグ ( 0:平月 1:閏月 )
            # m[i][2] ... 朔日のjd
            m[0][0] = (chu[0][1] // 30) + 2
            if m[0][0] > 12:
                m[0][0] -= 12
            m[0][2] = int(saku[0])
            m[0][1] = 0
            for i in range(1, 5):
                if leap == 1 and i != 1:
                    if int(chu[i - 1][0]) <= int(saku[i - 1]) or \
                       int(chu[i - 1][0]) >= int(saku[i]):
                        m[i - 1][0] = m[i-2][0]
                        m[i - 1][1] = 1
                        m[i - 1][2] = int(saku[i - 1])
                        leap = 0
                m[i][0] = m[i - 1][0] + 1
                if m[i][0] > 12:
                    m[i][0] -= 12
                m[i][2] = int(saku[i])
                m[i][1] = 0
            # 朔日行列から旧暦を求める。
            state, index = 0, 0
            for i in range(5):
                index = i
                if int(jd) < int(m[i][2]):
                    state = 1
                    break
                elif int(jd) == int(m[i][2]):
                    state = 2
                    break
            if state == 1:
                index -= 1
            oc[1] = m[index][1]
            oc[2] = m[index][0]
            oc[3] = int(jd) - int(m[index][2]) + 1
            # 旧暦年の計算
            # （旧暦月が10以上でかつ新暦月より大きい場合には、
            #   まだ年を越していないはず...）
            a = self.__jd2gc(jd)
            oc[0] = a[0]
            if oc[2] > 9 and oc[2] > a[1]:
                oc[0] -= 1
            # 六曜
            oc[4] = (oc[2] + oc[3]) % 6
            return oc
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
            return list(map(lambda x: int(x), ut))
        except Exception as e:
            raise

    def __last_nibun(self, year, month, day, hour=0, minute=0, second=0):
        """ 直近の二分ニ至（春分、秋分、夏至、冬至）取得

        :param  MySQLdb con
        :param  int    year
        :param  int   month
        :param  int     day
        :param  int    hour: optional
        :param  int  minute: optional
        :param  int  second: optional
        :return list last_nibun: [int kokei, string gc_datetime]
        """
        try:
            datetime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                year, month, day, hour, minute, second
            )
            sql = """
                SELECT kokei, gc_datetime
                  FROM dat_sekki24s
                 WHERE MOD(kokei, 90) = 0
                   AND gc_datetime < '{}'
              ORDER BY gc_datetime DESC
                 LIMIT 1
            """.format(datetime)
            with self.con.cursor() as cur:
                cur.execute(sql)
                rs = cur.fetchone()
                last_nibun = rs if rs else [0, "0000-00-00 00:00:00"]
                last_nibun = [
                    list(map(
                        lambda x: int(x), re.split(r'\D', str(last_nibun[1]))
                    )), last_nibun[0]
                ]
            return last_nibun
        except Exception as e:
            raise

    def __last_chu(self, year, month, day, hour=0, minute=0, second=0):
        """ 直近の中気取得

        :param  MySQLdb con
        :param  int    year
        :param  int   month
        :param  int     day
        :param  int    hour: optional
        :param  int  minute: optional
        :param  int  second: optional
        :return list last_chu: [int kokei, string gc_datetime]
        """
        try:
            datetime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                year, month, day, hour, minute, second
            )
            sql = """
                SELECT kokei, gc_datetime
                  FROM dat_sekki24s
                 WHERE MOD(kokei, 30) = 0
                   AND gc_datetime < '{}'
              ORDER BY gc_datetime DESC
                 LIMIT 1
            """.format(datetime)
            with self.con.cursor() as cur:
                cur.execute(sql)
                rs = cur.fetchone()
                last_chu = rs if rs else [0, "0000-00-00 00:00:00"]
                last_chu = [
                    list(map(
                        lambda x: int(x), re.split(r'\D', str(last_chu[1]))
                    )), last_chu[0]
                ]
            return last_chu
        except Exception as e:
            raise

    def __last_saku(self, year, month, day, hour=0, minute=0, second=0):
        """ 直近の朔取得

        :param  MySQLdb con
        :param  int    year
        :param  int   month
        :param  int     day
        :param  int    hour: optional
        :param  int  minute: optional
        :param  int  second: optional
        :return float last_saku
        """
        try:
            datetime = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
                year, month, day, hour, minute, second
            )
            sql = """
                SELECT gc_datetime
                  FROM dat_moons
                 WHERE diff_kokei = 0
                   AND gc_datetime < '{}'
              ORDER BY gc_datetime DESC
                 LIMIT 1
            """.format(datetime)
            with self.con.cursor() as cur:
                cur.execute(sql)
                rs = cur.fetchone()
                last_saku = rs[0] if rs else "0000-00-00 00:00:00"
                last_saku = list(
                    map(lambda x: int(x), re.split(r'\D', str(last_saku)))
                )
            return last_saku
        except Exception as e:
            raise

    def __del_dat_old_calendar(self, con, year):
        """ DB DELETE

        :param MySQLdb con
        :param int    year
        """
        try:
            sql = "DELETE FROM dat_old_calendars WHERE gc_year = " + str(year)
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise

    def __ins_dat_old_calendar(self, con, data):
        """ DB INSERT

        :param MySQLdb con
        :param list   data
        """
        try:
            sql = """
                INSERT INTO dat_old_calendars (
                  gc_year, gc_month, gc_day,
                  oc_year, oc_leap, oc_month, oc_day, rokuyo
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
        obj = JplOc()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

