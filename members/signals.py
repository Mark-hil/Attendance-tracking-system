from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.core.cache import cache
from .models import Member
import logging

logger = logging.getLogger(__name__)

@receiver(pre_delete, sender=Member)
def delete_member_qr_tokens(sender, instance, **kwargs):
    """
    Clean up any QR code tokens associated with a member when the member is deleted.
    This version is simplified to work without database cache.
    """
    try:
        # Try to delete any potential cache keys
        # This is a best-effort approach since we can't reliably list all keys
        # with most cache backends
        cache.delete(f'qr_token_{instance.id}')
        cache.delete(f'invalid_qr_tokens_{instance.id}')
        
    except Exception as e:
        # Log any errors but don't prevent the member from being deleted
        logger.error(f"Error cleaning up QR tokens for member {instance.id}: {str(e)}")
    
    # Note: For a production environment with Redis, you could implement
    # a more robust solution using Redis key patterns or a separate model
    # to track active QR code tokens.
