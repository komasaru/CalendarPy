"""
JPLEPH(JPL の DE430 バイナリデータ)読み込みライブラリ

  date          name            version
  2018.04.05    mk-mode.com     1.00 新規作成

Copyright(C) 2018 mk-mode.com All Rights Reserved.
----------------------------------------------------------------------
     1: 水星 (Mercury)
     2: 金星 (Venus)
     3: 地球 - 月の重心 (Earth-Moon barycenter)
     4: 火星 (Mars)
     5: 木星 (Jupiter)
     6: 土星 (Saturn)
     7: 天王星 (Uranus)
     8: 海王星 (Neptune)
     9: 冥王星 (Pluto)
    10: 月（地心） (Moon (geocentric))
    11: 太陽 (Sun)
    12: 地球の章動（1980年IAUモデル） (Earth Nutations in longitude and obliquity(IAU 1980 model))
    13: 月の秤動 (Lunar mantle libration)
"""
import datetime
import struct


class JplReadDe430:
    FILE_BIN = "JPLEPH"
    KSIZE    = 2036
    RECL     = 4

    def __init__(self, jd):
        self.pos = 0                         # レコード位置
        self.jd = jd

    def read_de430(self):
        """ Execution """
        try:
            with open(self.FILE_BIN, "rb") as f:
                self.__get_ttl(f)     # TTL
                self.__get_cnam(f)    # CNAM
                self.__get_ss(f)      # SS
                self.__get_ncon(f)    # NCON
                self.__get_au(f)      # AU
                self.__get_emrat(f)   # EMRAT
                self.__get_ipt(f)     # IPT
                self.__get_numde(f)   # NUMDE
                self.__get_ipt_13(f)  # IPT
                self.__get_cval(f)    # CVAL
                self.__get_coeff(f)   # 係数取得
            self.__get_jdepoc()       # JDEPOC
        except Exception as e:
            raise

    def __get_ttl(self, f):
        """ TTL（タイトル）取得
            - 84 byte * 3
            - ASCII文字列(後続のnull文字やスペースを削除)

        :param file_object f
        """
        len_rec = 84
        self.ttl = ""
        try:
            for i in range(3):
                f.seek(self.pos + len_rec * i)
                a = struct.unpack(str(len_rec) + "s", f.read(len_rec))[0]
                if i != 0:
                    self.ttl += "\n"
                self.ttl += a.decode("utf-8").rstrip()
            self.pos += len_rec * 3
        except Exception as e:
            raise

    def __get_cnam(self, f):
        """ CNAM（定数名）取得
            - 6 byte * 400
            - ASCII文字列(後続のnull文字やスペースを削除)

        :param file_object f
        """
        len_rec = 6
        self.cnams = []
        try:
            for i in range(400):
                f.seek(self.pos + len_rec * i)
                a = struct.unpack(str(len_rec) + "s", f.read(len_rec))[0]
                self.cnams.append(a.decode("utf-8").rstrip())
            self.pos += len_rec * 400
        except Exception as e:
            raise

    def __get_ss(self, f):
        """ SS（ユリウス日（開始、終了）、分割日数）取得
            - 8 byte * 3
            - 倍精度浮動小数点数(機種依存)

        :param file_object f
        """
        len_rec = 8
        self.sss = []
        try:
            for i in range(3):
                f.seek(self.pos + len_rec * i)
                a = struct.unpack("d", f.read(len_rec))[0]
                self.sss.append(a)
            self.pos += len_rec * 3
        except Exception as e:
            raise

    def __get_ncon(self, f):
        """ NCON（定数の数）取得
            - 4 byte * 1
            - unsigned int (符号なし整数, エンディアンと int のサイズに依存)

        :param file_object f
        """
        len_rec = 4
        try:
            f.seek(self.pos)
            a = struct.unpack("I", f.read(len_rec))[0]
            self.ncon = a
            self.pos += len_rec
        except Exception as e:
            raise

    def __get_au(self, f):
        """ AU（天文単位）取得
            - 8 byte * 1
            - 倍精度浮動小数点数(機種依存)

        :param file_object f
        """
        len_rec = 8
        try:
            f.seek(self.pos)
            a = struct.unpack("d", f.read(len_rec))[0]
            self.au = a
            self.pos += len_rec
        except Exception as e:
            raise

    def __get_emrat(self, f):
        """ EMRAT（地球と月の質量比）取得
            - 8 byte * 1
            - 倍精度浮動小数点数(機種依存)

        :param file_object f
        """
        len_rec = 8
        try:
            f.seek(self.pos)
            a = struct.unpack("d", f.read(len_rec))[0]
            self.emrat = a
            self.pos += len_rec
        except Exception as e:
            raise

    def __get_numde(self, f):
        """ NUMDE（DEバージョン番号）取得
            - 4 byte * 1
            - unsigned int (符号なし整数, エンディアンと int のサイズに依存)

        :param file_object f
        """
        len_rec = 4
        try:
            f.seek(self.pos)
            a = struct.unpack("I", f.read(len_rec))[0]
            self.numde = a
            self.pos += len_rec
        except Exception as e:
            raise

    def __get_ipt(self, f):
        """ IPT（オフセット、係数の数、サブ区間数）（水星〜月の章動）取得
            - 4 byte * 12 * 3
            - unsigned int (符号なし整数, エンディアンと int のサイズに依存)

        :param file_object f
        """
        len_rec = 4
        self.ipts = []
        try:
            for i in range(12):
                l = []
                for j in range(3):
                    f.seek(self.pos + len_rec * j)
                    a = struct.unpack("I", f.read(len_rec))[0]
                    l.append(a)
                self.ipts.append(l)
                self.pos += len_rec * 3
        except Exception as e:
            raise

    def __get_ipt_13(self, f):
        """ IPT_13（オフセット、係数の数、サブ区間数）（月の秤動）取得
            - 4 byte * 1 * 3
            - unsigned int (符号なし整数, エンディアンと int のサイズに依存)

        :param file_object f
        """
        len_rec = 4
        try:
            l = []
            for i in range(3):
                f.seek(self.pos + len_rec * i)
                a = struct.unpack("I", f.read(len_rec))[0]
                l.append(a)
            self.ipts.append(l)
            self.pos += len_rec * 3
        except Exception as e:
            raise

    def __get_cval(self, f):
        """ CVAL（定数値）取得
            - 8 byte * @ncon
            - 倍精度浮動小数点数(機種依存)

        :param file_object f
        """
        self.pos = self.KSIZE * self.RECL
        len_rec = 8
        self.cvals = []
        try:
            for i in range(self.ncon):
                f.seek(self.pos + len_rec * i)
                a = struct.unpack("d", f.read(len_rec))[0]
                self.cvals.append(a)
        except Exception as e:
            raise

    def __get_coeff(self, f):
        """ COEFF 取得
            * レコード位置計算
            * 対象区間のユリウス日（開始、終了）をインスタンス変数(list)
              self.jds に設定する
            * 全ての係数の値をインスタンス変数（配列） self.coeffs に設定する
              （x, y, z やサブ区間毎に分割して格納）
            * 8 byte * ?
            * 倍精度浮動小数点数(機種依存)
            * 最初の2要素は当該データの開始・終了ユリウス日
        """
        idx = (self.jd - self.sss[0]) // self.sss[2]
        pos = int(self.KSIZE * self.RECL * (2 + idx))
        recl = 8
        items = []
        self.coeffs = []
        try:
            for i in range(self.KSIZE // 2):
                f.seek(pos + recl * i)
                a = struct.unpack("d", f.read(recl))[0]
                items.append(a)
            self.jds = [items.pop(0), items.pop(0)]
            for i, ipt in enumerate(self.ipts):
                n = 2 if i == 11 else 3
                l_1 = []
                for _ in range(ipt[2]):
                    l_0 = []
                    for _ in range(n):
                        l_0.append(items[:ipt[1]])
                        items = items[ipt[1]:]
                    l_1.append(l_0)
                self.coeffs.append(l_1)
        except Exception as e:
            raise

    def __get_jdepoc(self):
        """ JDEPOC 取得
            * self.cvals（定数値配列）の中から「元期」をインスタンス変数
              self.jdepoc に設定する
        """
        try:
            self.jdepoc = self.cvals[4]
        except Exception as e:
            raise

