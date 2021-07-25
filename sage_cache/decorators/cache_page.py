from functools import wraps
import warnings

from django.views.decorators.cache import cache_page

from sage_cache import settings
from sage_cache.services.timeout_funcs import get_timeout_for_user


def cache_page_per_user():
    """cache page supported by DRF (per user)
    settings:
    CACHE_PAGE_ENABLED
    CACHE_PER_USER_TIMEOUT_FUNC
    CACHE_PER_USER_UNIQUE_ATTR
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):

            if hasattr(settings, 'CACHE_PAGE_ENABLED'):
                enabled = settings.CACHE_PAGE_ENABLED
            else:
                enabled = True

            if hasattr(settings, 'CACHE_PER_USER_TIMEOUT_FUNC'):
                timeout_func = settings.CACHE_PER_USER_TIMEOUT_FUNC
            else:
                raise AttributeError(
                    'CACHE_PER_USER_TIMEOUT_FUNC must be defined in settings.'
                )

            if enabled:

                user_id = 'not_auth'
                timeout_ = settings.CACHE_TIMEOUT

                if request.user.is_authenticated:

                    if hasattr(settings, 'CACHE_PER_USER_UNIQUE_ATTR'):
                        user_id = getattr(request.user, settings.CACHE_PER_USER_UNIQUE_ATTR)
                    else:
                        warnings.warn(
                            'CACHE_PER_USER_UNIQUE_ATTR not defined in settings. Changed to user default value.'
                        )
                        user_id = request.user.id

                    timeout_ = get_timeout_for_user(user=request.user, func=timeout_func)
            else:
                warnings.warn(
                    'Cache page is disabled from settings. Set CACHE_PAGE_ENABLED to True to activate.'
                )
                return view_func(self, request, *args, **kwargs)

            return cache_page(timeout=timeout_, key_prefix=f'_{user_id}_')(view_func)(request, *args, **kwargs)

        return _wrapped_view

    return decorator


def cache_page_per_site():
    """cache page supported by DRF (per site)
    settings:
    CACHE_PAGE_ENABLED
    CACHE_PAGE_PER_SITE_PREFIX
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(self, request, *args, **kwargs):
            if hasattr(settings, 'CACHE_PAGE_ENABLED'):
                enabled = settings.CACHE_PAGE_ENABLED
            else:
                enabled = True

            if enabled:
                if hasattr(settings, 'CACHE_TIMEOUT'):
                    timeout = settings.CACHE_TIMEOUT
                else:
                    warnings.warn(
                        'CACHE_TIMEOUT is not defined in settings. Changed to use default value.'
                    )
                    timeout = 60

                if hasattr(settings, 'CACHE_PAGE_PER_SITE_PREFIX'):
                    prefix = settings.CACHE_PAGE_PER_SITE_PREFIX
                else:
                    warnings.warn(
                        'CACHE_PAGE_PER_SITE_PREFIX is not defined in settings. Changes to use default value.'
                    )
                    prefix = 'cache_page'

                return cache_page(timeout=timeout, key_prefix=prefix)(view_func)(request, *args, **kwargs)

            else:
                warnings.warn(
                    'Cache page is disabled from settings. Set CACHE_PAGE_ENABLED to True to activate.'
                )
                return view_func(self, request, *args, **kwargs)

        return _wrapped_view

    return decorator
