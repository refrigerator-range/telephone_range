from django.urls import path

from . import views
# ログインフォーム用
from django.contrib.auth import views as auth_views

app_name = 'Oort'

urlpatterns = [
    path('', views.IndexViews, name='index'),

    # detail用にURL(ルーティング)を通す。index.htmlのOort:detailと紐づく
    path('<int:content_id>', views.detail, name='detail'),

    # 登録フォーム用
    path('register', views.register, name='register'),

    # ファイル経由インポート用
    path('import', views.Import.as_view(), name='import'),

    # オートコンプリートで表示
    path('cast-autocomplete/', views.CastAutoComplete.as_view(), name='cast-autocomplete'),
    path('genre-autocomplete/', views.GenreAutoComplete.as_view(), name='genre-autocomplete'),
    path('director-autocomplete/', views.DirectorAutoComplete.as_view(), name='director-autocomplete'),

    # ログインフォーム用
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('signup', views.SignUp.as_view(), name='signup')

]
