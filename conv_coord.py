#! /usr/local/bin/python3
"""
赤道・黄道座標変換

  date          name            version
  2018.04.27    mk-mode         1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
"""
import math
import sys
import traceback
from lib import coord as lcd


class ConvCoord:
    # 黄道傾斜角(単位: rad)
    EPS = 23.43929 * math.pi / 180
    # 元の赤道直交座標
    # (ある日の地球重心から見た太陽重心の位置(単位: AU))
    POS = [ 0.99443659220700997281, -0.03816291768957833647, -0.01655177670960058384]

    def exec(self):
        try:
            self.rect_ec = lcd.rect_eq2ec(self.POS, self.EPS)
            self.rect_eq = lcd.rect_ec2eq(self.rect_ec, self.EPS)
            self.pol_eq, self.r = lcd.rect2pol(self.rect_eq)
            self.pol_ec = lcd.pol_eq2ec(self.pol_eq, self.EPS)
            self.pol_eq = lcd.pol_ec2eq(self.pol_ec, self.EPS)
            self.rect_eq_2 = lcd.pol2rect(self.pol_eq, self.r)
            self.__display()
        except Exception as e:
            raise

    def __display(self):
        """ 結果出力 """
        try:
            pass
            print((
                "元の赤道直交座標:\n  {}\n"
                "黄道直交座標に変換:\n  {}\n"
                "赤道直交座標に戻す:\n  {}\n"
                "赤道極座標に変換:\n  {} (R = {})\n"
                "黄道極座標に変換:\n  {}\n"
                "赤道極座標に戻す:\n  {}\n"
                "赤道直交座標に戻す:\n  {}"
            ).format(
                self.POS,
                self.rect_ec,
                self.rect_eq,
                self.pol_eq, self.r,
                self.pol_ec,
                self.pol_eq,
                self.rect_eq_2
            ))
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = ConvCoord()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

