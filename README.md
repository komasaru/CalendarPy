Calendar (Python Ver.)
======================

以下で紹介するスクリプトは全て実行ファイルの作成例であり、計算の本質部分は `lib` ディレクトリ配下のスクリプトである。  
また、 `_i` で終わるディレクトリ配下のスクリプトは、 `lib` ディレクトリ配下のライブラリを使用せず、直接計算するように作成したものである。

jpl_cal.py
----------

### 概要

引数で与えた JST（日本標準時）のカレンダーを、JPL DE430 から天体の正確な位置データを取得して計算する。

### 使用方法

DE430 バイナリデータ(`JPLEPH`)を同じディレクトリ内に配置して、以下のように実行する。

`./jpl_cal.py [YYYYMMDD]`

### 定数データ等の生成について

* 二十四節気、月の朔望の正確な日時は、都度ループ処理による近似計算が必要であるため、予め計算しておいたデータを使用することにしている。
* その他のデータも合わせ、以下のような手順で生成している。
* 二十四節気、月の朔望の定数は、以下の 2-11, 2-12 で生成したものを使用している。

1. DB 生成（権限等も適切に設定する）
  1-1. Database (with `db_script/create_db.sql`)
  1-2. Table    (with `db_script/create_tbl.sql`)
2. カレンダ生成
  2-1.  `jpl_kokei.py 1899 2100`
  2-2.  `jpl_sekki_24.py 1899 2100`
  2-3.  `jpl_moon.py 1899 2100`
  2-4.  `jpl_zassetsu.py 1900 2099` (depend on `calendar`.`dat_kokeis`)
  2-5.  `jpl_holiday.py 1900 2099`  (depend on `calendar`.`dat_sekki24s`)
  2-6.  `jpl_etc.py 1900 2099`      (depend on `calendar`.`dat_moons`)
  2-7.  `jpl_oc.py 1900 2099`       (depend on `calendar`.`dat_sekki24s`, `calendar`.`dat_moons`)
  2-8.  `jpl_db.py 1900 2099`       (depend on all of the above)
  2-9.  `jpl_csv.py 1900 2099`      (depend on `calendar`.`dat_calenars`)
  2-10. `jpl_csv_saku`
  2-11. `jpl_csv_sekki_24`
  2-12. `jpl_cal.py`

---

apparent_sun_moon_jpl.py
------------------------

### 概要

引数で与えた JST（日本標準時）の太陽・月の視位置を計算する。（自作ライブラリを使用）

### 使用方法

`./apparent_sun_moon_jpl.py [YYYYMMDD|YYYYMMDDHHMMSS|YYYYMMDDHHMMSSffffff]`

---

bpn_rotation.py
---------------

### 概要

引数で与えた TDB（太陽系力学時）の指定（スクリプト内に直接記述）の座標にバイアス・歳差・章動を適用する。（自作ライブラリを使用）

### 使用方法

`./bpn_rotation.py [YYYYMMDD|YYYYMMDDHHMMSS]`

---

calc_delta_t.py
---------------

### 概要

引数で与えた年月(UTC（協定世界時）)の地球自転速度の補正値 delta T(ΔT)の計算する。（自作ライブラリを使用）  
「[NASA - Polynomial Expressions for Delta T](http://eclipse.gsfc.nasa.gov/SEcat5/deltatpoly.html)」の計算式を使用する。  
但し、 1972年 - 2018年は、比較対象として「うるう年総和 + 32.184(TT - TAI)」の値も計算する。

### 使用方法

`./calc_delta_t.py [[+-]YYYYMM]`

---

conv_coord.py
-------------

### 概要

指定の座標（スクリプト内に直接記述）の赤道・黄道座標変換を行う。（黄道傾斜角は固定）（自作ライブラリを使用）

### 使用方法

`./conv_coord.py`

---

conv_time.py
------------

### 概要

引数で与えた JST（日本標準時）を各種時刻系に換算する。（自作ライブラリを使用）

### 使用方法

`./conv_time.py [YYYYMMDD|YYYYMMDDHHMMSS|YYYYMMDDHHMMSSUUUUUU]`

---

ephemeris_jpl.py
----------------

### 概要

引数で与えた対象天体・基準天体・ユリウス日の ICRS 座標（位置・速度）を、JPLEPH（JPL の DE430 バイナリデータ）読み込んで計算する。（自作ライブラリを使用）

### 使用方法

`./ephemeris_jpl.py <対象店対番号> <基準天体番号> <ユリウス日>`

* 天体番号等については、 `ephemeris_jpl.py` 内のコメントを参照。

---

mean_obliquity_ecliptic.py
--------------------------

### 概要

引数で与えた TT（地球時）の平均黄道傾斜角を計算する。（自作ライブラリを使用）

### 使用方法

`./mean_obliquity_ecliptic.py [YYYYMMDD|YYYYMMDDHHMMSS]`

---

nutation_model.py
-----------------

### 概要

引数で与えた TT（地球時）の章動を、 IAU2000A 章動理論(MHB2000, IERS2003) を用いて計算する。（自作ライブラリを使用）

### 使用方法

`./nutation_model.py [YYYYMMDD|YYYYMMDDHHMMSS]`

