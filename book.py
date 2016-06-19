try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import os.path
import datetime
import re
import os
import time
from xml.sax.saxutils import unescape

# OpenSearch mediatype option
_MEDIATYPE_BOOK    = '1' #本
_MEDIATYPE_ARTICLE = '2' #記事・論文
_MEDIATYPE_NEWS    = '3' #新聞
_MEDIATYPE_CHILD   = '4' #児童書
_MEDIATYPE_REF     = '5' #レファレンス情報
_MEDIATYPE_DIGITAL = '6' #デジタル資料
_MEDIATYPE_OTHER   = '7' #その他
_MEDIATYPE_DISAB   = '8' #障がい者向け資料
_MEDIATYPE_LEGI    = '9' #立法情報

# 一度に取得する検索結果数(最大500件)
_SCOUNT = '500'
# 検索結果の件数情報取得のための正規表現
_RE_TOTAL_ = re.compile(r'<openSearch:totalResults>([0-9]+)</openSearch:totalResults>')
_RE_INDEX_ = re.compile(r'<openSearch:startIndex>([0-9]+)</openSearch:startIndex>')

# OpenSearch WebAPI
#REQ_FORMAT = 'http://iss.ndl.go.jp/api/opensearch?from=__FROM__&until=__UNTIL__&mediatype='+_MEDIATYPE+'&cnt='+_SCOUNT+'&idx=__INDEX__'
#REQ2_FORMAT = 'http://iss.ndl.go.jp/api/opensearch?from=__FROM__&until=__UNTIL__&ndc=7&cnt='+_SCOUNT+'&idx=__INDEX__'
REQ_FORMATS = ['http://iss.ndl.go.jp/api/opensearch?from=__FROM__&until=__UNTIL__&mediatype='+_MEDIATYPE_CHILD+'&cnt='+_SCOUNT+'&idx=__INDEX__',
               'http://iss.ndl.go.jp/api/opensearch?from=__FROM__&until=__UNTIL__&mediatype='+_MEDIATYPE_BOOK+'&cnt='+_SCOUNT+'&idx=__INDEX__',
               'http://iss.ndl.go.jp/api/opensearch?from=__FROM__&until=__UNTIL__&ndc=7&cnt='+_SCOUNT+'&idx=__INDEX__' ]

# XML保存ディレクトリの作成
_SAVE_DIR = 'OpenSearch_XML'
if not os.path.isdir(_SAVE_DIR):
    os.mkdir(_SAVE_DIR)




# 検索の期間を整形した形で返す(argから一ヶ月間).
# arg is 'y-m'.  e.g. 2016-06
# from  : いつから取得するか   e.g. 2016-06-02
# until : いつまでを取得するか  e.g. 2016-07-01
# lastM : 次の開始年月(先月)を'year-month'で返す ... (過去の検索用,遡っていく)
def getRequestBDateInfos(y_m):
    y = int(y_m.split('-')[0])
    m = int(y_m.split('-')[1])
    # until
    umonth = m+1 if m < 12 else 1
    uyear  = str(y+1) if m == 12 else str(y)
    umonth = '0'+str(umonth) if umonth < 10 else str(umonth)
    # last month
    lmonth = m-1 if m > 1 else 12
    lyear  = str(y-1) if m == 1 else str(y)
    lmonth = '0'+str(lmonth) if lmonth < 10 else str(lmonth)
    # from
    y = '0'+str(y) if y < 10 else str(y)
    m = '0'+str(m) if m < 10 else str(m)
    return {'from' :y+'-'+m+'-02',
            'until':uyear+'-'+umonth+'-01',
            'next':lyear+'-'+lmonth }

def requestOpenSearchBackward():
    datefile_path = os.path.join(_SAVE_DIR,'.date_before')
    # リクエスト年月の設定
    if os.path.exists(datefile_path): #再開
        f = open(datefile_path, 'r')
        c = f.read().split(',')
        b_date = c[0].split('=')[1]
        b_idx  = c[1].split('=')[1]
        f.close()
    else: #新規
        today = datetime.date.today()
        t_y = str(today.year)
        t_m = '0'+str(today.month) if today.month < 10 else str(today.month)
        b_date = t_y+'-'+t_m
        b_idx  = '1'
    # 再開月にまだ検索結果が残っているかどうか
    isReminder = True if b_idx != '1' else False
    BDateInfos = getRequestBDateInfos(b_date)

    # リクエスト発行
    for i,req in enumerate(REQ_FORMATS):
        time.sleep(1)
        url = req.replace('__FROM__',BDateInfos['from']).replace('__UNTIL__',BDateInfos['until']).replace('__INDEX__', str(1+(int(b_idx)-1)*int(_SCOUNT)) )
        response = urllib2.urlopen(url)
        xml = unescape( response.read().decode('utf-8') ) #&ampなどのエスケープ文字をなおす

        # 結果を保存
        result_file = b_date+'_'+b_idx+'_req'+str(i)+'.xml'
        f = open(_SAVE_DIR+'/'+result_file,'w')
        f.write(xml)
        f.close()

    # 検索結果がまだ残っているか
    total = _RE_TOTAL_.search(xml).group(1)
    index = _RE_INDEX_.search(xml).group(1)
    if not (total and index): #正規表現にマッチしない場合
        return 0 #たぶんない．(もしなった場合のスキップ処理を用意すべき)
    if int(index)*int(_SCOUNT) < int(total):
        # 残っている. dateはそのままでindexを+1
        contents = 'date='+b_date+',index='+str(int(index)+1)
    else:
        # 残っていない. dateを次にしてindexを1に戻す.
        contents = 'date='+BDateInfos['next']+',index=1'

    # 次回のリクエスト年月を保存
    f = open(datefile_path, 'w')
    # もし検索結果が途中なら続きをリクエスト
    f.write(contents)
    f.close()

if __name__ == '__main__':
    while True:
        requestOpenSearchBackward()
        time.sleep(5)
# [.date_before] -------------------------------
# contents is 'date=2016-6,index=1'
# date : 取得開始日
# index: 検索結果のindex. index > 1 ならまだ検索結果に続きがある(500件しか取得できない).
