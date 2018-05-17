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

* 二十四節気、月の朔望の正確な日時は、都度ループ処理による近似計算が必要であるため、別途計算しておいたデータを使用することにしている。（`lib` ディレクトリ内の `const_saku.py`, `const_sekki_24.py`）
* 二十四節気、月の朔望の正確な日時等を予め計算するスクリプトも作成しているが、ここでは非公開とする。

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

