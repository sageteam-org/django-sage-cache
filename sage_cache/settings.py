from django.conf import settings

if not settings.CACHES.get('default').get('BACKEND') == "django_redis.cache.RedisCache":
    raise ConnectionError('redis cache config not found in settings please add these lines to your settings\n'
                          'CACHES = {"default": {"BACKEND": "django_redis.cache.RedisCache","LOCATION": "redis://localhost:6379"}}')

CACHE_PER_USER_TIMEOUT_FUNC = getattr(
    settings, 'CACHE_PER_USER_TIMEOUT_FUNC',
    'sage_cache.services.timeout_funcs.default_timeout'
)
CACHE_PER_USER_UNIQUE_ATTR = getattr(settings, 'CACHE_PER_USER_UNIQUE_ATTR', 'id')
CACHE_QUERYSET_ENABLED = getattr(settings, 'CACHE_QUERYSET_ENABLED', True)
CACHE_TIMEOUT = getattr(settings, 'CACHE_TIMEOUT', 60)
CACHE_PAGE_ENABLED = getattr(settings, 'CACHE_PAGE_ENABLED', True)
CACHE_PAGE_PER_SITE_PREFIX = getattr(settings, 'CACHE_PAGE_PER_SITE_PREFIX', 'cache_page')
