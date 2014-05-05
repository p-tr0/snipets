from django.core.cache import caches
from django.conf import settings
from types import MethodType

def get_cache(name='default'):
    """Returns cache with ttl(key) method added that returns key's time to live 
    (time left until expiration). It works only for redis and locmem. 
    For other backends it raises exception.    
    """
    cache = caches[name]
    if hasattr(cache, 'ttl'):        
        return cache    
    backend = settings.CACHES.get(name, {}).get('BACKEND', None)
    if backend == 'redis_cache.RedisCache':
        def ttl(self, key):
            key2 = cache.make_key(key)
            t = cache._client.ttl(key2)
            return t        
    elif backend == 'django.core.cache.backends.locmem.LocMemCache':
        def ttl(self, key):
            key2 = cache.make_key(key)
            t = int(cache._expire_info.get(key2, 0) - time.time())
            return t if t>0 else 0        
    else:
        def ttl(self, key):
            raise NotImplementedError("'ttl' method was added only for redis and locmem cache backends")
    cache.ttl = MethodType( ttl, cache )    
    return cache
