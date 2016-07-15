# FindNewWordsForNeologd
## Overview
形態素解析器MeCab用の新語辞書である[mecab-ipadic-neologd](https://github.com/neologd/mecab-ipadic-neologd)に登録されていない単語(書籍名)と読み仮名のペアを収集する．書籍名は国立国会図書館サーチのAPIを用いて収集する．


## 実行環境
次の環境で動作を確認済み．
 - Python 3.5.0
 - OS X El Capitan Version10.11.5
 - MeCab 0.996
 - mecab-ipadic-neologd 20160613-01 release
 - SQLite 3.8.10.2

## 使用方法
国立国会図書館サーチからの書籍情報を持つXMLの取得と単語と読み仮名のペアの収集に処理が分かれている．
```
$ python book.py
```

月ごとの書籍情報のXMLを過去に遡って取得する．.data_beforeファイルにいつまで遡って取得したか記録しているため，続きから取得可能である．

```
$ python check.py
```

書籍情報のXMLがあればそのファイルに含まれる未登録の単語(書籍名)と読み仮名のペアをnew.csvに保存する．
	
## ファイル構成
### 実行用スクリプト
 - book.py

 	OpenSerach_XMLディレクトリを作成し，国立国会図書館サーチから取得する書籍情報を持つXMLを保存する．
 
 - check.py

    OpenSerach_XMLディレクトリXMLファイルがあればXMLから未登録単語を捜し，new.csvに追記保存する．
    
 - startGetBookInfo.sh

    バックグラウンドでbook.pyのプロセスを起動する．
    
 - endGetBookInfo.sh

	startGetBookInfo.shで開始したプロセスを終了させる．

### 補助スクリプト
 - xml2json.py
    XMLをJson形式に変換する．check.pyで使用している．
 - checkProcess.sh
	startGetBookInfo.shで起動したプロセスが実行中か確認する．


## 補足
国立国会図書館サーチのAPIは普通に使うには無許可でよいが，商用・負荷をかける場合には許可がいるため，アクセス頻度を少なくするように注意されたし．
