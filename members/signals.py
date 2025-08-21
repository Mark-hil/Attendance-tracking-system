from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.core.cache import cache
from .models import Member
import re

@receiver(pre_delete, sender=Member)
def delete_member_qr_tokens(sender, instance, **kwargs):
    """
    Delete all QR code tokens associated with a member when the member is deleted.
    """
    # Get all cache keys
    from django.core.cache import caches
    cache = caches['default']
    
    # This is a simplified approach - in a production environment, you might need
    # a more sophisticated way to track all keys for a member
    # This will only work with certain cache backends that support key iteration
    try:
        # This is a simple approach that works with DatabaseCache
        from django.core.cache.backends.db import DatabaseCache
        from django.db import connection
        
        table = connection.ops.quote_name('cache_table')
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT cache_key FROM {table} WHERE cache_key LIKE %s", 
                         [f'%qr_token_{instance.id}_%'])
            keys = [row[0] for row in cursor.fetchall()]
            
        # Delete all matching keys
        if keys:
            cache.delete_many(keys)
    except Exception as e:
        # Fallback: Log the error and continue with member deletion
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error cleaning up QR tokens for member {instance.id}: {str(e)}")
        # Invalidate all caches for this member by setting an expired key
        # This is a fallback and might not work with all cache backends
        cache.set(f'invalid_qr_tokens_{instance.id}', True, timeout=1)
        
    # Note: For production, consider using a more robust solution like:
    # 1. Storing token references in the database
    # 2. Using Redis with key patterns for better token management
    # 3. Implementing a periodic cleanup task for orphaned tokens
