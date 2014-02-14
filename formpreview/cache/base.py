from django.conf import settings
from django.http.request import QueryDict
from django.utils.datastructures import MultiValueDict
from django.utils.module_loading import import_by_path

from ..files import FileCache


def overwrite_dict(base, *args):
    if not isinstance(base, dict):
        raise ValueError('Argument must be dict object.')

    if isinstance(base, MultiValueDict):
        if isinstance(base, QueryDict):
            base = base.copy()
        func = base.setlist
    else:
        func = base.__setitem__

    for d in args:
        if not isinstance(d, dict):
            raise ValueError('Argument must be dict object.')

        if isinstance(d, MultiValueDict):
            for k, values in d.lists():
                func(k, values)
        else:
            for k, value in d.items():
                func(k, [value])
    return base


class PostCacheBase(object):
    file_cache = FileCache()

    def __init__(self, key):
        self.key = key
        cached_data = self.get_cache(key)
        if cached_data:
            self._post = cached_data['data']
            self._files = self.load_files(cached_data['files'])
        else:
            self._post = MultiValueDict()
            self._files = MultiValueDict()

    def save(self, request):
        files = self.save_files(request.FILES)
        cached_data = self.get_cache(self.key)
        cached_files = cached_data['files'] if cached_data else MultiValueDict()
        cached_files = self.remove_cleared_files(request, cached_files)
        files = overwrite_dict(cached_files, files)

        post = request.POST.copy()
        self.set_cache(self.key, {'data': post, 'files': files})

        self._post = post
        self._files = self.load_files(files)

    def remove_cleared_files(self, request, cached_files):
        for key, values in cached_files.lists():
            is_clear = bool(request.POST.get(key + '-clear', False))
            if key not in request.FILES and is_clear:
                for val in cached_files.getlist(key):
                    self.file_cache.delete(val)
                del cached_files[key]
        return cached_files

    def clear(self):
        self.delete_files(self._files)
        self._cache.delete(self.key)
        self._post = MultiValueDict()
        self._files = MultiValueDict()

    def save_files(self, files):
        saved_files = MultiValueDict()
        files = MultiValueDict(files)
        for key, values in files.lists():
            saved_files.setlist(key, [self.file_cache.save(v) for v in values])
        return saved_files

    def load_files(self, files):
        loaded_files = MultiValueDict()
        for key, values in files.lists():
            loaded_files.setlist(key, [self.file_cache.load(v) for v in values])
        return loaded_files

    def delete_files(self, files):
        for key, values in files.lists():
            for v in values:
                self.file_cache.delete(v)

    @property
    def POST(self):
        return self._post

    @property
    def FILES(self):
        return self._files

    def get_cache(self, key, default=None):
        raise NotImplementedError()

    def set_cache(self, key, data, expires=None):
        raise NotImplementedError()


def get_post_cache_class(import_path=None):
    if not import_path:
        import_path = getattr(settings, 'FORMPREVIEW_CACHE_BACKEND', 'formpreview.cache.CachePostCache')
    return import_by_path(import_path)
