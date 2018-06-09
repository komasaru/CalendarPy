"""
Class for calendar.
"""
from datetime import datetime
from datetime import timedelta
import math
import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import apos           as lapos
import const          as lcst
import const_saku     as lsak
import const_sekki_24 as ls24
import time_          as ltm


class Calendar:
    def __init__(self, bin_path, jst):
        """ Initialization

        :param string file_bin: バイナリファイルのフルパス
        :param datetime    jst: JST（日本標準時）
        """
        self.bin_path = bin_path
        self.jst    = jst
        self.utc    = jst - timedelta(hours=9)
        self.year   = jst.year
        self.month  = jst.month
        self.day    = jst.day
        self.jd     = ltm.gc2jd(self.utc)
        self.jd_jst = self.jd + lcst.JST_D

    def yobi(self, jst=None):
        """ 曜日計算
            * datetime の weekday() 関数は使用しない

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 曜日の文字（"日" - "土"）
        """
        try:
            jd = ltm.gc2jd(jst) if jst else self.jd_jst
            code = self.__yobi(jd)
            return lcst.YOBI[code]
        except Exception as e:
            raise

    def holiday(self, jst=None):
        """ 休日計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 休日の文字列
        """
        try:
            if jst is None:
                jst = self.jst
            code = self.__holiday(jst)
            res = [row[6] for row in lcst.HOLIDAY if row[0] == code]
            return res[0] if res else ""
        except Exception as e:
            raise

    def holiday_year(self, jst=None):
        """ 年間休日一覧計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 休日の文字列
        """
        holidays = []
        try:
            if jst is None:
                jst = self.jst
            data = self.__holiday_year(jst.year)
            for d in data:
                s = ""
                res = [h[6] for h in lcst.HOLIDAY if d[3] == h[0]]
                if res:
                    s = res[0]
                holidays.append([d[0], d[1], d[2], s])
            return holidays
        except Exception as e:
            raise

    def kanshi(self, jst=None):
        """ 干支計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 干支の文字列
        """
        try:
            jd = ltm.gc2jd(jst) if jst else self.jd_jst
            code = self.__kanshi(jd)
            return lcst.KANSHI[code]
        except Exception as e:
            raise

    def sekki_24(self, jst=None):
        """ 二十四節気計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 二十四節気の文字列
        """
        try:
            if jst is None:
                jst = self.jst
            deg = self.__sekki_24(jst)
            return "" if deg == 999 else lcst.SEKKI_24[deg // 15]
        except Exception as e:
            raise

    def sekku(self, jst=None):
        """ 節句計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 節句の文字列
        """
        try:
            if jst is None:
                jst = self.jst
            code = self.__sekku(jst)
            return "" if code == 9 else lcst.SEKKU[code][-1]
        except Exception as e:
            raise

    def zassetsu(self, jst=None):
        """ 雑節計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return string      : 雑節の文字列
        """
        try:
            if jst is None:
                jst = self.jst
            codes = self.__zassetsu(jst)
            return "・".join(map(lambda x: lcst.ZASSETSU[x], codes))
        except Exception as e:
            raise

    def kokei_sun(self, jst=None):
        """ 視黄経（太陽）計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return float       : 視黄経（太陽）(単位: deg)
        """
        try:
            if jst is None:
                utc = self.utc
            else:
                utc = jst - timedelta(hours=9)
            return self.__comp_kokei_sun(utc)
        except Exception as e:
            raise

    def kokei_moon(self, jst=None):
        """ 視黄経（月）計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return float       : 視黄経（月）(単位: deg)
        """
        try:
            if jst is None:
                utc = self.utc
            else:
                utc = jst - timedelta(hours=9)
            return self.__comp_kokei_moon(utc)
        except Exception as e:
            raise

    def moonage(self, jst=None):
        """ 月齢（正午）計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return float       : 月齢（正午）
        """
        try:
            if jst is None:
                jst = self.jst
            return self.__comp_moonage(jst)
        except Exception as e:
            raise

    def oc(self, jst=None):
        """ 旧暦計算

        :param  datetime jst: JST（日本標準時）(optional)
        :return list        : [旧暦年, 閏月Flag, 旧暦月, 旧暦日, 六曜]
        """
        try:
            if jst is None:
                jst = self.jst
            return self.__comp_oc(jst)
        except Exception as e:
            raise

    def __holiday_year(self, year):
        """ 年間休日一覧の取得

        :param  int year     : 対象の西暦年
        :return list holidays: 年間休日一覧
        """
        try:
            # 日付固定の祝日、変動の祝日の日付･曜日を計算
            holiday_0 = self.__comp_holiday_0(year)
            # 国民の休日計算
            holiday_1 = self.__comp_holiday_1(holiday_0)
            # 振替休日計算
            holiday_2 = self.__comp_holiday_2(holiday_0)
            return sorted(holiday_0 + holiday_1 + holiday_2)
        except Exception as e:
            raise

    def __comp_holiday_0(self, year):
        """ 日付固定の祝日、変動の祝日の日付・曜日を計算
            * 施行日：1948-07-20

        :param  int year: 対象の西暦年
        :return list    : 変動の祝日の日付・曜日の一覧
        """
        holidays = []
        try:
            for hid, month, day, kbn, year_s, year_e, name in lcst.HOLIDAY:
                if kbn > 7 or year < year_s or year > year_e:
                    continue
                if kbn == 0:  # 月日が既定のもの
                    gc = datetime(year, month, day)
                    jd = ltm.gc2jd(gc) + lcst.JST_D
                    yobi = self.__yobi(jd)
                    holidays.append([year, month, day, hid])
                else:         # 月日が不定のもの
                    if kbn == 2:    # 第2月曜日 ( 8 - 14 の月曜日)
                        for day_2 in range(8, 15):
                            gc = datetime(year, month, day_2)
                            jd = ltm.gc2jd(gc) + lcst.JST_D
                            yobi = self.__yobi(jd)
                            if yobi == 1:
                                holidays.append([year, month, day_2, hid])
                                break
                    elif kbn == 3:  # 第3月曜日 ( 15 - 21 の月曜日)
                        for day_2 in range(15, 22):
                            gc = datetime(year, month, day_2)
                            jd = ltm.gc2jd(gc) + lcst.JST_D
                            yobi = self.__yobi(jd)
                            if yobi == 1:
                                holidays.append([year, month, day_2, hid])
                                break
                    elif kbn == 4:  # 二分（春分、秋分）
                        gc = datetime(year, month, 30)
                        day_2 = self.__get_last_nc(gc, 180)[0].day
                        gc = datetime(year, month, day_2)
                        holidays.append([year, month, day_2, hid])
            return holidays
        except Exception as e:
            raise

    def __comp_holiday_1(self, holiday_0):
        """ 国民の休日計算
            ( 「国民の祝日」で挟まれた「国民の祝日」でない日 )
            ( 年またぎは考慮していない(今のところ不要) )
            * 施行日：1985-12-27

        :param  list holiday_0: 変動の祝日の日付・曜日の一覧
        :return list          : 国民の休日の一覧
        """
        holidays = []
        try:
            y_min = [h[4] for h in lcst.HOLIDAY if h[0] == 90][0]
            if holiday_0[0][0] < y_min:
                return []
            for i in range(len(holiday_0) - 1):
                y_0, m_0, d_0 = holiday_0[i    ][0:3]
                y_1, m_1, d_1 = holiday_0[i + 1][0:3]
                jd_0 = ltm.gc2jd(datetime(y_0, m_0, d_0))
                jd_1 = ltm.gc2jd(datetime(y_1, m_1, d_1))
                if jd_0 + 2 == jd_1:
                    jd = jd_0 + 1
                    yobi = self.__yobi(jd)
                    y, m, d = ltm.jd2gc(jd)[0:3]
                    holidays.append([y, m, d, 90])
            return holidays
        except Exception as e:
            raise

    def __comp_holiday_2(self, holiday_0):
        """ 振替休日計算
            ( 「国民の祝日」が日曜日に当たるときは、
              その日後においてその日に最も近い「国民の祝日」でない日 )
            * 施行日：1973-04-12

        :param  list holiday_0: 変動の祝日の日付の曜日の一覧
        :return list          : 振替休日の一覧
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
                jd = ltm.gc2jd(datetime(y, m, d))
                yobi = self.__yobi(jd)
                if yobi != 0:
                    continue
                next_jd = jd + 1
                next_yobi = self.__yobi(next_jd)
                if i == len(holiday_0) - 1:
                    next_y, next_m, next_d = ltm.jd2gc(next_jd)[0:3]
                    holidays.append([next_y, next_m, next_d, 91])
                else:
                    flg_furikae = 0
                    plus_day = 1
                    while flg_furikae == 0:
                        if i + plus_day < len(holiday_0):
                            plus_y, plus_m, plus_d \
                                = holiday_0[i + plus_day][0:3]
                            gc= datetime(plus_y, plus_m, plus_d)
                            plus_jd = ltm.gc2jd(gc)
                            if next_jd == plus_jd:
                                next_jd += 1
                                next_yobi = 0 \
                                    if next_yobi == 6 else next_yobi + 1
                                plus_day += 1
                            else:
                                flg_furikae = 1
                                next_y, next_m, next_d \
                                    = ltm.jd2gc(next_jd)[0:3]
                                holidays.append(
                                    [next_y, next_m, next_d, 91]
                                )
            return holidays
        except Exception as e:
            raise

    def __yobi(self, jd):
        """ 曜日計算
            * datetime の weekday() 関数は使用しない

        :param  float jd: ユリウス日
        :return int     : 0-6
        """
        try:
            return (int(jd) + 2) % 7
        except Exception as e:
            raise

    def __holiday(self, jst):
        """ 休日計算
            * 国民の休日とハッピーマンデーのダブリは考慮不要（現行制度上）

        :param  datetime jst: JST（日本標準時）
        :return int         : HOLIDAY のインデックス
        """
        try:
            # 日付固定の祝日、変動の祝日？
            code = self.__holiday_n(jst)
            if code != 99:
                return code
            # 国民の休日？
            code = self.__holiday_k(jst)
            if code != 99:
                return code
            # 振替休日？
            code = self.__holiday_f(jst)
            if code != 99:
                return code
            return 99
        except Exception as e:
            raise

    def __holiday_n(self, jst):
        """ 日付固定の祝日、変動の祝日計算
            * 施行日：1948-07-20

        :param  datetime jst: JST（日本標準時）
        :return int         : HOLIDAY のインデックス
        """
        try:
            # 月日固定の祝日
            res = [
                h[0] for h in lcst.HOLIDAY
                if h[1] == jst.month == h[1] and \
                   h[2] == jst.day == h[2] and \
                   h[4] <= jst.year and \
                   h[5] >= jst.year
            ]
            if res:
                return res[0]
            # ハッピーマンデー
            if self.__yobi(ltm.gc2jd(jst)) == 1:
                n = (jst.day - 1) // 7 + 1
                # 第[23]月曜日
                if n == 2 or n == 3:
                    res = [
                        h[0] for h in lcst.HOLIDAY
                        if h[1] == jst.month and h[3] == n and \
                           h[4] <= jst.year and \
                           h[5] >= jst.year
                    ]
                    if res:
                        return res[0]
            # [春秋]分の日
            if jst.month == 3 or jst.month == 9:
                gc = datetime(jst.year, jst.month, 30)
                dt_n = self.__get_last_nc(gc, 180)[0]
                if dt_n.month == jst.month and dt_n.day == jst.day:
                    res = [
                        h[0] for h in lcst.HOLIDAY
                        if h[1] == jst.month and h[3] == 4 and \
                           h[4] <= jst.year and \
                           h[5] >= jst.year
                    ]
                    if res:
                        return res[0]
            return 99
        except Exception as e:
            raise

    def __holiday_k(self, jst):
        """ 国民の休日を計算
            ( 「国民の祝日」で挟まれた「国民の祝日」でない日 )
            ( 年またぎは考慮していない(今のところ不要) )
            * 施行日：1985-12-27

        :param  datetime jst: JST（日本標準時）
        :return int         : 休日コード（国民の休日=90, その他=99）
        """
        try:
            y_min = [h[4] for h in lcst.HOLIDAY if h[0] == 90][0]
            if jst.year < y_min:
                return 99
            # 前日
            code_y = self.__holiday_n(jst - timedelta(days=1))
            if code_y == 99:
                return 99
            # 翌日
            code_t = self.__holiday_n(jst + timedelta(days=1))
            if code_t == 99:
                return 99
            return 90  # 国民の休日
        except Exception as e:
            raise

    def __holiday_f(self, jst):
        """ 振替休日計算
            ( 「国民の祝日」が日曜日に当たるときは、
              その日後においてその日に最も近い「国民の祝日」でない日 )
            * 施行日：1973-04-12

        :param  datetime jst: JST（日本標準時）
        :return int         : 休日コード（振替休日=91, その他=99）
        """
        try:
            y_min = [h[4] for h in lcst.HOLIDAY if h[0] == 91][0]
            if jst.year < y_min:
                return 99
            jst_y = jst - timedelta(days=1)
            code_y = self.__holiday_n(jst_y)
            while code_y < 90:
                if self.__yobi(ltm.gc2jd(jst_y)) == 0:
                    return 91  # 振替休日
                jst_y -= timedelta(days=1)
                code_y = self.__holiday_n(jst_y)
            return 99
        except Exception as e:
            raise

    def __kanshi(self, jd):
        """ 干支計算

        :param  float jd: ユリウス日
        :return int     : KANSHI のインデックス
        """
        try:
            return (int(jd) - 10) % 60
        except Exception as e:
            raise

    def __sekki_24(self, jst):
        """ 二十四節気取得
            * 処理が重くなるため、ここでは計算しない。
            * 予め計算しておいたデータから該当のものを取得する。

        :param  datetime jst: JST（日本標準時）
        :return int         : 二十四節気に対応した視黄経（15度間隔）
        """
        try:
            res = [
                row[-1] for row in ls24.SEKKI_24_TM
                if list(map(lambda x: int(x), row[0:3])) ==
                   [jst.year, jst.month, jst.day]
            ]
            deg = res[0] if res else 999
            return deg
        except Exception as e:
            raise

    def __sekku(self, jst):
        """ 節句計算

        :param  datetime jst: JST（日本標準時）
        :return int         : SEKKU のインデックス
        """
        try:
            res = [
                s[0] for s in lcst.SEKKU
                if s[1] == jst.month and s[2] == jst.day
            ]
            code = res[0] if res else 9
            return code
        except Exception as e:
            raise

    def __zassetsu(self, jst):
        """ 雑節計算

        :param  datetime jst: JST（日本標準時）
        :return list        : ZASSETSU のインデクスの list（要素数:0-2）
        """
        zassetsus = []
        try:
            utc = jst - timedelta(hours=9)
            jd = ltm.gc2jd(jst)

            # 計算対象日の太陽の黄経
            lmd_today = self.__comp_kokei_sun(utc)
            # 計算対象日の翌日の太陽の黄経
            lmd_tomorrow = self.__comp_kokei_sun(utc + timedelta(days=1))
            # 計算対象日の5日前の太陽の黄経(社日計算用)
            lmd_before_5 = self.__comp_kokei_sun(utc - timedelta(days=5))
            # 計算対象日の4日前の太陽の黄経(社日計算用)
            lmd_before_4 = self.__comp_kokei_sun(utc - timedelta(days=4))
            # 計算対象日の5日後の太陽の黄経(社日計算用)
            lmd_after_5  = self.__comp_kokei_sun(utc + timedelta(days=5))
            # 計算対象日の6日後の太陽の黄経(社日計算用)
            lmd_after_6  = self.__comp_kokei_sun(utc + timedelta(days=6))
            # 太陽の黄経の整数部分( 土用, 入梅, 半夏生 計算用 )
            lmd_today0    = int(lmd_today)
            lmd_tomorrow0 = int(lmd_tomorrow)

            #### ここから各種雑節計算
            # 0:節分 ( 立春の前日 )
            if self.__sekki_24(jst + timedelta(days=1)) == 315:  # 立春
                zassetsus.append(0)
            # 1:彼岸入（春） ( 春分の日の3日前 )
            if self.__sekki_24(jst + timedelta(days=3)) == 0:    # 春分
                zassetsus.append(1)
            # 2:彼岸（春） ( 春分の日 )
            if self.__sekki_24(jst) == 0:    # 春分
                zassetsus.append(2)
            # 3:彼岸明（春） ( 春分の日の3日後 )
            if self.__sekki_24(jst - timedelta(days=3)) == 0:    # 春分
                zassetsus.append(3)
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
                    if self.__sekki_24(jst + timedelta(days=i)) == 0:  # 春分
                        zassetsus.append(4)
                        break
                # [ 1日前から4日前 ]
                for i in range(1, 5):
                    if self.__sekki_24(jst - timedelta(days=i)) == 0:  # 春分
                        zassetsus.append(4)
                        break
                # [ 5日後 ]
                if self.__sekki_24(jst + timedelta(days=5)) == 0:  # 春分
                    # 春分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 0度(360度)以上なら、春分点が午前と判断
                    if (lmd_after_5 + lmd_after_6 + 360) / 2 >= 360:
                        zassetsus.append(4)
                # [ 5日前 ]
                if self.__sekki_24(jst - timedelta(days=5)) == 0:  # 春分
                    # 春分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 0度(360度)未満なら、春分点が午後と判断
                    if (lmd_before_4 + lmd_before_5 + 360) / 2 < 360:
                        zassetsus.append(4)
            # 5:土用入（春） ( 黄経(太陽) = 27度 )
            if lmd_today0 != lmd_tomorrow0 and \
               lmd_tomorrow0 == 27:
                zassetsus.append(5)
            # 6:八十八夜 ( 立春から88日目(87日後) )
            if self.__sekki_24(jst - timedelta(days=87)) == 315:  # 立春
                zassetsus.append(6)
            # 7:入梅 ( 黄経(太陽) = 80度 )
            if lmd_today0 != lmd_tomorrow0 and \
               lmd_tomorrow0 == 80:
                zassetsus.append(7)
            # 8:半夏生  ( 黄経(太陽) = 100度 )
            if lmd_today0 != lmd_tomorrow0 and \
               lmd_tomorrow0 == 100:
                zassetsus.append(8)
            # 9:土用入（夏） ( 黄経(太陽) = 117度 )
            if lmd_today0 != lmd_tomorrow0 and \
               lmd_tomorrow0 == 117:
                zassetsus.append(9)
            # 10:二百十日 ( 立春から210日目(209日後) )
            if self.__sekki_24(jst - timedelta(days=209)) == 315:  # 立春
                zassetsus.append(10)
            # 11:二百二十日 ( 立春から220日目(219日後) )
            if self.__sekki_24(jst - timedelta(days=219)) == 315:  # 立春
                zassetsus.append(11)
            # 12:彼岸入（秋） ( 秋分の日の3日前 )
            if self.__sekki_24(jst + timedelta(days=3)) == 180:  # 秋分
                zassetsus.append(12)
            # 13:彼岸（秋） ( 秋分の日 )
            if self.__sekki_24(jst) == 180:  # 秋分
                zassetsus.append(13)
            # 14:彼岸明（秋） ( 秋分の日の3日後 )
            if self.__sekki_24(jst - timedelta(days=3)) == 180:  # 秋分
                zassetsus.append(14)
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
                    if self.__sekki_24(jst + timedelta(days=i)) == 180:  # 秋分
                        zassetsus.append(15)
                        break
                # [ 1日前から4日前 ]
                for i in range(1, 5):
                    if self.__sekki_24(jst - timedelta(days=i)) == 180:  # 秋分
                        zassetsus.append(15)
                        break
                # [ 5日後 ]
                if self.__sekki_24(jst + timedelta(days=5)) == 180:  # 秋分
                    # 秋分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 180度以上なら、秋分点が午前と判断
                    if (lmd_after_5 + lmd_after_6) / 2 >= 180:
                        zassetsus.append(15)
                # [ 5日前 ]
                if self.__sekki_24(jst - timedelta(days=5)) == 180:  # 秋分
                    # 秋分の日の黄経(太陽)と翌日の黄経(太陽)の中間点が
                    # 180度未満なら、秋分点が午後と判断
                    if (lmd_before_4 + lmd_before_5) / 2 < 180:
                        zassetsus.append(15)
            # 16:土用入（秋） ( 黄経(太陽) = 207度 )
            if lmd_today0 != lmd_tomorrow0 and \
               lmd_tomorrow0 == 207:
                zassetsus.append(16)
            # 17:土用入（冬） ( 黄経(太陽) = 297度 )
            if lmd_today0 != lmd_tomorrow0 and\
               lmd_tomorrow0 == 297:
                zassetsus.append(17)
            return zassetsus
        except Exception as e:
            raise

    def __comp_oc(self, jst):
        """ 旧暦計算
            * 旧暦一日の六曜
                １・７月   : 先勝
                ２・８月   : 友引
                ３・９月   : 先負
                ４・１０月 : 仏滅
                ５・１１月 : 大安
                ６・１２月 : 赤口
              と決まっていて、あとは月末まで順番通り。
              よって、月と日をたした数を６で割った余りによって六曜を決定することができます。
              ( 旧暦の月 ＋ 旧暦の日 ) ÷ 6 ＝ ？ … 余り
              余り 0 : 大安
                   1 : 赤口
                   2 : 先勝
                   3 : 友引
                   4 : 先負
                   5 : 仏滅

        :param  datetime jst: JST（日本標準時）
        :return list        : [旧暦年, 閏月Flag, 旧暦月, 旧暦日, 六曜]
        """
        chu, saku = [], []  # jd(UTC)
        m = [[0 for _ in range(3)] for _ in range(5)]
        oc = [0 for _ in range(5)]
        try:
            jd = self.jd_jst if jst == self.jst else ltm.gc2jd(jst)
            jd -= .5
            # 計算対象の直前にあたる二分二至の時刻を計算
            res = self.__get_last_nc(jst - timedelta(hours=9))
            chu.append([ltm.gc2jd(res[0]) - .375, res[1]])
            # 中気の時刻を計算 ( 3回計算する )
            for i in range(1, 4):
                dt  = datetime(*ltm.jd2gc(chu[i - 1][0] + 32))
                dt -= timedelta(hours=9)
                res = self.__get_last_nc(dt, 30)
                chu.append([ltm.gc2jd(res[0]) - .375, res[1]])
            # 計算対象の直前にあたる二分二至の直前の朔の時刻を求める
            saku.append(
                ltm.gc2jd(
                    self.__get_last_saku(datetime(*ltm.jd2gc(chu[0][0]))) \
                  - timedelta(hours=9)
                ) - 0.125
            )
            # 朔の時刻を求める
            for i in range(1, 5):
                dt  = datetime(*ltm.jd2gc(saku[i - 1] + 30 - .375))
                saku.append(
                    ltm.gc2jd(self.__get_last_saku(dt)) - .5
                )
                # 前と同じ時刻を計算した場合( 両者の差が26日以内 )には、初期値を
                # +33日にして再実行させる。
                if abs(int(saku[i - 1]) - int(saku[i])) <= 26:
                    dt  = datetime(*ltm.jd2gc(saku[i - 1] + 35 - .375))
                    saku[i] = ltm.gc2jd(self.__get_last_saku(dt)) - .5
            # saku[1]が二分二至の時刻以前になってしまった場合には、朔をさかのぼり過ぎ
            # たと考えて、朔の時刻を繰り下げて修正する。
            # その際、計算もれ（saku[4]）になっている部分を補うため、朔の時刻を計算
            # する。（近日点通過の近辺で朔があると起こる事があるようだ...？）
            if int(saku[1]) <= int(chu[0][0]):
                saku.pop(0)
                s = self.__get_last_saku(datetime(*ltm.jd2gc(saku[3] + 35)))
                saku.append(ltm.gc2jd(s))
            # saku[0]が二分二至の時刻以後になってしまった場合には、朔をさかのぼり足
            # りないと見て、朔の時刻を繰り上げて修正する。
            # その際、計算もれ（saku[0]）になっている部分を補うため、朔の時刻を計算
            # する。（春分点の近辺で朔があると起こる事があるようだ...？）
            elif int(saku[0]) > int(chu[0][0]):
                saku.pop(-1)
                s = self.__get_last_saku(datetime(*ltm.jd2gc(saku[0] + 27)))
                saku.insert(0, ltm.gc2jd(s))
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
                        m[i - 1][0] = m[i - 2][0]
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
            oc[2] = int(m[index][0])
            oc[3] = int(jd) - int(m[index][2]) + 1
            # 旧暦年の計算
            # （旧暦月が10以上でかつ新暦月より大きい場合には、
            #   まだ年を越していないはず...）
            a = ltm.jd2gc(jd)
            oc[0] = a[0]
            if oc[2] > 9 and oc[2] > a[1]:
                oc[0] -= 1
            # 六曜
            oc[4] = lcst.ROKUYO[(oc[2] + oc[3]) % 6]
            return oc
        except Exception as e:
            raise

    def __get_last_nc(self, jst, kbn=90):
        """ 直前二分二至・中気時刻取得
            * 処理が重くなるため、ここでは計算しない。
            * 予め計算しておいたデータから該当のものを取得する。

        :param  datetime jst: JST（日本標準時）
        :param  int      kbn: 90: 二分二至, 30: 中気
        :return list        : [二分二至・中気の時刻, その時の黄経]
        """
        try:
            sekki_24_tms = [s for s in ls24.SEKKI_24_TM if s[6] % kbn == 0]
            str_target  = jst.strftime("%Y-%m-%d %H:%M:%S")
            str_target += " {:3d}".format(kbn)
            for row in reversed(sekki_24_tms):
                str_row = (
                    "{:04d}-{:02d}-{:02d} "
                    "{:02d}:{:02d}:{:02d}"
                ).format(*row)
                if str_row <= str_target[0:19]:
                    return [
                        datetime(*list(map(lambda x: int(x), row[0:6]))),
                        int(row[6])
                    ]
            return []
        except Exception as e:
            raise

    def __get_last_saku(self, jst):
        """ 直前朔時刻取得
            * 処理が重くなるため、ここでは計算しない。
            * 予め計算しておいたデータから該当のものを取得する。

        :param  datetime jst: JST（日本標準時）
        :return datetime    : 朔の時刻
        """
        try:
            str_target  = jst.strftime("%Y-%m-%d %H:%M:%S")
            for row in reversed(lsak.SAKU_TM):
                str_row = (
                    "{:04d}-{:02d}-{:02d} "
                    "{:02d}:{:02d}:{:02d}"
                ).format(*row)
                if str_row <= str_target:
                    return datetime(*list(map(lambda x: int(x), row[0:6])))
            return None
        except Exception as e:
            raise

    def __comp_moonage(self, jst):
        """ 月齢(正午)計算

        :param  float jd: ユリウス日(JST)
        :return float   : 月齢(正午)
        """
        try:
            jd = self.jd_jst if jst == self.jst else ltm.gc2jd(jst)
            last_saku = self.__get_last_saku(jst)
            return jd + 0.5 - ltm.gc2jd(last_saku)
        except Exception as e:
            raise

    def __comp_kokei_sun(self, utc):
        """ 太陽視黄経計算

        :param  datetime    utc: UTC（協定世界時）
        :return float kokei_sun: 太陽視黄経
        """
        try:
            o = lapos.Apos(self.bin_path, utc)
            kokei_sun  = o.sun()[1][0] * 180.0 / math.pi
            return kokei_sun
        except Exception as e:
            raise

    def __comp_kokei_moon(self, utc):
        """ 月視黄経計算

        :param  datetime     utc: UTC（協定世界時）
        :return float kokei_moon: 月視黄経
        """
        try:
            o = lapos.Apos(self.bin_path, utc)
            kokei_moon = o.moon()[1][0] * 180.0 / math.pi
            return kokei_moon
        except Exception as e:
            raise

