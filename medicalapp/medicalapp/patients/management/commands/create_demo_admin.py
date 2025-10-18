from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from adminpanel.models import AdminUser

class Command(BaseCommand):
    help = 'Create demo admin user'

    def handle(self, *args, **options):
        # Create Django superuser
        username = 'demo_admin'
        email = 'admin@cliniq.com'
        password = 'demo123456'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'User {username} already exists'))
            user = User.objects.get(username=username)
        else:
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser {username} created successfully'))
        
        # Create admin profile
        admin_profile, created = AdminUser.objects.get_or_create(
            user=user,
            defaults={
                'role': 'super_admin',
                'phone_number': '+1234567890',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Admin profile created for {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Admin profile already exists for {username}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== DEMO ADMIN CREDENTIALS ==='))
        self.stdout.write(self.style.SUCCESS(f'Username: {username}'))
        self.stdout.write(self.style.SUCCESS(f'Password: {password}'))
        self.stdout.write(self.style.SUCCESS(f'Email: {email}'))
        self.stdout.write(self.style.SUCCESS('================================'))
        self.stdout.write(self.style.SUCCESS('\nYou can now login to:'))
        self.stdout.write(self.style.SUCCESS('- Django Admin: /admin/'))
        self.stdout.write(self.style.SUCCESS('- CliniQ Admin Panel: /adminpanel/login/'))