from django.core.files.base import ContentFile
from django.test import TestCase
from mock import patch

from ..files import CachedFile, FileCache


class FileCacheTest(TestCase):
    def setUp(self):
        self.patcher = patch('formpreview.files.FileCache._storage', **{
            'save.return_value': '/path/to/filename',
            'open.return_value': ContentFile(''),
            'url.return_value': '/media/path/to/storage/filename',
            'path.return_value': '/document_root/media/path/to/storage/filename',
            'delete.return_value': None,
        })
        self.patcher.start()
        self.file_cache = FileCache()

    def tearDown(self):
        self.patcher.stop()

    def test_save(self, *args, **kwargs):
        file_object = ContentFile('')
        file_object.name = 'filename'
        path = self.file_cache.save(file_object)
        self.assertTrue(isinstance(path, str))

    def test_load(self, *args, **kwargs):
        file_object = self.file_cache.load('/path/to/filename')
        self.assertTrue(isinstance(file_object, CachedFile))

    def test_delete(self, *args, **kwargs):
        path = '/path/to/filename'
        self.assertEqual(self.file_cache.delete(path), None)
