========
pymeshio
========
http://meshio.sourceforge.jp/

pmdとmqoの読み書きライブラリと、それを使ったblender2.57b向けaddonです。

インストール
============
アーカイブを解凍すると中にmeshioというディレクトリができます。
これを、
{blender2.57bのインストールディレクトリ}/2.57/scripts/addons
にコピーしください。

次にblenderを起動して、(File)-(User Preferences)をオープン。
(Add-Ons)タブを選択。
Import-Exportの中から"meshio. (.pmd)(.mqo)"を探して右のチェックボックスを有効にします。これでaddonが有効になり、(File)メニューの(Import)と(Export)それぞれにpmdとmqoが現れます。

更新履歴
========

20110518 1.10
-------------
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

