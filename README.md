# Django Sage Cache
#### django-sage-cache is a package based on Django Web Framework & Django Rest Framework for queryset/page caching.

##### The Latest version of [django-sage-cache](https://django-sage-cache.readthedocs.io/) documentation

![SageTeam](https://github.com/sageteam-org/django-sage-painless/blob/develop/docs/images/tag_sage.png?raw=true "SageTeam")

![PyPI release](https://img.shields.io/pypi/v/django-sage-cache "django-sage-cache")
![Supported Python versions](https://img.shields.io/pypi/pyversions/django-sage-cache "django-sage-cache")
![Supported Django versions](https://img.shields.io/pypi/djversions/django-sage-cache "django-sage-cache")
![Documentation](https://img.shields.io/readthedocs/django-sage-cache "django-sage-cache")

- [Project Detail](#project-detail)
- [Git Rules](#git-rules)
- [Get Started](#getting-started)
- [Usage](#usage)
- [Filter Backends](#filter-backend)
- [Signals](#signals)
- [Cache Methods](#cache-methods)
- [Settings](#settings)

## Project Detail

- Language: Python > 3.5
- Framework: Django > 3.1

## Git Rules

S.A.G.E. team Git Rules Policy is available here:

- [S.A.G.E. Git Policy](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)

## Getting Started

First install the package using pip:

```shell
$ pip install django-sage-cache
```

Then add `sage_cache` to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'sage_cache',
    ...
]
```

For using cache support you need to config `redis server`:

- ubuntu:
```shell
$ sudo apt install redis-server
```

- windows:

[you can download redis server from here]((https://redis.io/download))

Then add redis cache to django settings:

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 'redis://localhost:6379'
    }
}
```

## Usage

There are multiple ways to use `sage_cache` in your project:

1. For simple usage you can use Model Mixin:

```python
# models.py
from sage_cache.mixins.model_cache import ModelCacheMixin

class Category(models.Model, ModelCacheMixin):
    CACHE_KEY = 'category'  # set for cache (set cache with this key)
    
    title = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
```

```python
# views.py
class CategoryViewset(ModelViewSet):
    serializer_class = CategorySerializer
    model_class = Category  # set for cache (its your model)
    
    def get_queryset(self):
        return self.model_class.get_all_from_cache()  # get from cache instead of db
```

2. Use built-in decorators:

You can use built-in view decorators in DRF methods

```python
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sage_cache.decorators.cache_queryset import cache_queryset_per_site

class CategoryViewset(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    model_class = Category  # set for cache

    @cache_queryset_per_site()  # set for cache (per site caching)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

list of built-in decorators:

- cache_queryset_per_site
- cache_queryset_per_user
- cache_page_per_site
- cache_page_per_user

3. You can also write your own functions:

`sage_cache` provides some useful functions and tools for cache support, You can use them to create cache apps

list of tools you can access:

- services:
    - cache_funcs:
        - get_all_from_cache
        - filter_from_cache
        - filter_related_from_cache
        - clear_cache_for_users
        - clear_cache_for_model
        - clear_model_cache_for_user
    - timeout_funcs:
        - get_timeout_for_user
        - default_timeout
    - view_funcs:
        - get_object

## Filter Backend

In cached views use these Filter/Search backends:

1. CacheFilterBackend
2. CacheSearchBackend

```python
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from sage_cache.decorators.cache_queryset import cache_queryset_per_site
from sage_cache.filters.backend import CacheFilterBackend, CacheSearchBackend

class CategoryViewset(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    model_class = Category  # set for cache
    filter_backends = (CacheFilterBackend, CacheSearchBackend)  # cache backends

    @cache_queryset_per_site()  # set for cache (per site caching)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

## Signals

When you set cache it will not update until timeout and expiration, In some situations you need to update cache when your data is updated in main db, For this reason we use Signals to update/remove cache.

- A simple example of update cache signal

```python
from sage_cache.services.cache_funcs import clear_cache_for_model

@receiver(post_save, sender=Category)
def update_category(sender, instance, created, **kwargs):
    clear_cache_for_model(sender.CACHE_KEY)  # remove all cache for updated model
```

List of some useful functions for Cache Updating:

- clear_cache_for_users
- clear_cache_for_model
- clear_model_cache_for_user

## Cache Methods

You can cache your project in 2 ways:

1. per site
2. per user

In per site mode you set just 1 cache key for each model in redis, And it is same for all users, But in per user method each user has unique cache keys.

For example cache key for `Category` model:

mode (per site): ":category"

mode (per user): ":category-mrhnz13@gmail.com"

In per user mode you can set multiple timeouts for each user.

## Settings
```python
CACHE_QUERYSET_ENABLED = True  # Is cache queryset enabled
CACHE_PAGE_ENABLED = True  # Is cache page enabled
CACHE_TIMEOUT = 60  # cache default timeout in seconds
CACHE_PER_USER_UNIQUE_ATTR = 'username'  # unique field in User
CACHE_PER_USER_TIMEOUT_FUNC = 'sage_cache.services.timeout_funcs.default_timeout'  # in per_user mode timeout will calculate by this function
CACHE_PAGE_PER_SITE_PREFIX = 'sage_cache_site'  # cache page key prefix
```


## Team
| [<img src="https://github.com/sageteam-org/django-sage-painless/blob/develop/docs/images/sepehr.jpeg?raw=true" width="230px" height="230px" alt="Sepehr Akbarzadeh">](https://github.com/sepehr-akbarzadeh) | [<img src="https://github.com/sageteam-org/django-sage-painless/blob/develop/docs/images/mehran.png?raw=true" width="225px" height="340px" alt="Mehran Rahmanzadeh">](https://github.com/mrhnz) |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Sepehr Akbarazadeh Maintainer](https://github.com/sepehr-akbarzadeh)                                                                                                             | [Mehran Rahmanzadeh Maintainer](https://github.com/mrhnz)                                                                                                       |