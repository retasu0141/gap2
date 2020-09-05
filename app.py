# インストールしたパッケージのインポート
from flask import Flask, render_template, request, redirect, url_for, make_response
from pytrends.request import TrendReq  #グーグルトレンドの情報取得
import pandas as pd  #データフレームで扱う
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import datetime
import codecs
from datetime import date, datetime, timedelta
from io import BytesIO
import urllib
import os,io
import base64
import json
import urllib.request

# appという名前でFlaskのインスタンスを作成
PEOPLE_FOLDER = os.path.join('static', 'photo')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
data = {
    'keyword': ''
}


def download(day):
	url = 'https://trends.google.com/trends/api/dailytrends?geo=JP&ed={}'.format(day)
	title = 'trends{}.txt'.format(day)
	urllib.request.urlretrieve(url,"{0}".format(title))
	with open(title) as f:
		data = f.read()
	data = data[5:]
	jsondata = json.loads(data.encode('utf-16be'))
	with open('trends{}.json'.format(day), 'w') as f:
		json.dump(jsondata, f)


@app.route('/')
def main():
    return render_template('form.html')

@app.route('/post', methods=['GET', 'POST'])
def index():
    plt.figure()
    plot_url = ''
    img = ''
    if request.method == 'POST':
        plt.clf()
        #os.remove("static\photo\img.png")

        keyword = request.form['name']
        # 今日
        today = date.today()

        # 30日前
        day = today - timedelta(30)

        #print(day)

        dt_now = datetime.now()

        dt_now_s = str(dt_now.microsecond)
        pytrends = TrendReq(hl='ja-JP', tz=360)
        #keyword=''
        kw_list = [keyword]
        pytrends.build_payload(kw_list, cat=0, timeframe=str(day)+' '+str(today), geo='JP', gprop='')
        df = pytrends.interest_over_time() #時系列データを取り出す
        df.to_csv(dt_now_s+".csv", encoding='cp932')
        #関連トピック
        df = pytrends.related_topics()
        #トップ
        try:
            text_ = df[keyword]['top'].loc[:,['topic_title']].head(10)
            text__ = text_['topic_title']
            _text = '\n・'.join(text__)
            text = _text.replace('Name: topic_title, dtype: object', '')
        except:
            text = 'なし'
        #上昇
        try:
            text2_ = df[keyword]['rising'].loc[:,['topic_title']].head(10)
            text2__ = text2_['topic_title']
            _text2 = '\n・'.join(text2__)
            text2 = _text2.replace('Name: topic_title, dtype: object', '')
        except:
            text2 = 'なし'


        #関連キーワード
        df = pytrends.related_queries()
        #トップ
        try:
            text3_ = df[keyword]['top'].head(10)
            text3__ = text3_['query']
            _text3 = '\n・'.join(text3__)
            text3 = _text3.replace('Name: query, dtype: object', '')
        except:
            text3 = 'なし'
        #上昇
        try:
            text4_ = df[keyword]['rising'].head(10)
            text4__ = text4_['query']
            _text4 = '\n・'.join(text4__)
            text4 = _text4.replace('Name: query, dtype: object', '')
        except:
            text4 = 'なし'

        #print(keyword+'.csv')

        df = pd.read_csv(dt_now_s+'.csv',encoding='cp932')


        '''
        print(df)
        print(df.columns)
        print(df['date'])
        print(df[keyword])
        '''
        img = io.BytesIO()
        #グラフの作成
        fig = plt.figure()
        plt.figure(1)
        plt.plot(df['date'],df[keyword],marker="o")
        #グラフの軸
        plt.xlabel(df['date'].name)
        plt.ylabel(keyword)

        #canvas = FigureCanvasAgg(fig)
        #canvas.print_png(buf)
        #data = buf.getvalue()

        plt.savefig(img, format='png')
        img.seek(0)

        plot_url = base64.b64encode(img.getvalue()).decode()

        #plt.savefig("static\photo\img.png")
        #plt.close()
        #fig.savefig("static\img.png")
        #full_filename = os.path.join(app.config['UPLOAD_FOLDER'], "img.png")

        #グラフ表示
        #plt.show()
        #return '<img src="data:image/png;base64,{}">'.format(plot_url)
        return render_template('choice.html',text=text,text2=text2,text3=text3,text4=text4,img="data:image/png;base64,{}".format(plot_url))

@app.route('/today', methods=['GET', 'POST'])
def today():

    today__ = date.today()
    #yesterday__ = today - timedelta(1)
    today_ = str(today__)
    today = today_.replace('-', '')
    #yesterday_ = str(yesterday__)
    #yesterday = yesterday_.replace('-', '')

    download(today)


    JSON_FILE = 'trends{}.json'.format(today)
    with open(JSON_FILE) as f:
        data = json.load(f)
	#print(json.dumps(data,ensure_ascii=False, indent=2))
    kye1 = data['default']['trendingSearchesDays']
    kye2 = kye1[0]


    day = kye2['date']
    formattedDate = kye2['formattedDate']
    #トレンドは20個ある
    #print(len(kye2['trendingSearches']))
    #→20

    kye3 = kye2['trendingSearches']
    #トレンド1位
    T1 = kye3[0]
    #トレンドのタイトル
    T1title = T1['title']['query']
    #検索件数
    T1search = T1['formattedTraffic']
    #検索結果の関連(リスト) T1relatedQueries_list
    T1relatedQueries = T1['relatedQueries']
    T1relatedQueries_list = []
    for kye in T1relatedQueries:
    	T1relatedQueries_list.append(kye['query'])
    #記事
    #記事は6つある
    #print(len(T1['articles']))
    #→6
    for kye in T1['articles']:
    	pass

    #トレンドを全部とる
    trendlist = [] #トレンドリスト
    for kye in kye3:
    	trendlist.append(kye['title']['query'])
    #トレンドの検索回数を全部とる
    trendlist_2 = [] #検索回数リスト
    for kye in kye3:
    	trendlist_2.append(kye['formattedTraffic'])
    #トレンドの関連を全部とる
    trendlist_3 = []
    for kye in kye3:
    	hogelist = []
    	for kye2 in kye['relatedQueries']:
    		hogelist.append(kye2['query'])
    	trendlist_3.append(hogelist)
    numbers = list(range(1,20))

    text_list = []
    #'トレンド{number}位{1}。検索回数{2}。関連{3}。'
    for number,rank,search,Relation in zip(numbers,trendlist,trendlist_2,trendlist_3):
    	txt = 'トレンド{n}位{r}。検索回数{s}。関連{re}。'.format(n=number,r=rank,s=search,re=Relation)
    	text_list.append(txt)



    #text = '\n'.join(text_list)
    return render_template('day.html',text_list=text_list)

@app.route('/yesterday', methods=['GET', 'POST'])
def yesterday():

    today__ = date.today()
    yesterday__ = today__ - timedelta(1)
    yesterday_ = str(yesterday__)
    yesterday = yesterday_.replace('-', '')

    download(yesterday)

    JSON_FILE = 'trends{}.json'.format(yesterday)
    with open(JSON_FILE) as f:
        data = json.load(f)
	#print(json.dumps(data,ensure_ascii=False, indent=2))
    kye1 = data['default']['trendingSearchesDays']
    kye2 = kye1[0]


    day = kye2['date']
    formattedDate = kye2['formattedDate']
    #トレンドは20個ある
    #print(len(kye2['trendingSearches']))
    #→20

    kye3 = kye2['trendingSearches']
    #トレンド1位
    T1 = kye3[0]
    #トレンドのタイトル
    T1title = T1['title']['query']
    #検索件数
    T1search = T1['formattedTraffic']
    #検索結果の関連(リスト) T1relatedQueries_list
    T1relatedQueries = T1['relatedQueries']
    T1relatedQueries_list = []
    for kye in T1relatedQueries:
    	T1relatedQueries_list.append(kye['query'])
    #記事
    #記事は6つある
    #print(len(T1['articles']))
    #→6
    for kye in T1['articles']:
    	pass

    #トレンドを全部とる
    trendlist = [] #トレンドリスト
    for kye in kye3:
    	trendlist.append(kye['title']['query'])
    #トレンドの検索回数を全部とる
    trendlist_2 = [] #検索回数リスト
    for kye in kye3:
    	trendlist_2.append(kye['formattedTraffic'])
    #トレンドの関連を全部とる
    trendlist_3 = []
    for kye in kye3:
    	hogelist = []
    	for kye2 in kye['relatedQueries']:
    		hogelist.append(kye2['query'])
    	trendlist_3.append(hogelist)
    numbers = list(range(1,20))

    text_list = []
    #'トレンド{number}位{1}。検索回数{2}。関連{3}。'
    for number,rank,search,Relation in zip(numbers,trendlist,trendlist_2,trendlist_3):
    	txt = 'トレンド{n}位{r}。検索回数{s}。関連{re}。'.format(n=number,r=rank,s=search,re=Relation)
    	text_list.append(txt)



    #text = '\n'.join(text_list)
    return render_template('day.html',text_list=text_list)

if __name__ == '__main__':
    # 作成したappを起動
    # ここでflaskの起動が始まる
    #app.debug = True
    app.run()