#! /usr/local/bin/python3
"""
JPLEPH(JPL の DE430 バイナリデータ)読み込み、座標（位置・速度）を計算

  date          name            version
  2018.05.01    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
----------------------------------------------------------------------
* 引数
  [第１] 対象天体番号（必須）
          1: 水星            (Mercury)
          2: 金星            (Venus)
          3: 地球            (Earth)
          4: 火星            (Mars)
          5: 木星            (Jupiter)
          6: 土星            (Saturn)
          7: 天王星          (Uranus)
          8: 海王星          (Neptune)
          9: 冥王星          (Pluto)
         10: 月              (Moon)
         11: 太陽            (Sun)
         12: 太陽系重心      (Solar system Barycenter)
         13: 地球 - 月の重心 (Earth-Moon Barycenter)
         14: 地球の章動      (Earth Nutations)
         15: 月の秤動        (Lunar mantle Librations)
  [第２] 基準天体番号（必須。 0, 1 - 13）
         （ 0 は、対象天体番号が 14, 15 のときのみ）
  [第３] ユリウス日（省略可。省略時は現在日時のユリウス日）

* 注意事項
  - 求める座標は「赤道直角座標(ICRS)」
  - 天体番号は、係数データの番号（並び順）と若干異なるので注意する。
    （特に、天体番号 3, 10, と 12 以降）
    係数データの並び順：
      水星(1)、金星(2)、地球 - 月の重心(3)、火星(4)、木星(5)、土星(6)、
      天王星(7)、海王星(8)、冥王星(9)、月（地心）(10)、太陽(11)、
      地球の章動(12)、月の秤動(13)
  - 時刻系は「太陽系力学時(TDB)」である。（≒地球時(TT)）
  - 天体番号が 1 〜 13 の場合は、 x, y, z の位置・速度（6要素）、
    天体番号が 14 の場合は、黄経における章動 Δψ, 黄道傾斜における章動 Δε の
    角位置・角速度（4要素）、
    天体番号が 15 の場合は、 φ, θ, ψ の角位置・角速度（6要素）。
  - 対象天体番号 = 基準天体番号 は、無意味なので処理しない。
  - 天体番号が 12 の場合は、 x, y, z の位置・速度の値は全て 0.0 とする。
  - その他、JPL 提供の FORTRAN プログラム "testeph.f" を参考にした。
"""
import datetime
import struct
import sys
import traceback
from lib import eph_jpl as ljpl


class EphemerisJpl:
    USAGE = (
        "【使用方法】 ./jpl_calc_de430.rb 対象天体番号 基準天体番号 [ユリウス日]\n"
        "【天体番号】（対象: 1 - 15, 基準: 0 - 13）\n"
        "   1: 水星,  2: 金星,  3: 地球,  4: 火星,  5: 木星,\n"
        "   6: 土星,  7: 天王星,  8: 海王星,  9: 冥王星, 10: 月,\n"
        "  11: 太陽,  12: 太陽系重心,  13: 地球 - 月の重心,\n"
        "  14: 地球の章動,  15: 月の秤動,\n"
        "   0: 対象天体番号 14, 15 の場合に指定\n"
        "  ※対象天体番号≠基準天体番号"
    )
    ASTRS = [
        "Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus",
        "Neptune", "Pluto", "Moon", "Sun", "Solar system Barycenter",
        "Earth-Moon barycenter", "Earth Nutations", "Lunar mantle Librations"
    ]
    FILE_BIN = "/path/to/JPLEPH"
    BARY = True
    KM   = False

    def __init__(self):
        self.__get_args()

    def exec(self):
        """ Execution """
        try:
            de = ljpl.EphJpl(
                self.FILE_BIN,
                *self.astrs, self.jd,
                self.BARY, self.KM
            )
            self.au = de.au
            self.rrds = de.calc()
            self.__display()
        except Exception as e:
            raise

    def __get_args(self):
        """ コマンドライン引数取得
            * 第１引数の値をインスタンス変数 self.astrs[0] に設定する
            * 第２引数の値をインスタンス変数 self.astrs[1] に設定する
            * 第３引数の値をインスタンス変数 self.jd に設定する
              （但し、第３引数が存在しない場合は現在日時を設定する）
        """
        try:
            # 対象、基準天体番号
            if len(sys.argv) < 3:
                print(self.USAGE)
                sys.exit(0)
            target, center = int(sys.argv[1]), int(sys.argv[2])
            if ((target < 1 or target > 15) or
                (center < 0 or center > 13) or
                 target == center or
                (target == 14 and center != 0) or
                (target == 15 and center != 0) or
                (target != 14 and target != 15 and center == 0)):
                print(self.USAGE)
                sys.exit(0)
            self.astrs = [target, center]
            # ユリウス日
            if len(sys.argv) > 3:
                self.jd = float(sys.argv[3])
            else:
                self.jd = self.__gc2jd(datetime.datetime.now())
        except Exception as e:
            raise

    def __gc2jd(self, t):
        """ 年月日(グレゴリオ暦)からユリウス日(JD)を計算する
            * フリーゲルの公式を使用する
              JD = int(365.25 * year)
                 + int(year / 400)
                 - int(year / 100)
                 + int(30.59 (month - 2))
                 + day
                 + 1721088
            * 上記の int(x) は厳密には、 x を超えない最大の整数

        :param  object t: datetime
        :return float jd: ユリウス日
        """
        year, month,  day    = t.year, t.month,  t.day
        hour, minute, second = t.hour, t.minute, t.second
        try:
            # 1月,2月は前年の13月,14月とする
            if month < 3:
                year  -= 1
                month += 12
            # 日付(整数)部分計算
            jd  = int(365.25 * year) + year // 400 - year // 100 \
                + int(30.59 * (month - 2)) + day + 1721088
            # 時間(小数)部分計算
            t  = (second / 3600 + minute / 60 + hour) / 24
            return jd + t
        except Exception as e:
            raise

    def __display(self):
        """ Display """
        try:
            s = (
                "  Target: {:2d} ({})\n"
                "  Center: {:2d}"
            ).format(
                self.astrs[0], self.ASTRS[self.astrs[0] - 1],
                self.astrs[1]
            )
            if self.astrs[1] != 0:
                s += " ({})".format(self.ASTRS[self.astrs[1] - 1])
            s += (
                "\n"
                "      JD: {:16.8f} day\n"
                "     1AU: {:11.1f} km\n"
            ).format(self.jd, self.au)
            print(s)
            s = ""
            if self.astrs[0] == 14:
                s = (
                    "  Position(Δψ) = {:32.20f} rad\n"
                    "  Position(Δε) = {:32.20f} rad\n"
                    "  Velocity(Δψ) = {:32.20f} rad/day\n"
                    "  Velocity(Δε) = {:32.20f} rad/day"
                ).format(
                    self.rrds[0], self.rrds[1],
                    self.rrds[2], self.rrds[3]
                )
            elif self.astrs[0] == 15:
                s = (
                    "  Position(φ) = {:32.20f} rad\n"
                    "  Position(θ) = {:32.20f} rad\n"
                    "  Position(ψ) = {:32.20f} rad\n"
                    "  Velocity(φ) = {:32.20f} rad/day\n"
                    "  Velocity(θ) = {:32.20f} rad/day\n"
                    "  Velocity(ψ) = {:32.20f} rad/day"
                ).format(
                    self.rrds[0], self.rrds[1], self.rrds[2],
                    self.rrds[3], self.rrds[4], self.rrds[5]
                )
            else:
                unit_0, unit_1 = ["km", "sec"] if self.KM else ["AU", "day"]
                s = (
                    "  Position(x) = {:32.20f} {}\n"
                    "  Position(y) = {:32.20f} {}\n"
                    "  Position(z) = {:32.20f} {}\n"
                    "  Velocity(x) = {:32.20f} {}/{}\n"
                    "  Velocity(y) = {:32.20f} {}/{}\n"
                    "  Velocity(z) = {:32.20f} {}/{}"
                ).format(
                    self.rrds[0], unit_0,
                    self.rrds[1], unit_0,
                    self.rrds[2], unit_0,
                    self.rrds[3], unit_0, unit_1,
                    self.rrds[4], unit_0, unit_1,
                    self.rrds[5], unit_0, unit_1
                )
            print(s)
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = EphemerisJpl()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

