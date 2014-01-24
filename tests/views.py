import StringIO

from django import forms
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from django.test.client import RequestFactory
from django.utils.datastructures import MultiValueDict
from mock import patch

from ..views import FormView
from ..files import CachedFile


class SampleForm(forms.Form):
    title = forms.CharField(label='Title', max_length=50)
    body = forms.CharField(label='Body', max_length=1000, widget=forms.Textarea)
    attachment = forms.FileField(label='Attachment', required=False)


class SampleView(FormView):
    form_class = SampleForm
    form_template = 'formpreview/form.html'
    preview_template = 'formpreview/preview.html'
    success_url = '/success'


class FormViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = SampleView.as_view()

        io = StringIO.StringIO('xxx')
        self.file_object = InMemoryUploadedFile(io, None, 'sample.txt', 'text', io.len, None)
        self.test_file = CachedFile(self.file_object, '/path/to/filename', '/path/to/filename')
        self.test_file.name = 'sample.txt'

        self.patcher = patch('formpreview.views.FormView.post_cache_class', ** {
            'return_value.save.return_value': None,
            'return_value.clear.return_value': None,
            'return_value.POST': MultiValueDict({
                'title': ['hoge'],
                'body': ['piyopiyo'],
            }),
            'return_value.FILES': MultiValueDict({
                'attachment': [self.test_file],
            }),
        })
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def test_get(self):
        request = self.factory.get('/')
        self.add_session_to_request(request)

        response = self.view(request)
        context = response.context_data

        self.assertEqual(response.status_code, 200)
        self.assertTrue('stage' in context)
        self.assertEqual(context['stage'], 'input')

    def test_post(self):
        data = {
            'stage': 'preview',
            'title': 'hoge',
            'body': 'piyopiyo',
            'attachment': self.file_object,
        }
        request = self.factory.post('/', data)
        self.add_session_to_request(request)
        response = self.view(request)
        context = response.context_data
        self.assertEqual(response.status_code, 200)
        self.assertTrue('stage' in context)
        self.assertEqual(context['stage'], 'preview')

        data = {'stage': 'input'}
        request = self.factory.post('/', data)
        self.add_session_to_request(request)
        response = self.view(request)
        context = response.context_data
        self.assertEqual(response.status_code, 200)
        self.assertTrue('stage' in context)
        self.assertEqual(context['form']['title'].value(), 'hoge')
        self.assertEqual(context['form']['body'].value(), 'piyopiyo')
        self.assertEqual(context['stage'], 'input')

        data = {'stage': 'post'}
        request = self.factory.post('/', data)
        self.add_session_to_request(request)
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], SampleView.success_url)
