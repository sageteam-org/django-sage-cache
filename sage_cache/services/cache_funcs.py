import operator
import warnings

from django.core.cache import cache
from django.db.models import QuerySet

from sage_cache import settings


def get_all_from_cache(model_class, timeout, get_cache_key, set_cache_key, **kwargs):
    """get/set all queryset from cache
    if lazy=True return QuerySet
    else returns list
    NOTE: get_cache_key can be a pattern for searching in cache. e.g: '*-products-*'
    """
    lazy = kwargs.get('lazy', False)

    if hasattr(model_class, 'CACHED_RELATED_OBJECT'):
        # select related

        keys = cache.keys(get_cache_key)
        if keys:
            queryset = cache.get(keys[0])
        else:
            cache.set(
                set_cache_key,
                model_class.objects.all().select_related(**model_class.CACHED_RELATED_OBJECT),
                timeout
            )
            queryset = cache.get(set_cache_key)

    else:
        keys = cache.keys(get_cache_key)
        if keys:
            queryset = cache.get(keys[0])
        else:
            cache.set(
                set_cache_key,
                model_class.objects.all(),
                timeout
            )
            queryset = cache.get(set_cache_key)

    return queryset if lazy else list(queryset)


def filter_from_cache(queryset, operator_=operator.eq, **kwargs):
    """filter queryset from cache
    filter based on `operator_` (must be from operator module)
    if lazy=True return QuerySet
    else returns list
    """
    lazy = kwargs.get('lazy', False)

    if lazy and not isinstance(queryset, QuerySet):
        raise TypeError('in lazy mode just QuerySet is allowed')

    def filter_obj(obj):
        select = True
        for filter_key, filter_value in kwargs.items():
            select = True  # boolean indicating if the item should be selected
            if isinstance(filter_value, list):
                if getattr(obj, filter_key) not in filter_value:
                    select = False
                    if operator_ not in [operator.contains, operator.or_]:
                        break
            elif not operator_(getattr(obj, filter_key), filter_value):
                select = False
                if operator_ not in [operator.contains, operator.or_]:
                    break
            if operator_ in [operator.contains, operator.or_]:
                if select:
                    break
        return select

    return list(filter(filter_obj, queryset)) if not lazy else queryset.filter(**kwargs)


def filter_related_from_cache(queryset, **kwargs):
    """filter related from cache
    if lazy=True return QuerySet
    else returns list
    """
    lazy = kwargs.get('lazy', False)

    if lazy and not isinstance(queryset, QuerySet):
        raise TypeError('in lazy mode just QuerySet is allowed')

    if not lazy:
        for foreign_key, related_filters in kwargs.items():
            related_objects_list = [getattr(obj, foreign_key) for obj in queryset]
            # Filtering related objects based related object's attribute filters
            filtered_related_objects = filter_from_cache(
                related_objects_list, **related_filters
            )
            # Filtering queryset based filtered related objects
            queryset = list(
                filter(
                    lambda x: getattr(x, foreign_key) in filtered_related_objects,
                    queryset,
                )
            )
    else:
        queryset = queryset.filter(**kwargs)

    return queryset


def clear_cache_for_users(users: list, pattern: str = '*{}*'):
    """removes all caches related to users arg
    NOTE: Default value of CACHE_PER_USER_UNIQUE_ATTR is 'id'
    NOTE: You can change default search pattern
    """
    if hasattr(settings, 'CACHE_PER_USER_UNIQUE_ATTR'):
        unique_attr = settings.CACHE_PER_USER_UNIQUE_ATTR
    else:
        warnings.warn(
            'CACHE_PER_USER_UNIQUE_ATTR is not defined in settings, Changed to use default value `id`.'
        )
        unique_attr = 'id'

    for user in users:
        query = pattern.format(getattr(user, unique_attr))
        keys = cache.keys(query)
        cache.delete_many(keys)


def clear_cache_for_model(cache_key: str, pattern: str = '*{}*'):
    """removes all caches of this model
    NOTE: You can change default search pattern
    """
    query = pattern.format(cache_key)
    keys = cache.keys(query)
    cache.delete_many(keys)


def clear_model_cache_for_user(user, cache_key: str, pattern: str = '*{}*{}*'):
    """removes user's caches (filtered for cache_key)
    NOTE: You can change default search pattern
    NOTE: Default value of CACHE_PER_USER_UNIQUE_ATTR is 'id'
    """
    if hasattr(settings, 'CACHE_PER_USER_UNIQUE_ATTR'):
        unique_attr = settings.CACHE_PER_USER_UNIQUE_ATTR
    else:
        warnings.warn(
            'CACHE_PER_USER_UNIQUE_ATTR is not defined in settings, Changed to use default value.'
        )
        unique_attr = 'id'

    query = pattern.format(getattr(user, unique_attr), cache_key)
    keys = cache.keys(query)
    cache.delete_many(keys)
