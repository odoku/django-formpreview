from django.conf import settings
from django.core.cache import get_cache

from base import PostCacheBase


class CachePostCache(PostCacheBase):
    _cache = get_cache(getattr(settings, 'FORM_PREVIEW_CACHE_ALIAS', 'default'))

    def get_cache(self, key):
        return self._cache.get(key, None)

    def set_cache(self, key, value, expires=None):
        if not expires:
            expires = 24 * 60 * 60
        self._cache.set(key, value, expires)
