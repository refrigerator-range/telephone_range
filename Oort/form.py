import csv
import io

from dal import autocomplete
from django import forms
from .models import Content, Genre, Director, Cast


# 登録フォーム用
# modelクラスを元にフィールドを自動生成する
class ContentForm(forms.ModelForm):
    class Meta:
        # 紐づけるmodelクラスはContentクラス
        model = Content
        # Modelから入力フォームを生成する対象のフィールドをタプル形式で指定
        fields = ['title', 'thumbnail', 'payback_time', 'country', 'release', 'genre', 'director', 'cast', 'award']

        # オートコンプリート用
        widgets = {
            'cast': autocomplete.ModelSelect2Multiple(url='Oort:cast-autocomplete'),
            'genre': autocomplete.ModelSelect2(url='Oort:genre-autocomplete'),
            'director': autocomplete.ModelSelect2(url='Oort:director-autocomplete')
        }


# ジャンル登録フォーム用
# modelクラスを元にフィールドを自動生成する
class GenreForm(forms.ModelForm):
    class Meta:
        # 紐づけるmodelクラスはGenreクラス
        model = Genre
        # Modelから入力フォームを生成する対象のフィールドをタプル形式で指定
        fields = ['genre']


# キャスト登録フォーム用
# modelクラスを元にフィールドを自動生成する
class CastForm(forms.ModelForm):
    class Meta:
        model = Cast
        # Modelから入力フォームを生成する対象のフィールドをタプル形式で指定
        fields = ['name', 'resume']


# 監督登録フォーム用
class DirectorForm(forms.ModelForm):
    class Meta:
        model = Director
        fields = ['name', 'resume']


# インポートフォーム用
class CSVUploadForm(forms.Form):
    file = forms.FileField(label='CSVファイル', help_text='CSVをアップロードしてください')

    # # いらないかも
    # def clean_file(self):
    #     file = self.cleaned_data['file']
    #     print('ここでform.py')
    #
    #     # ファイル名がCSVかどうかの確認
    #     if not file.name.endwith('.csv'):
    #         raise forms.ValidationError('拡張子がcsvのファイルをアップロードしてください')
    #
    #     # csv.readerに渡すため、TextIOWrapperでテキストモードなファイルに変換
    #     csv_file = io.TextIOWrapper(file, encoding='utf-8')
    #     reader = csv.reader(csv_file)
    #
    #     # 各行から作った保存前のモデルインスタンスを保管するリスト
    #     self._instances = []
    #     try:
    #         for row in reader:
    #             content = Content(pk=row[0], title=row[1])
    #             self._instances.append(content)
    #     except UnicodeDecodeError:
    #         raise forms.ValidationError('エンコーディングがおかしい')
    #
    #     print('ファイル', file)
    #     return file

    # bulk_createで沢山作って、bulk_updateで沢山更新する
    def save(self):
        Content.objects.bulk_create(self._instances, ignore_conflicts=True)
        Content.objects.bulk_update(self._instances, fields=['title'])


# DB直接インポート用
class DirectImportForm(forms.Form):
    start = forms.IntegerField()
    end = forms.IntegerField()
