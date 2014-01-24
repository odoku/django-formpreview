from django.core.files.base import ContentFile
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from mock import patch

from ..cache.base import PostCacheBase
from ..files import CachedFile


class PostCacheBaseTest(TestCase):
    def setUp(self):
        self.patchers = []
        self.patchers.append(
            patch('formpreview.cache.base.PostCacheBase.file_cache', **{
                'save.return_value': '/path/to/filename',
                'load.return_value': CachedFile(ContentFile(''), '/path/to/filename', '/path/to/filename'),
                'delete.return_value': None,
            })
        )
        self.patchers.append(
            patch('formpreview.cache.base.PostCacheBase.get_cache', **{
                'return_value': {
                    'data': MultiValueDict({'hoge': [10], 'piyo': ['aaa']}),
                    'files': MultiValueDict({'foo': ['/path/to/filename']}),
                }
            })
        )
        self.patchers.append(patch('formpreview.cache.base.PostCacheBase.set_cache'))
        for p in self.patchers:
            p.start()
        self.cache = PostCacheBase('key')

    def tearDown(self):
        for p in self.patchers:
            p.stop()

    def test_create(self, *args, **kwargs):
        self.assertTrue(isinstance(self.cache.POST, MultiValueDict))
        self.assertTrue(isinstance(self.cache.FILES, MultiValueDict))
        self.assertEqual(len(self.cache.POST), 2)

    def test_load_files(self, *args, **kwargs):
        files = self.cache.load_files(MultiValueDict({'hoge': ['/path/to/filename']}))
        self.assertTrue(isinstance(files, MultiValueDict))
        self.assertEqual(len(files), 1)
        for key, values in files.lists():
            for v in values:
                self.assertTrue(isinstance(v, CachedFile))
                self.assertEqual(v.url, '/path/to/filename')

    def test_save_files(self, *args, **kwargs):
        files = self.cache.save_files(MultiValueDict({'hoge': [ContentFile('')]}))
        self.assertTrue(isinstance(files, MultiValueDict))
        self.assertEqual(len(files), 1)
        for key, values in files.lists():
            for v in values:
                self.assertTrue(isinstance(v, str))

    def test_delete_files(self, *args, **kwargs):
        result = self.cache.delete_files(MultiValueDict({'hoge': ['/path/to/filename']}))
        self.assertEqual(result, None)
