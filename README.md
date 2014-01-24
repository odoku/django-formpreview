django-cached-formpreview
=========================

Django用の確認画面付き汎用フォームビュー。  
ちゃんと入力画面に戻れるよ。  
ファイルのプレビューも出来るよ！ワァオ！！

使い方
-------------------------
DjangoのFormViewを継承しているので、基本的な使い方は[Djangoのドキュメント](https://docs.djangoproject.com/en/dev/ref/class-based-views/generic-editing/#django.views.generic.edit.FormView)を参照して下さい。

### 設定

フォームの内容をDjangoのキャッシュフレームワークを用いて保存しています。  
なので、必ずキャッシュの設定を行って下さい！

    # 貴方のお好みのキャッシュを使ってね！
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache',
        }
    }

サイト全体のキャッシュとは別のキャッシュAPIを使いたい場合は以下の様に指定して下さい。

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            'LOCATION': 'django_cache',
        },
        'formpreview': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache',
        }
    }
    FORM_PREVIEW_CACHE_ALIAS = 'formpreview'

アップロードされたファイルは、DjangoのストレージAPIを使って一時保存されます。  
Djangoのデフォルトストレージを変更すると、一緒に変わります。  
別々にしたい場合は以下の様に設定を行って下さい。

    # お好きなストレージ
    FORMPREVIEW_FILE_CACHE_STORAGE = 'django.core.files.storage.FileSystemStorage'

ファイルの一時保存先ディレクトリの指定は以下の様に。

    FORM_PREVIEW_UPLOAD_TMP_DIR = '/upload/tmp'

### ビューの実装方法

    from django import forms
    from formpreview.views import FormPreview


    class ArticleView(FormPreview):
        form_class = forms.Forms
        form_template = 'form.html'
        preview_template = 'preview.html'
        success_url = '/completed'

        def input(self, form):
            # 入力画面
            return super(ArticleView, self).input(form)

        def preview(self, form):
            # 確認画面
            return super(ArticleView, self).input(form)

        def done(self, form):
            # 登録処理など
            return super(ArticleView, self).done(form)

注意点
-------------------------
FormViewの代わりに使用される事を想定しています。  
UpdateViewとかその他の便利ビューと一緒には使えないのでご了承下さいませ。