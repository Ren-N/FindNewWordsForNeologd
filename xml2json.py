import os
import shutil
import re
import json
import codecs
from xml.sax.saxutils import unescape
# 月ごとにファイルを作るのは無駄だが，随時新しいのが作られる事を想定して，統合・重複削除はDBでやる.

_RE_BOOK     = re.compile(r'<item>(.+?)</item>',re.DOTALL)
_RE_TITLE    = re.compile(r'<dc:title>(.+?)</dc:title>',re.DOTALL)
_RE_KANA     = re.compile(r'<dcndl:titleTranscription>(.+?)</dcndl:titleTranscription>',re.DOTALL)
_RE_CATEGORY = re.compile(r'<category>(.+?)</category>',re.DOTALL)
_RE_AUTHOR   = re.compile(r'<author>(.+?)</author>',re.DOTALL) #authorは末尾に,が入っている場合がある. creatorを,で連結した方が楽．
_RE_CREATOR  = re.compile(r'<dc:creator>(.+?)</dc:creator>',re.DOTALL)

_XML_DIR      = 'OpenSearch_XML'
_XML_DONE_DIR = 'OpenSearch_XML_old' #一応使い終わったものもとっておく．
_JSON_DIR     = 'OpenSearch_JSON'
_IGNORE_FILE  = ['.date_before']
if not os.path.isdir(_JSON_DIR):
    os.mkdir(_JSON_DIR)
if not os.path.isdir(_XML_DONE_DIR):
    os.mkdir(_XML_DONE_DIR)

def convtJson(xml_txt):
    books = {} #{title:{author:... , } , title2:{...}}
    for book in _RE_BOOK.findall(xml_txt):
        title = _RE_TITLE.search(book)
        if title:
            title = title.group(1)
        else:
            continue
        if title not in books:
            kana = _RE_KANA.search(book)
            category = _RE_CATEGORY.search(book)
            author = ','.join(_RE_CREATOR.findall(book))
            if kana and category and (len(author)>0):
                kana = kana.group(1)
                category = category.group(1)
            else:
                continue
            books[title] = {'kana':kana,
                            'author':author,
                            'category': category}
    return books

# if __name__ == '__main__':
def xmlToJson():
    for xml in os.listdir(_XML_DIR):
        # XML読み込み
        if xml in _IGNORE_FILE:
            continue
        f = open(os.path.join(_XML_DIR,xml), 'r')
        cts = unescape(f.read())
        f.close()
        # JSON形式で保存
        b_json = convtJson(cts)
        if len(b_json) == 0:
            continue
        f=codecs.open(os.path.join(_JSON_DIR,xml.replace('.xml','.json')),'w','utf-8')
        json.dump(b_json,f, indent=2, ensure_ascii=False)
        f.close()
        # 一度読み込んだXMLファイルを除外
        shutil.move(os.path.join(_XML_DIR,xml), _XML_DONE_DIR)
