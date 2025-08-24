from django.core.management.base import BaseCommand
from members.models import Member
from django.core.cache import cache
import qrcode
from io import BytesIO
from urllib.parse import quote_plus

class Command(BaseCommand):
    help = 'Update all QR codes to include member names'

    def handle(self, *args, **options):
        members = Member.objects.all()
        updated_count = 0
        
        for member in members:
            try:
                # Generate a unique token for this QR code
                import uuid
                token = str(uuid.uuid4())
                cache_key = f'qr_token_{member.id}_{token}'
                
                # Store token data
                token_data = {
                    'valid': True,
                    'last_used': None,
                    'member_id': member.id
                }
                cache.set(cache_key, token_data, timeout=None)
                
                # Create QR code with production URL and include member name
                base_url = 'https://attendance-tracking-system-5d9n.onrender.com'
                full_name = f"{member.first_name} {member.last_name}"
                qr_data = f"{base_url}/scan-attendance/?member_id={member.id}&name={quote_plus(full_name)}&token={token}"
                
                # Generate QR code with high error correction
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=12,
                    border=6,
                )
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                # Create image with high contrast
                img = qr.make_image(fill_color='black', back_color='white')
                
                # Ensure the QR code is large enough to be scanned
                size = (img.size[0] * 2, img.size[1] * 2)
                img = img.resize(size, resample=0)
                
                # Save to buffer
                buffer = BytesIO()
                img.save(buffer, format='PNG', quality=100)
                
                # Update the member's QR code
                member.qr_code = buffer.getvalue()
                member.save(update_fields=["qr_code"])
                
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated QR code for {full_name}'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error updating QR code for member {member.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} QR codes'))
