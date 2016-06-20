Python3.0


[description]
  book.py      ... OpenSearch_XMLに書籍情報をダウンロード．
  xml2json.py  ...  XMLから情報抽出しJSONに．OpenSearch_JSONに蓄積．
  check.py     ...  JSONを読み込んでNeologdでチェック．CSVファイルに新しい情報を蓄積．
[use]
  book.pyでxmlをDL．
  check.pyで新語発見．



・book.py
  国立国会図書館サーチから書籍情報を取得．
  1分おきにリクエスト(普通に使う分には無許可で良いが，商用・負荷をかける場合には許可がいるため，アクセス頻度を少なく)
  xml形式でOpenSearch_XMLディレクトリに保存していく．
  2016-06を遡って月ごとにダウンロード．
  今後発売される本に関しては未実装．
  (xmlを保存せずにjsonで保存すべきだが，念のために保持．デバッグ時のリクエスト数を減らす)
  [use]
    startGetBookInfos.sh でバックグラウンドでプロセス起動．
    checkPID.sh で動作中か確認．
    killGetBookInfos.sh でプロセス終了．

・xml2json.py
  OpenSearch_XMLディレクトリにあるxmlファイルを必要な情報だけ抽出しjson形式で
  OpenSearch_JSONディレクトリに保存していく．
  変換した後のxmlファイルはOpenSearch_Done_XMLディレクトリに移動．
  [use] (check.pyで使用)
    import xml2json
    xmlToJson()

・check.py
  OpenSearch_JSONディレクトリからjsonファイルを読み込み，
  まだ既出(DBでチェック)であるか確認し，[1 or 2]の処理をする．
    1. Neologdに未登録 ... 読みと組でnew.csvファイルに書き込み
    2. Neologdに登録済 ... メタ情報と組でmeta.csvファイルに書き込み
  チェックし終わったjsonファイルはOpenSearch_Done_JSONディレクトリに移動．
  [use]
    python check.py



収集1回目
mediatype:4 児童書
mediatype:1 本
NDC:7 芸術

収集2回目
NDC:
913: 日本文学 小説・物語
726: 絵画 漫画・挿絵・童画
930: 英米文学
911: 日本文学 詩歌

収集3回目
28 : 伝記
03 : 百科事典
08 : 叢書・全集・選集
76 : 音楽
778: 映画
79 : 諸芸、娯楽

収集4回目
21 : 日本史
81 : 日本語
914: 日本文学 評論、エッセイ、随筆
915: 日本文学 日記、書簡、紀行

16 : 宗教
19 : キリスト教
23 : ヨーロッパ史、西洋史
35 : 財政
