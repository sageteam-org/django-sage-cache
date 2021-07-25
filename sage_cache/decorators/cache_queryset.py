import warnings
from functools import wraps

from sage_cache import settings
from sage_cache.services.cache_funcs import get_all_from_cache, filter_from_cache
from sage_cache.services.timeout_funcs import get_timeout_for_user


def cache_queryset_per_user(lazy=False):
    """cache queryset for DRF views (per user)
    identify cache keys with a unique attr of user
    settings:
    CACHE_QUERYSET_ENABLED
    CACHE_PER_USER_TIMEOUT_FUNC
    CACHE_PER_USER_UNIQUE_ATTR
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if hasattr(settings, 'CACHE_QUERYSET_ENABLED'):
                enabled = settings.CACHE_QUERYSET_ENABLED
            else:
                enabled = True
            if enabled:
                if not hasattr(self, 'model_class'):
                    raise AttributeError('model_class must be defined in {}'.format(self.__name__))

                if not hasattr(self.model_class, 'CACHE_KEY'):
                    raise AttributeError("CACHE_KEY must be defined in {}".format(self.model_class.__name__))

                if hasattr(settings, 'CACHE_PER_USER_TIMEOUT_FUNC'):
                    timeout_func = settings.CACHE_PER_USER_TIMEOUT_FUNC
                else:
                    raise AttributeError(
                        'CACHE_PER_USER_TIMEOUT_FUNC must be defined in settings.'
                    )

                if hasattr(settings, 'CACHE_PER_USER_UNIQUE_ATTR'):
                    user_id = getattr(request.user, settings.CACHE_PER_USER_UNIQUE_ATTR)
                else:
                    warnings.warn(
                        'CACHE_PER_USER_UNIQUE_ATTR not defined in settings. Changed to user default value.'
                    )
                    user_id = request.user.id

                get_cache_key = f'*{user_id}*{self.model_class.CACHE_KEY}*'
                set_cache_key = f'{user_id}-{self.model_class.CACHE_KEY}'
                queryset = get_all_from_cache(
                    model_class=self.model_class,
                    get_cache_key=get_cache_key,
                    set_cache_key=set_cache_key,
                    timeout=get_timeout_for_user(user=request.user, func=timeout_func),
                    lazy=lazy
                )  # all

                if hasattr(self, 'queryset_filter'):
                    queryset = filter_from_cache(queryset, **self.queryset_filter, lazy=lazy)  # filtered

                self.queryset = queryset

                return view_func(self, request, *args, **kwargs)

            else:
                warnings.warn(
                    'Cache queryset is disabled from settings. Set CACHE_QUERYSET_ENABLED to True to activate.'
                )
                self.queryset = self.model_class.objects.all()
                if hasattr(self, 'queryset_filter'):
                    self.queryset = self.queryset.filter(**self.queryset_filter)
                return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator


def cache_queryset_per_site(lazy=False):
    """cache queryset for DRF views (per site)
    one cache key for whole site
    settings:
    CACHE_QUERYSET_ENABLED
    CACHE_TIMEOUT
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if hasattr(settings, 'CACHE_QUERYSET_ENABLED'):
                enabled = settings.CACHE_QUERYSET_ENABLED
            else:
                enabled = True

            if enabled:
                if not hasattr(self.model_class, 'CACHE_KEY'):
                    raise AttributeError("CACHE_KEY must be defined in {}".format(self.model_class.__name__))

                if hasattr(settings, 'CACHE_TIMEOUT'):
                    timeout = settings.CACHE_TIMEOUT
                else:
                    warnings.warn(
                        'CACHE_TIMEOUT is not defined in settings. Changed to use default value.'
                    )
                    timeout = 60

                get_cache_key = f'*{self.model_class.CACHE_KEY}*'
                set_cache_key = f'{self.model_class.CACHE_KEY}'
                queryset = get_all_from_cache(
                    model_class=self.model_class,
                    get_cache_key=get_cache_key,
                    set_cache_key=set_cache_key,
                    timeout=timeout,
                    lazy=lazy
                )  # all

                if hasattr(self, 'queryset_filter'):
                    queryset = filter_from_cache(queryset, **self.queryset_filter, lazy=lazy)  # filtered

                self.queryset = queryset

                return view_func(self, request, *args, **kwargs)

            else:
                warnings.warn(
                    'Cache queryset is disabled from settings. Set CACHE_QUERYSET_ENABLED to True to activate.'
                )
                return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator
