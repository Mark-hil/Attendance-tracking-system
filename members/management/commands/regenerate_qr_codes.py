from django.core.management.base import BaseCommand
from members.models import Member, generate_qr_code_for_attendance
from io import BytesIO

class Command(BaseCommand):
    help = 'Regenerate QR codes for all members with proper URL encoding'

    def handle(self, *args, **options):
        members = Member.objects.all()
        count = 0
        
        for member in members:
            try:
                # Generate new QR code using the centralized function
                qr_code_file = generate_qr_code_for_attendance(member)
                if qr_code_file:
                    # Read the file content and save to the member
                    member.qr_code = qr_code_file.read()
                    member.save(update_fields=["qr_code"])
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Regenerated QR code for {member.first_name} {member.last_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Failed to generate QR code for {member.first_name} {member.last_name}'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {member.first_name} {member.last_name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully regenerated {count} QR codes'))
