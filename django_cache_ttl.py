from django.core.cache import caches
from django.conf import settings
from types import MethodType

def get_cache(name='default'):
    """Adds 'ttl' (time to live) method to specified cache; 
    ttl returns seconds left until specified key expires 
    or None if expiration time was not set    
    """
    cache = caches[name]
    if hasattr(cache, 'ttl'):        
        return cache    
    backend = settings.CACHES.get(name, {}).get('BACKEND', None)      
    if backend == 'django.core.cache.backends.locmem.LocMemCache':
        def ttl(self, key, version=None):
            if cache.has_key(key, version):                
                key = cache.make_key(key, version)
                t = cache._expire_info.get(key)
                if t is None:
                    return None
                t -= time.time()
                if t>0:
                    return int(t)
            return 0
    ## This is not needed since django-redis-cache 0.12.0
    #elif backend == 'redis_cache.RedisCache':
    #    def ttl(self, key, version=None):
    #        key = self.make_key(key, version=version)
    #        if self._client.exists(key):
    #            return self._client.ttl(key)
    #        return 0
    else:        
        raise NotImplementedError("'get_cache' does not support backend: '%s'" % backend)
    cache.ttl = MethodType( ttl, cache ) 
    return cache
