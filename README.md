# 概要
このプログラムは、読み込まれた単旋律ギタータブ譜の音高を変化させ、初心者用のタブ譜を出力するプログラムです。
`main.py`でファイル名を書いて実行すると、出力されます。

## データの用意
現在`XML`ディレクトリにMusicXMLファイルが入っています。
自分で用意したい場合は、museScoreでギターのタブ譜を作成し、エクスポートでMusicXMLファイルにできます。

## 必要なライブラリ
このプログラムを動かすのに必要なライブラリは以下の通りです。
以下のコマンドで、`music21`、`glob`、`itertools`、`numpy`、`os`をインストールしてください。

```bash
pip install music21 glob itertools numpy os
