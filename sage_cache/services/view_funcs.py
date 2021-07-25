from django.http import Http404

from sage_cache.services.cache_funcs import filter_from_cache


def get_object(cls):
    """get object from cache
    Must be replaced with `get_object()` method in viewsets
    """
    lookup_url_kwarg = cls.lookup_url_kwarg or cls.lookup_field
    filter_kwargs = {
        cls.lookup_field: cls.kwargs[lookup_url_kwarg]
    }
    qs = filter_from_cache(cls.queryset, **filter_kwargs)
    if len(qs) == 0:
        raise Http404('Not Found')
    obj = qs[0]
    return obj
