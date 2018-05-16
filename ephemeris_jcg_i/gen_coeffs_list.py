#! /usr/local/bin/python3.6
"""
リスト作成
: 天測暦テキストデータを読み込み、太陽・月・R・黄道傾斜角の係数配列を生成する

  date          name            version
  2018.03.26    mk-mode.com     1.00 新規作成

  Copyright(C) 2018 mk-mode.com All Rights Reserved.
"""
import re
import sys
import traceback


class GenCoeffsList:
    DATS = [
        [2008, "text/na08-data.txt"],
        [2009, "text/na09-data.txt"],
        [2010, "text/na10-data.txt"],
        [2011, "text/na11-data.txt"],
        [2012, "text/na12-data.txt"],
        [2013, "text/na13-data.txt"],
        [2014, "text/na14-data.txt"],
        [2015, "text/na15-data.txt"],
        [2016, "text/na16-data.txt"],
        [2017, "text/na17-data.txt"],
        [2018, "text/na18-data.txt"]
    ]
    OUT_FILE = "consts.py"

    def __init__(self):
        self.sun_ra   = []
        self.sun_dec  = []
        self.sun_dist = []
        self.moon_ra  = []
        self.moon_dec = []
        self.moon_hp  = []
        self.r        = []
        self.eps      = []

    def exec(self):
        try:
            self.__gen_list()
            self.__output()
        except Exception as e:
            raise

    def __gen_list(self):
        kbn = ""
        lst  = [[] for _ in range(9)]
        term = [[] for _ in range(3)]
        try:
            for year, txt in self.DATS:
                with open(txt, "r", encoding="cp932") as f:
                    for l in f:
                        line = l.rstrip()
                        line = re.sub("^\s+", "", line)
                        if re.search("太陽の", line) is not(None):
                            kbn = "S"
                            lst = [[] for _ in range(9)]
                            continue
                        elif re.search("Ｒ，黄道傾角", line) is not(None):
                            kbn = "R"
                            lst = [[] for _ in range(9)]
                            continue
                        elif re.search("月の", line) is not(None):
                            kbn = "M"
                            lst = [[] for _ in range(9)]
                            continue
                        elif line == "":
                            if kbn == "S":
                                for i in range(3):
                                    self.sun_ra.append(
                                        [year, term[i], lst[i * 3]]
                                    )
                                    self.sun_dec.append(
                                        [year, term[i], lst[i * 3 + 1]]
                                    )
                                    self.sun_dist.append(
                                        [year, term[i], lst[i * 3 + 2]]
                                    )
                            elif kbn == "R":
                                for i in range(3):
                                    self.r.append(
                                        [year, term[i], lst[i * 2]]
                                    )
                                    self.eps.append(
                                        [year, term[i], lst[i * 2 + 1]]
                                    )
                            elif kbn == "M":
                                for i in range(3):
                                    self.moon_ra .append(
                                        [year, term[i], lst[i * 3]]
                                    )
                                    self.moon_dec.append(
                                        [year, term[i], lst[i * 3 + 1]]
                                    )
                                    self.moon_hp .append(
                                        [year, term[i], lst[i * 3 + 2]]
                                    )
                            kbn = ""
                            continue
                        if kbn == "":
                            continue
                        m = re.findall("a\s*=\s*(\d+)\s*,\s*b\s*=\s*(\d+).*a\s*=\s*(\d+)\s*,\s*b\s*=\s*(\d+).*a\s*=\s*(\d+)\s*,\s*b\s*=\s*(\d+)", line)
                        if m != []:
                            term = [
                                [int(m[0][0]), int(m[0][1])],
                                [int(m[0][2]), int(m[0][3])],
                                [int(m[0][4]), int(m[0][5])]
                            ]
                            continue
                        cols = re.split("\s+", line)
                        if re.search("[0-9]+", cols[0]) is None:
                            continue
                        for i in range(1, len(cols) - 1):
                            lst[i - 1].append(float(cols[i]))
        except Exception as e:
            raise

    def __output(self):
        try:
             with open(self.OUT_FILE, "w") as f:
                 f.write(self.__gen_str("SUN_RA",   self.sun_ra  ))
                 f.write(self.__gen_str("SUN_DEC",  self.sun_dec ))
                 f.write(self.__gen_str("SUN_DIST", self.sun_dist))
                 f.write(self.__gen_str("MOON_RA",  self.moon_ra ))
                 f.write(self.__gen_str("MOON_DEC", self.moon_dec))
                 f.write(self.__gen_str("MOON_HP",  self.moon_hp ))
                 f.write(self.__gen_str("R",        self.r       ))
                 f.write(self.__gen_str("EPS",      self.eps     ))
        except Exception as e:
            raise

    def __gen_str(self, name, src):
        try:
            str = "{} = [\n".format(name)
            for row in src:
                str += "    [{}, [{}, {}], ".format(row[0], row[1][0], row[1][1])
                str += "["
                str += ", ".join([
                    "{:.6f}".format(col)
                    if re.search(r"DEC|EPS", name) is None else
                    "{:.5f}".format(col)
                    for col in row[2]
                ])
                str += "]"
                str += "],\n"
            str += "]\n"
            return str
        except Exception as e:
            raise


if __name__ == '__main__':
    try:
        obj = GenCoeffsList()
        obj.exec()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

