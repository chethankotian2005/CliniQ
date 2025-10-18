from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from adminpanel.models import AdminUser

class Command(BaseCommand):
    help = 'Create admin user and AdminUser profile'

    def handle(self, *args, **options):
        # Create or get admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@cliniq.com',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('Created admin user')
        else:
            self.stdout.write('Admin user already exists')
        
        # Set password
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()
        
        # Create AdminUser profile
        admin_profile, created = AdminUser.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'super_admin',
                'phone_number': '+1-555-0123',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('Created AdminUser profile')
        else:
            admin_profile.role = 'super_admin'
            admin_profile.is_active = True
            admin_profile.save()
            self.stdout.write('Updated AdminUser profile')
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Admin setup complete!\n'
                'Username: admin\n'
                'Password: admin123\n'
                'Login at: /adminpanel/login/\n'
            )
        )