from django.core.cache import cache
from django_redis import get_redis_connection

from apps.tenant_service.middlewares import get_current_db_name


class CacheManager:
    """Custom cache manager used to set values in cache and much more."""

    @property
    def db_name(self):
        """Returns the current db name."""

        return get_current_db_name() or "default-iiht"

    @staticmethod
    def clear_cache():
        """Clear everything in the cache"""

        get_redis_connection("default").flushall()

    def set_item_in_cache(self, item, value, timeout=None):
        """
        Set the `value` in cache for the given `item` along with the timeout. If
        `timeout` is not provided then by default 5 minutes will be set.
        """

        if timeout is None:
            timeout = 300  # 5 minutes

        cached_tenant_data = cache.get(self.db_name)
        if not cached_tenant_data:
            cache.set(self.db_name, {item: value}, timeout=timeout)
        else:
            cached_tenant_data[item] = value

    def get_item_in_cache(self, item):
        """Get the value in cache for the given item."""

        cached_tenant_data = cache.get(self.db_name)
        if cached_tenant_data:
            return cached_tenant_data.get(item)
        return None


cache_manager = CacheManager()
