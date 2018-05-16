#! /usr/local/bin/python3.6
"""
雑節一覧

  date          name            version
  2018.05.06    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数: [西暦年(START) [西暦年(END)]]
        ( 西暦年(START, END)の範囲: 0000 - 9999 )
"""
import MySQLdb
import sys
import traceback
import time


class JplZassetsu:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_zassetsu.py [YYYY [YYYY]]"
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
                    # 以下の1行は 2099-12-31 で lambda_tomorrow = nil となるのを防ぐため
                    if year == 2099 and month == 12:
                        days -= 1
                    for day in range(1, days + 1):
                        jd = self.__gc2jd(year, month, day)
                        zassetsus = self.__comp_zassetsu(jd)
                        if zassetsus == []:
                            continue
                        print(
                            "* {:04d}-{:02d}-{:02d} - {}"
                            .format(
                                year, month, day,
                                ",".join(map(lambda x: str(x), zassetsus))
                            )
                        )
                        zassetsus += [99 for _ in range(2 - len(zassetsus))]
                        data.append([year, month, day, *zassetsus])
                if self.REG:
                    self.__del_dat_zassetsu(self.con, year)
                    self.__ins_dat_zassetsu(self.con, data)
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


    def __comp_zassetsu(self, jd):
        """ 雑節の計算

        :param  float     jd
        :return list zassets: [zassetsu_1, zassetsu_2]
        """
        zassetsu = []
        try:
            # 計算対象日の太陽の黄経
            lambda_today = self.__get_lambda(jd)
            # 計算対象日の翌日の太陽の黄経
            lambda_tomorrow = self.__get_lambda(jd + 1)
            # 計算対象日の5日前の太陽の黄経(社日計算用)
            lambda_before_5 = self.__get_lambda(jd - 5)
            # 計算対象日の4日前の太陽の黄経(社日計算用)
            lambda_before_4 = self.__get_lambda(jd - 4)
            # 計算対象日の5日後の太陽の黄経(社日計算用)
            lambda_after_5  = self.__get_lambda(jd + 5)
            # 計算対象日の6日後の太陽の黄経(社日計算用)
            lambda_after_6  = self.__get_lambda(jd + 6)
            # 太陽の黄経の整数部分( 土用, 入梅, 半夏生 計算用 )
            lambda_today0    = int(lambda_today)
            lambda_tomorrow0 = int(lambda_tomorrow)

            #### ここから各種雑節計算
            # 0:節分 ( 立春の前日 )
            if self.__get_sekki_24(jd + 1) == 315:  # 立春
                zassetsu.append(0)
            # 1:彼岸入（春） ( 春分の日の3日前 )
            if self.__get_sekki_24(jd + 3) == 0:    # 春分
                zassetsu.append(1)
            # 2:彼岸（春） ( 春分の日 )
            if self.__get_sekki_24(jd)     == 0:    # 春分
                zassetsu.append(2)
            # 3:彼岸明（春） ( 春分の日の3日後 )
            if self.__get_sekki_24(jd - 3) == 0:    # 春分
                zassetsu.append(3)
            # 4:社日（春） ( 春分の日に最も近い戊(つちのえ)の日 )
            # * 計算対象日が戊の日の時、
            #   * 4日後までもしくは4日前までに春分の日がある時、
            #       この日が社日
            #   * 5日後が春分の日の時、
            #       * 春分点(黄経0度)が午前なら
            #           この日が社日
            #       * 春分点(黄経0度)が午後なら
            #           この日の10日後が社日
            if int(jd % 10) == 4:  # 戊の日
                # [ 当日から4日後 ]
                for i in range(5):
                    if self.__get_sekki_24(jd + i) == 0:  # 春分
                        zassetsu.append(4)
                        break
                # [ 1日前から4日前 ]
                for i in range(1, 5):
                    if self.__get_sekki_24(jd - i) == 0:  # 春分
                        zassetsu.append(4)
                        break
                # [ 5日後 ]
                if self.__get_sekki_24(jd + 5)  == 0:  # 春分
                    # 春分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 0度(360度)以上なら、春分点が午前と判断
                    if (lambda_after_5 + lambda_after_6 + 360) / 2 >= 360:
                        zassetsu.append(4)
                # [ 5日前 ]
                if self.__get_sekki_24(jd - 5) == 0:  # 春分
                    # 春分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 0度(360度)未満なら、春分点が午後と判断
                    if (lambda_before_4 + lambda_before_5 + 360) / 2 < 360:
                        zassetsu.append(4)
            # 5:土用入（春） ( 黄経(太陽) = 27度 )
            if lambda_today0 != lambda_tomorrow0 and \
               lambda_tomorrow0 == 27:
                zassetsu.append(5)
            # 6:八十八夜 ( 立春から88日目(87日後) )
            if self.__get_sekki_24(jd - 87) == 315:  # 立春
                zassetsu.append(6)
            # 7:入梅 ( 黄経(太陽) = 80度 )
            if lambda_today0 != lambda_tomorrow0 and \
               lambda_tomorrow0 == 80:
                zassetsu.append(7)
            # 8:半夏生  ( 黄経(太陽) = 100度 )
            if lambda_today0 != lambda_tomorrow0 and \
               lambda_tomorrow0 == 100:
                zassetsu.append(8)
            # 9:土用入（夏） ( 黄経(太陽) = 117度 )
            if lambda_today0 != lambda_tomorrow0 and \
               lambda_tomorrow0 == 117:
                zassetsu.append(9)
            # 10:二百十日 ( 立春から210日目(209日後) )
            if self.__get_sekki_24(jd - 209) == 315:  # 立春
                zassetsu.append(10)
            # 11:二百二十日 ( 立春から220日目(219日後) )
            if self.__get_sekki_24(jd - 219) == 315:  # 立春
                zassetsu.append(11)
            # 12:彼岸入（秋） ( 秋分の日の3日前 )
            if self.__get_sekki_24(jd + 3)   == 180:  # 秋分
                zassetsu.append(12)
            # 13:彼岸（秋） ( 秋分の日 )
            if self.__get_sekki_24(jd)       == 180:  # 秋分
                zassetsu.append(13)
            # 14:彼岸明（秋） ( 秋分の日の3日後 )
            if self.__get_sekki_24(jd - 3)   == 180:  # 秋分
                zassetsu.append(14)
            # 15:社日（秋） ( 秋分の日に最も近い戊(つちのえ)の日 )
            # * 計算対象日が戊の日の時、
            #   * 4日後までもしくは4日前までに秋分の日がある時、
            #       この日が社日
            #   * 5日後が秋分の日の時、
            #       * 秋分点(黄経180度)が午前なら
            #           この日が社日
            #       * 秋分点(黄経180度)が午後なら
            #           この日の10日後が社日
            if int(jd % 10) == 4:  # 戊の日
                # [ 当日から4日後 ]
                for i in range(5):
                    if self.__get_sekki_24(jd + i) == 180:  # 秋分
                        zassetsu.append(15)
                        break
                # [ 1日前から4日前 ]
                for i in range(1, 5):
                    if self.__get_sekki_24(jd - i) == 180:  # 秋分
                        zassetsu.append(15)
                        break
                # [ 5日後 ]
                if self.__get_sekki_24(jd + 5) == 180:  # 秋分
                    # 秋分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 180度以上なら、秋分点が午前と判断
                    if (lambda_after_5 + lambda_after_6) / 2 >= 180:
                        zassetsu.append(15)
                # [ 5日前 ]
                if self.__get_sekki_24(jd - 5) == 180:  # 秋分
                    # 秋分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 180度未満なら、秋分点が午後と判断
                    if (lambda_before_4 + lambda_before_5) / 2 < 180:
                        zassetsu.append(15)
            # 16:土用入（秋） ( 黄経(太陽) = 207度 )
            if lambda_today0 != lambda_tomorrow0 and \
               lambda_tomorrow0 == 207:
                zassetsu.append(16)
            # 17:土用入（冬） ( 黄経(太陽) = 297度 )
            if lambda_today0 != lambda_tomorrow0 and\
               lambda_tomorrow0 == 297:
                zassetsu.append(17)
            return zassetsu
        except Exception as e:
            raise

    def __get_lambda(self, jd):
        """ 太陽視黄経取得

        :param  float        jd
        :return float kokei_sun
        """
        kokei_sun = 999
        try:
            year, month, day, hour, minute, second = self.__jd2gc(jd)
            sql = """
                SELECT kokei_sun
                  FROM dat_kokeis
                 WHERE gc_year  = {}
                   AND gc_month = {}
                   AND gc_day   = {}
            """.format(year, month, day)
            with self.con.cursor() as cur:
                cur.execute(sql)
                kokei_sun = cur.fetchone()[0]
            return kokei_sun
        except Exception as e:
            raise

    def __get_sekki_24(self, jd):
        """ 二十四節気取得

        :param  float     jd
        :return int sekki_24
        """
        try:
            year, month, day, hour, minute, second = self.__jd2gc(jd)
            sql = """
                SELECT kokei
                  FROM dat_sekki24s
                 WHERE gc_year  = {}
                   AND gc_month = {}
                   AND gc_day   = {}
            """.format(year, month, day)
            with self.con.cursor() as cur:
                cur.execute(sql)
                rs = cur.fetchone()
                sekki_24 = rs[0] if rs else 999
            return sekki_24
        except Exception as e:
            raise

    def __del_dat_zassetsu(self, con, year):
        """ DB DELETE

        :param MySQLdb con
        :param int    year
        """
        try:
            sql = "DELETE FROM dat_zassetsus WHERE gc_year = " + str(year)
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise

    def __ins_dat_zassetsu(self, con, data):
        """ DB INSERT

        :param MySQLdb con
        :param list   data
        """
        try:
            sql = """
                INSERT INTO dat_zassetsus (
                  gc_year, gc_month, gc_day, zassetsu_1, zassetsu_2
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
        obj = JplZassetsu()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

