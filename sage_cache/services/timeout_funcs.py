import importlib

from sage_cache import settings

def default_timeout(user):
    """sample get timeout func for user"""
    return settings.CACHE_TIMEOUT


def get_timeout_for_user(user, func):
    """gets a func for calculating timeout for user"""
    module = func.split('.')
    function = module.pop(-1)
    import_string = '.'.join(module)
    module = importlib.import_module(import_string)
    function = getattr(module, function)
    return function(user)
