#! /usr/local/bin/python3.6
"""
休日一覧

  date          name            version
  2018.05.06    mk-mode.com     1.00 新規作成
  2018.05.17    mk-mode.com     1.01 各休日に有効開始／終了年を設定

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数: [西暦年(START) [西暦年(END)]]
        ( 西暦年(START, END)の範囲: 0000 - 9999 )
"""
import MySQLdb
import sys
import traceback
import time
from lib import const as lcst


class JplHoliday:
    Y_MIN, Y_MAX = 1900, 2099  #0, 9999
    USAGE        = "[USAGE] ./jpl_holiday.py [YYYY [YYYY]]"
    JST_D        = 0.375
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
                print("*", year)
                if year < 1948:
                    continue
                # 変動の祝日の日付･曜日を計算 ( 振替休日,国民の休日を除く )
                holiday_0 = self.__comp_holiday_0(year)
                # 国民の休日計算
                holiday_1 = self.__comp_holiday_1(holiday_0)
                # 振替休日計算
                holiday_2 = self.__comp_holiday_2(holiday_0)
                data = sorted(holiday_0 + holiday_1 + holiday_2)
                if self.REG:
                    self.__del_dat_holiday(self.con, year)
                    self.__ins_dat_holiday(self.con, data)
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

    def __comp_holiday_0(self, year):
        """ 日付固定の祝日、変動の祝日の日付・曜日を計算
            * 施行日：1948-07-20

        :param  int year
        :return list
        """
        holidays = []
        try:
            for hid, month, day, kbn, year_s, year_e, name in lcst.HOLIDAY:
                if kbn > 7 or year < year_s or year > year_e:
                    continue
                if kbn == 0:  # 月日が既定のもの
                    jd = self.__gc2jd(year, month, day) + self.JST_D
                    yobi = self.__yobi(jd)
                    holidays.append([year, month, day, hid])
                else:         # 月日が不定のもの
                    if kbn == 2:    # 第2月曜日 ( 8 - 14 の月曜日)
                        for day_2 in range(8, 15):
                            jd = self.__gc2jd(year, month, day_2) + self.JST_D
                            yobi = self.__yobi(jd)
                            if yobi == 1:
                                holidays.append([year, month, day_2, hid])
                                break
                    elif kbn == 3:  # 第3月曜日 ( 15 - 21 の月曜日)
                        for day_2 in range(15, 22):
                            jd = self.__gc2jd(year, month, day_2) + self.JST_D
                            yobi = self.__yobi(jd)
                            if yobi == 1:
                                holidays.append([year, month, day_2, hid])
                                break
                    elif kbn == 4:  # 二分（春分、秋分）
                        day_2 = self.__get_last_nibun(year, month, 31)[2]
                        jd = self.__gc2jd(year, month, day_2) + self.JST_D
                        yobi = self.__yobi(jd)
                        holidays.append([year, month, day_2, hid])
            return holidays
        except Exception as e:
            raise

    def __comp_holiday_1(self, holiday_0):
        """ 国民の休日計算
            ( 「国民の祝日」で前後を挟まれた「国民の祝日」でない日 )
            ( 年またぎは考慮していない(今のところ不要) )
            * 施行日：1985-12-27

        :param  list holiday_0: 変動の祝日の日付／曜日
        :return list
        """
        holidays = []
        try:
            y_min = [h[4] for h in lcst.HOLIDAY if h[0] == 90][0]
            if holiday_0[0][0] < y_min:
                return []
            for i in range(len(holiday_0) - 1):
                y_0, m_0, d_0 = holiday_0[i    ][0:3]
                y_1, m_1, d_1 = holiday_0[i + 1][0:3]
                jd_0 = self.__gc2jd(y_0, m_0, d_0)
                jd_1 = self.__gc2jd(y_1, m_1, d_1)
                if jd_0 + 2 == jd_1:
                    jd = jd_0 + 1
                    yobi = self.__yobi(jd)
                    y, m, d = self.__jd2gc(jd)[0:3]
                    holidays.append([y, m, d, 90])
            return holidays
        except Exception as e:
            raise

    def __comp_holiday_2(self, holiday_0):
        """ 振替休日計算
            ( 「国民の祝日」が日曜日に当たるときは、
              その日後においてその日に最も近い「国民の祝日」でない日 )
            * 施行日：1973-04-12

        :param  list holiday_0: 変動の祝日の日付／曜日
        :return list
        """
        holidays = []
        try:
            y_min = [h[4] for h in lcst.HOLIDAY if h[0] == 91][0]
            if holiday_0[0][0] < y_min:
                return []
            for i in range(len(holiday_0)):
                y, m, d = holiday_0[i][0:3]
                if y == 1973:
                    if m < 4 or (m == 4 and d < 12):
                        continue
                jd = self.__gc2jd(y, m, d)
                yobi = self.__yobi(jd)
                if yobi != 0:
                    continue
                next_jd = jd + 1
                next_yobi = self.__yobi(next_jd)
                if i == len(holiday_0) - 1:
                    next_y, next_m, next_d = self.__jd2gc(next_jd)[0:3]
                    holidays.append([next_y, next_m, next_d, 91])
                else:
                    flg_furikae = 0
                    plus_day = 1
                    while flg_furikae == 0:
                        if i + plus_day < len(holiday_0):
                            plus_y, plus_m, plus_d \
                                = holiday_0[i + plus_day][0:3]
                            plus_jd = self.__gc2jd(plus_y, plus_m, plus_d)
                            if next_jd == plus_jd:
                                next_jd += 1
                                next_yobi = 0 \
                                    if next_yobi == 6 else next_yobi + 1
                                plus_day += 1
                            else:
                                flg_furikae = 1
                                next_y, next_m, next_d \
                                    = self.__jd2gc(next_jd)[0:3]
                                holidays.append(
                                    [next_y, next_m, next_d, 91]
                                )
            return holidays
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

    def __yobi(self, jd):
        """ 曜日計算

        :param  float jd
        :return int
        """
        try:
            return (int(jd) + 2) % 7
        except Exception as e:
            raise

    def __get_last_nibun(self, year, month, day):
        """ 直近の二分（春分、秋分）取得

        :param  int  year
        :param  int month
        :param  int   day
        :return list     : [year, month, day]
        """
        try:
            datetime = "{:04d}-{:02d}-{:02d} 00:00:00".format(year, month, day)
            kokei = 0 if month == 3 else 180
            sql = """
                SELECT gc_year, gc_month, gc_day
                  FROM dat_sekki24s
                 WHERE kokei = {}
                   AND gc_datetime < '{}'
              ORDER BY gc_year DESC, gc_month DESC, gc_day DESC
                 LIMIT 1
            """.format(kokei, datetime)
            with self.con.cursor() as cur:
                cur.execute(sql)
                rs = cur.fetchone()
                last_nibun = rs if rs else []
            return last_nibun
        except Exception as e:
            raise

    def __del_dat_holiday(self, con, year):
        """ DB DELETE

        :param MySQLdb con
        :param int    year
        """
        try:
            sql = "DELETE FROM dat_holidays WHERE gc_year = " + str(year)
            with con.cursor() as cur:
                cur.execute(sql)
            con.commit()
        except Exception as e:
            raise

    def __ins_dat_holiday(self, con, data):
        """ DB INSERT

        :param MySQLdb con
        :param list   data
        """
        try:
            sql = """
                INSERT INTO dat_holidays (
                  gc_year, gc_month, gc_day, holiday
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
        obj = JplHoliday()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

