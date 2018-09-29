#! /usr/local/bin/python3
"""
各種時刻換算

  date          name            version
  2018.04.26    mk-mode         1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
---
  引数 : JST（日本標準時）
           書式：YYYYMMDD or YYYYMMDDHHMMSS or YYYYMMDDHHMMSSUUUUUU
           無指定なら現在(システム日時)と判断。（上記の U はマイクロ秒）
---
* 定数 DUT1 (= UT1 - UTC) の値は以下を参照。
    [日本標準時プロジェクト Announcement of DUT1]
    (http://jjy.nict.go.jp/QandA/data/dut1.html)
  但し、値は 1.0 秒以下なので、精度を問わないなら 0.0 固定でもよい(?)
* UTC - TAI（協定世界時と国際原子時の差）は、以下のとおりとする。
  - 1972年07月01日より古い場合は一律で 10
  - 2019年07月01日以降は一律で 37
  - その他は、指定の値
    [日本標準時プロジェクト　Information of Leap second]
    (http://jjy.nict.go.jp/QandA/data/leapsec.html)
* ΔT = TT - UT1 は、以下のとおりとする。
  - 1972-01-01 以降、うるう秒挿入済みの年+2までは、以下で算出
      ΔT = 32.184 - (UTC - TAI) - DUT1
    UTC - TAI は
    [うるう秒実施日一覧](http://jjy.nict.go.jp/QandA/data/leapsec.html)
    を参照
  - その他の期間は NASA 提供の略算式により算出
    [NASA - Polynomial Expressions for Delta T]
    (http://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html)
"""
from datetime import datetime
from datetime import timedelta
import re
import sys
import traceback
from lib import delta_t as ldt
from lib import time_   as ltm


class ConvTime:
    MSG_ERR_1 = "[ERROR] Format: YYYYMMDD or YYYYMMDDHHMMSS or YYYYMMDDHHMMSSUUUUUU"
    MSG_ERR_2 = "[ERROR] Invalid date!"
    JST_UTC = 9

    def __init__(self):
        self.__get_arg()

    def exec(self):
        try:
            self.jd      = ltm.gc2jd(self.utc)
            self.t       = ltm.jd2jc(self.jd)
            self.utc_tai = ltm.utc2utc_tai(self.utc)
            self.dut1    = ltm.utc2dut1(self.utc)
            odt          = ldt.DeltaT(self.utc.year, self.utc.month)
            self.dt      = odt.delta_t()
            self.tai     = ltm.utc2tai(self.utc, self.utc_tai)
            self.ut1     = ltm.utc2ut1(self.utc, self.dut1)
            self.tt      = ltm.tai2tt(self.tai)
            self.tcg     = ltm.tt2tcg(self.tt, self.jd)
            self.tcb     = ltm.tt2tcb(self.tt, self.jd)
            self.jd_tcb  = ltm.gc2jd(self.tcb)
            self.tdb     = ltm.tcb2tdb(self.tcb, self.jd_tcb)
            self.__display()
        except Exception as e:
            raise

    def __get_arg(self):
        """ 引数取得
            * コマンドライン引数を取得して日時の妥当性チェックを行う。
            * コマンドライン引数無指定なら、現在日時とする。
            * JST, UTC をインスタンス変数 jst, utc に格納する。
        """
        try:
            if len(sys.argv) < 2:
                self.jst = datetime.now()
            else:
                arg = sys.argv[1]
                if re.search(r"^(\d{8}|\d{14}|\d{20})$", arg) is None:
                    print(self.MSG_ERR_1)
                    sys.exit()
                arg = arg.ljust(20, "0")
                try:
                    self.jst = datetime.strptime(arg, "%Y%m%d%H%M%S%f")
                except ValueError:
                    print(self.MSG_ERR_2)
                    sys.exit(1)
            self.utc = self.jst - timedelta(hours=self.JST_UTC)
        except Exception as e:
            raise

    def __display(self):
        """ 結果出力 """
        try:
            print((
                "      JST: {}\n"
                "      UTC: {}\n"
                "JST - UTC: {} hours\n"
                "       JD: {:.10f} days\n"
                "        T: {:.10f} century (= Julian Century Number)\n"
                "UTC - TAI: {} seconds (= amount of leap seconds)\n"
                "     DUT1: {:.1f} seconds\n"
                "  delta T: {:.3f} seconds\n"
                "      TAI: {}\n"
                "      UT1: {}\n"
                "       TT: {}\n"
                "      TCG: {}\n"
                "      TCB: {}\n"
                "   JD_TCB: {:.10f} days\n"
                "      TDB: {}"
            ).format(
                self.jst.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.utc.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.JST_UTC,
                self.jd,
                self.t,
                self.utc_tai,
                self.dut1,
                self.dt,
                self.tai.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.ut1.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.tt .strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.tcg.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.tcb.strftime('%Y-%m-%d %H:%M:%S.%f'),
                self.jd_tcb,
                self.tdb.strftime('%Y-%m-%d %H:%M:%S.%f')
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = ConvTime()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

