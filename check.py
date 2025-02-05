import sqlite3
import os
import MeCab
import json
import xml2json
import shutil
# OpenSearchでは巻数がtitleと別なので，titleを固有名詞として捉える．

_DB_NAME = 'books.db'
_JSON_DIR     = 'OpenSearch_JSON'
_JSON_DONE_DIR  = 'OpenSearch_Done_JSON'
_CSV_TITLE = 'new.csv'
_CSV_META  = 'meta.csv'
if not os.path.isdir(_JSON_DONE_DIR):
    os.mkdir(_JSON_DONE_DIR)


def initDB():
    isExistDB = False
    if os.path.exists(_DB_NAME):
        isExistDB = True
    connection = sqlite3.connect(_DB_NAME, isolation_level=None)
    csr = connection.cursor()
    if not isExistDB:
        sql = """CREATE TABLE books(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT UNIQUE, kana TEXT, category TEXT, author TEXT)"""
        csr.execute(sql)
    csr.close()


_CACHE_SIZE = 5000
cacheSet = set([])
#すでにDBに登録済みか
def hasBookInDB(title):
    if title in cacheSet:
        return True
    connection = sqlite3.connect(_DB_NAME, isolation_level=None)
    csr = connection.cursor()
    sql = """SELECT id, title FROM books WHERE title = "{0}";""".format(title.replace('"','""'))
    csr.execute(sql)
    b = csr.fetchone()
    csr.close()
    if b and len(b) > 0:
        # found
        if len(cacheSet) > _CACHE_SIZE:
            cacheSet.pop()
        cacheSet.add(title)
        return True
    else:
        # not found
        return False

# titleが初出ならDBに登録．既出なら登録しない. 登録できたかをBoolで返す．
def insertBookIntoDB(title,info):
    done = False
    if title in cacheSet:
        return False
    connection = sqlite3.connect(_DB_NAME, isolation_level=None)
    csr = connection.cursor()
    sql = """SELECT id, title FROM books WHERE title = "{0}";""".format(title.replace('"','""'))
    # print(title)
    csr.execute(sql)
    b = csr.fetchone()
    if b and len(b) > 0:
        # found
        # print(title)
        done = False
        # Cacheに追加
        if len(cacheSet) > _CACHE_SIZE:
            cacheSet.pop()
        cacheSet.add(title)
    else:
        # not found
        done = True
        # DBに登録
        sql = """INSERT INTO books(title,kana,author,category) VALUES("{0}","{1}","{2}","{3}")""".format(title.replace('"','""'),info['kana'].replace('"','""'),info['author'].replace('"','""'),info['category'].replace('"','""'))
        csr.execute(sql)
    csr.close()
    return done


mecab = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
def hasBookInNeologd(title):
    node = mecab.parseToNode(title)
    length = 0
    while node:
        length += 1
        node = node.next
    if length == 3: #BOF,EOFもカウントされている
        return True
    else:
        return False

acc={} #ファイルを頻繁に開くと無駄なのである程度ためる
acc_max = 500
# _data is list.      e.g. ['title', 'kana']
# _file is filename   i.e. _CSV_TITLE or _CSV_META
# onAcc is bool.      ためるかどうか
def insertIntoCsvFile(_data,_file,onAcc):
    if onAcc:
        if _file not in acc:
            acc[_file] = []
        if len(acc[_file]) < acc_max:
            acc[_file].append(toCsvFormat(_data))
            return
        data_acc = ''.join(acc[_file]) #acc取り出し
        acc[_file] = []
        # csvファイルに追記
        f = open(_file, 'a')
        f.write(data_acc)
        f.close()
        print('write:'+_file)
    else:
        #最後はACC全部書き込む
        acc[_file].append(toCsvFormat(_data))
        for _f, _acc in acc.items():
            data_acc = ''.join(_acc) #acc取り出し
            # csvファイルに追記
            f = open(_f, 'a')
            f.write(data_acc)
            f.close()
            print('write:'+_f)
        acc[_CSV_META] = [] #accリセット
        acc[_CSV_TITLE]= []

# data_lst is list.  e.g. ['title','kana']
# return '"title","kana"\n'
def toCsvFormat(data_lst):
    ds = []
    for d in data_lst:
        # 文字列中に,があるため""で囲む．文字列中の"は「""」でエスケープ．
        ds.append('"{0}"'.format(d.replace('"','""')))
    return ','.join(ds) + '\n'

if __name__ == '__main__':
    # DBの用意
    initDB()
    # XMLがあればJSONに
    xml2json.xmlToJson()
    # _JSON_DIRにあるjsonファイルを読み込む
    books_dic = {}
    dic_max = 1500
    json_files = os.listdir(_JSON_DIR)
    file_nums = len(json_files)
    print("json files:"+str(file_nums))
    cnt = 0
    allready = 0
    meta_nums = 0
    word_nums = 0
    for jfile in json_files:
        cnt += 1
        f = open(os.path.join(_JSON_DIR,jfile), 'r')
        b_json = json.load(f)
        f.close()
        # 一度読み込んだJSONファイルを除外
        if os.path.exists(os.path.join(_JSON_DONE_DIR,jfile)):
            os.remove(os.path.join(_JSON_DONE_DIR,jfile))
        shutil.move(os.path.join(_JSON_DIR,jfile), _JSON_DONE_DIR)
        # cnt_max回はためる ... 同じタイトル(漫画など)重複分の処理省略，jsonのサイズが小さい場合のDB操作のロスを減らす
        books_dic.update(b_json)
        print(jfile)
        print('book:'+str(len(b_json)))
        print('acc:'+str(len(books_dic)))
        if len(books_dic) < dic_max  and  cnt != file_nums: #最後の時はスキップしない
            continue
        print('DONE -------------')
        books_num = len(books_dic)
        i = 0
        for title, info in books_dic.items():
            i += 1
            #国立国会図書館サーチからの結果で，すでに登録していないかDBでチェック
            if not insertBookIntoDB(title,info):
                # title は既出
                allready += 1
                continue
            # title は初出
            # Neologdに登録されているかでチェック
            if hasBookInNeologd(title):
                #登録済 ... メタ情報と組にする
                _file = _CSV_META
                _data = [title, info['author'], info['category']]
                meta_nums += 1
            else:
                #未登録 ... kanaと組にする
                _file = _CSV_TITLE
                _data = [title, info['kana']]
                word_nums += 1
            if i == books_num:
                onAcc = False
            else:
                onAcc = True
            insertIntoCsvFile(_data, _file, onAcc)
        books_dic = {}
    print('重複回数:'+str(allready))
    print('新語:'+str(word_nums))
    print('メタ:'+str(meta_nums))
