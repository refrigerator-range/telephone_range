import csv
from io import TextIOWrapper

from dal import autocomplete
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse, HttpResponseRedirect
# インポート用render
from django.shortcuts import render
from django.template import loader
from django.urls import reverse, reverse_lazy
from django.views import generic

from Oort.form import ContentForm, GenreForm, CastForm, DirectorForm, CSVUploadForm, DirectImportForm
from Oort.scrayping import DirectImport
from .models import Content, Cast, Director, Genre


# ページネート用
def pagenate_query(request, queryset, count):
    # コンテンツ全部もってきてカウント毎に区切る
    paginator = Paginator(queryset, count)

    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj


def IndexViews(request):
    if request.method == 'GET':
        # コンテンツ情報を全部取ってくる
        lists = Content.objects.all()

        pg = pagenate_query(request, lists, 10)

        # 表示するHTMLはindex.html。ページネイトはincludeしている
        template = loader.get_template('Oort/index.html')

        # foo(html側の箱)とpg(Page 1 of 11とか)をマッピングしてcontextに格納
        context = {
            'foo': pg,
        }
        print('コンテキスト', context)
        # クライアントにrenderingするようレスポンスする。ページネイト情報(context)も一緒に渡す
        return HttpResponse(template.render(context, request))

    # 削除用
    if 'delete' in request.POST:
        # コンテンツ情報を全部取ってくる
        lists = Content.objects.all()

        # 表示するHTMLはindex.html
        template = loader.get_template('Oort/index.html')

        # foo(html側の箱)とlists(コンテンツ情報)をマッピングしてcontextにいれてる
        context = {
            'foo': lists,
        }
        # index.htmlの削除ボタンに入ってるcontent_idを抜き出す
        print('リクエストポスト', request.POST)
        content_id = request.POST['delete']
        print('コンテンツID', content_id)
        # モデルに渡して削除する
        Content.objects.get(pk=content_id).delete()

        # クライアントにrenderingするようレスポンスする
        return HttpResponse(template.render(context, request))

    # 検索用
    if 'word' in request.POST:
        word = request.POST['word']
        # 入力値wordにマッチしたコンテンツ情報を取ってくる
        lists = Content.objects.filter(title__contains=word)

        # 表示するHTMLはindex.html
        template = loader.get_template('Oort/index.html')

        # foo(html側の箱)とlists(コンテンツ情報)をマッピングしてcontextにいれてる
        context = {
            'foo': lists,
        }

        # クライアントにrenderingするようレスポンスする
        return HttpResponse(template.render(context, request))


# detail関数。コンテンツIDもゲットしてくる。
def detail(request, content_id):
    if request.method == 'GET':
        # object.getで1レコードだけ取る。pkはprimary keyのこと。
        record = Content.objects.get(pk=content_id)

        # 表示するHTMLはdetail.html
        template = loader.get_template('Oort/detail.html')
        # movie(HTML側の箱)とrecord(コンテンツ情報の１レコード)をマッピング
        context = {
            'movie': record,
        }
        return HttpResponse(template.render(context, request))


# 登録フォーム用
def register(request):
    # GETの場合
    if request.method == 'GET':
        template = loader.get_template('Oort/register.html')
        form = ContentForm()
        genre_form = GenreForm()
        cast_form = CastForm()
        dir_form = DirectorForm()

        context = {'form': form,
                   'genre_form': genre_form,
                   'cast_form': cast_form,
                   'dir_form': dir_form}

        # render関数は辞書型を第一引数に指定しないといけないのでformを指定
        return HttpResponse(template.render(context, request))

    # POSTの場合
    if request.method == 'POST':

        # URLの逆引き。register 名前(register)からURLを引く
        # リバース。
        url = reverse('Oort:register')

        # コンテンツ登録用
        if 'content' in request.POST:
            # request.FILESがファイルを扱うための引数
            form = ContentForm(request.POST, request.FILES)

            # バリッド(バリデーション)。実際にDBに登録するところ
            if form.is_valid():
                # フォームの中でcastを抜き出す⇒casts（for文を回すため）
                casts = form.cleaned_data['cast']
                # フォームからcastを削除(辞書から削除)
                del form.cleaned_data['cast']
                # フォームから１レコード作成。この時castは削除したのでNULLとして
                new_cont = Content.objects.create(**form.cleaned_data)

                # casts分(複数個)データを改めて１レコードに追加。
                for cast in casts:
                    new_cont.cast.add(cast)

                return HttpResponseRedirect(url)

        # ジャンル登録用。'genre'はregister.htmlのボタンnameと合わせる。何故かgenreだけでは通らない
        if 'genre' in request.POST:
            genre_form = GenreForm(request.POST)
            if genre_form.is_valid():
                Genre.objects.create(**genre_form.cleaned_data)
                return HttpResponseRedirect(url)

        # キャスト登録用。
        if 'cast' in request.POST:
            cast_form = CastForm(request.POST)
            if cast_form.is_valid():
                Cast.objects.create(**cast_form.cleaned_data)
                return HttpResponseRedirect(url)

        # 監督登録用。
        if 'director' in request.POST:
            dir_form = DirectorForm(request.POST)
            if dir_form.is_valid():
                Director.objects.create(**dir_form.cleaned_data)
                return HttpResponseRedirect(url)


# インポート用。ファイルかDB直接かでpost内で場合分け
class Import(generic.FormView):
    template_name = 'Oort/import.html'
    success_url = reverse_lazy('Oort/index.html')
    form_class = CSVUploadForm
    # d_class = DirectImport

    def get(self, request):
        form = self.form_class(request.GET)
        return render(request, self.template_name, {'form': form})

    def post(self, request):

        # ファイル経由インポート用分岐
        if 'import' in request.POST:

            # ファイル受け取りチェック
            if 'file' in request.FILES:

                form_data = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
                csv_file = csv.reader(form_data)
                # dura = timedelta(seconds=60)

                for line in csv_file:
                    print('ライン:', line)
                    # contentにモデル格納用、createdにTure or False
                    # contentは、既存idならupdate。新規idならcreate
                    content, created = Content.objects.update_or_create(id=line[0])
                    content.id = line[0]
                    content.title = line[1]
                    content.thumbnail = line[2]
                    content.release_date = line[3]
                    content.country = line[4]
                    # 上映時間はちゃんと変換しないと受け入れられない
                    # content.duration = line[5]

                    # 既存ジャンルならそれを流用。新規ジャンルならcreate
                    genre, _ = Genre.objects.get_or_create(genre=line[6])
                    content.genre = genre

                    # get_or_createは辞書とBooleanのタプルで帰ってくるので辞書だけ取り出す。
                    direct, _ = Director.objects.get_or_create(name=line[7])
                    content.director = direct

                    content.save()

                    # castは複数件を想定して処理
                    casts = line[8].split(';')
                    print(casts)

                    for itr in casts:
                        print(itr)
                        # 既存キャストならそれを流用。新規キャストならcreate
                        cs, _ = Cast.objects.get_or_create(name=itr)
                        content.cast.add(cs)

                    # content.awards = line[9]
                    content.save()

            return HttpResponseRedirect(reverse('Oort:index'))

        # DB直接インポート用分岐

        print('リクエスト', request.POST)

        if 'd_import' in request.POST:
            # form.pyのDB直接インポート用クラスを経由。数値変換
            d_import_form = DirectImportForm(request.POST)




            if d_import_form.is_valid():
                start = d_import_form.cleaned_data['start']
                end = d_import_form.cleaned_data['end']

                d_import = DirectImport()
                d_import.scrape(start, end)

                return HttpResponseRedirect(reverse('Oort:index'))


# オートコンプリート用(キャストDB内を登録画面で検索可能にする)
class CastAutoComplete(autocomplete.Select2QuerySetView):

    # selfは自分自身(CastAutoComplete)
    def get_queryset(self):
        qs = Cast.objects.all()

        # qは親クラス(Select2QuerySetView)が持ってる変数
        # qは入力値。qをもとに都度マッチする文字列を描画している
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class GenreAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Genre.objects.all()
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs


class DirectorAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Director.objects.all()
        print(qs)
        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs
