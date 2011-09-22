========
pymeshio
========
http://meshio.sourceforge.jp/

pmdとmqoの読み書きライブラリと、それを使ったblender2.5x向けaddonです。

package方法
===========
$ python setup.py sdist

blender-2.5x addonのインストール
===============================
アーカイブを解凍すると中にblender25-meshioというディレクトリができます。
これを、
{blender2.5xのインストールディレクトリ}/2.5x/scripts/addons
にコピーしください。

次にblenderを起動して、(File)-(User Preferences)をオープン。
(Add-Ons)タブを選択。

Import-Exportの中から"meshio. (.pmd)(.mqo)"を探して右のチェックボックスを有効にします。これでaddonが有効になり、(File)メニューの(Import)と(Export)それぞれにpmdとmqoが現れます。

Save As Defaultを押しておくと次回起動から(Uesr Preferences)以降を省略できます。

更新履歴
========
20110918 1.9.0
--------------
blender2.59に対応
剛体関連でなんか修正したらしい
mqo exportの修正

20110607 1.8.6
--------------
pmd exportの法線を修正。

20110530 1.8.5
--------------
cubeなどの単純形状をエクスポートできるように修正。

20110523 1.8.4
--------------
blender2.57bより新しくしてしまったのを修正。

20110523 1.8.3
--------------
python3のstrとbytesの使い分けをミスっていたのを修正。

20110522 1.8.2
--------------
python3向けの修正。
RigidBodyとConstrainの書き出し。

20110521 1.8.1
--------------
fix io_utils -> bpy_extras.io_utils

20110521 1.8.0
--------------
RigidBodyとConstraintの読み込みを実装。

20110518 1.7.0
--------------
setup.pyとtest導入。
python2と3両用に改造。

20110429 1.06
-------------
MeshIOからリポジトリを分離。
blender2.57b向け修正。
blender2.49サポートを終了。

20101229 1.05
-------------
blender2.55向け修正。

