import os.path
import uuid

from django.conf import settings
from django.core.files.base import File
from django.core.files.storage import default_storage
from django.utils.module_loading import import_by_path


def get_storage(import_path=None):
    if import_path:
        return import_by_path(import_path)()
    else:
        try:
            return import_by_path(settings.FORMPREVIEW_FILE_CACHE_STORAGE)()
        except AttributeError:
            return default_storage


class FileCache(object):
    _storage = get_storage()

    def save(self, file_object):
        path = self.create_filepath(file_object)
        self._storage.save(path, file_object)
        return path

    def get_upload_tmp_dir_path(self):
        return getattr(settings, 'FORM_PREVIEW_UPLOAD_TMP_DIR', 'formpreview/')

    def create_filepath(self, file_object):
        root, ext = os.path.splitext(file_object.name)
        name = str(uuid.uuid4())
        return self.get_upload_tmp_dir_path() + name + ext

    def load(self, path):
        file_object = self._storage.open(path)
        url = self._storage.url(path)
        path = self._storage.path(path)
        return CachedFile(file_object, url, path)

    def delete(self, path):
        self._storage.delete(path)


class CachedFile(File):
    def __init__(self, file_object, url, path):
        self.import_properties(file_object)
        self.url = url
        self.path = path
        self.name = url.replace(settings.MEDIA_URL, '')

    def import_properties(self, file_object):
        self.__dict__ = file_object.__dict__.copy()
