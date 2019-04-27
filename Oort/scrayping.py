import csv
import datetime

# 別途pycharm上でインストールが必要
import requests
from bs4 import BeautifulSoup

from urllib.parse import urljoin
import os

from telephone_range.settings import MEDIA_ROOT
from .models import Content, Genre, Director, Cast


class DirectImport():
    MOVIES_URL = 'https://filmarks.com/movies/'

    def scrape(self, start, end):
        for i in range(start, end):

            # ルートURLに数値を加算していき、responseに格納
            url = urljoin(self.MOVIES_URL, str(i))
            response = requests.get(url)

            # ページが404の場合はスキップ
            if response.status_code == 404:
                continue

            # ページ内容を取り出しやすいデータに変えてsoupへ格納
            soup = BeautifulSoup(response.content, 'html.parser')

            content, created = Content.objects.update_or_create(id=i)
            print('ID:', i)

            # タイトル
            title = soup.h2.span.string
            content.title = title

            # サムネイル
            # findでさらに抽出。altにタイトルが入ってる。get('src')は画像link
            src = soup.find('img', alt=title).get('src')

            # 拡張子がsvg(画像データがないもの)じゃなかった場合。つまり通常処理
            # html側で拡張子svgが指定されているが、実際には画像データないパターンのため
            extention = str(src)[-4:]
            if extention != '.svg':
                # 画像データを取得
                r = requests.get(src)

                # ローカル側でオブジェクトを作って、取得した画像データを入れ込む。wb書き込み？
                with open(os.path.join(MEDIA_ROOT, 'image\\' + str(i) + '.jpg'), 'wb') as file:
                    file.write(r.content)

                content.thumbnail = '/image/' + str(i) + '.jpg'

            else:
                # 画像データがsvg(画像データがないもの)だった場合。
                content.thumbnail = ''

            # リリース日、制作国、上映時間を取得
            h3_set = soup.select('h3.p-content-detail__other-info-title')
            h3_dict = {}
            for itr in h3_set:
                itr_str = itr.string.split('：')
                h3_dict[itr_str[0]] = itr_str[1]

            if '上映日' in h3_dict:
                if '月' in h3_dict['上映日']:
                    release_date = h3_dict['上映日'].replace('年', '-').replace('月', '-').replace('日', '')
                else:
                    release_date = h3_dict['上映日'].replace('年', '-') + '01-01'

                content.release = release_date
            else:
                content.release = '1900-01-01'

            if '製作国' in h3_dict:
                country = h3_dict['製作国']
                content.country = country
            else:
                content.country = ''

            # if '上映時間' in h3_dict:
            #     duration = int(h3_dict['上映時間'].replace('分', ''))
            #     duration_delta = datetime.timedelta(minutes=duration)
            #     content.release = duration_delta
            # # else:
            #     content.payback_time = ''

            # ジャンル
            genre = soup.select_one('div.p-content-detail__genre')

            try:
                content_genre = genre.ul.li.a.string
                content.genre, _ = Genre.objects.get_or_create(genre=content_genre)
            except AttributeError:
                content.genre = Genre.objects.get(genre='不明')

            # 監督
            try:
                director = soup.select_one('a.c-label')
                if director is not None:
                    content_director = director.string
                    content.director, _ = Director.objects.get_or_create(name=content_director)
                else:
                    content.director = Director.objects.get(name='不明')

            except AttributeError:
                content.director = Director.objects.get(name='不明')

            content.save()

            # キャスト
            cast_soup = soup.find('div', class_='p-content-detail__people-list-casts')

            try:
                for cast in cast_soup.select('a.c-label'):
                    content_cast, _ = Cast.objects.get_or_create(name=cast.string)
                    content.cast.add(content_cast)

            except AttributeError:
                content.cast.add(Cast.objects.get(name='不明'))

            content.save()
