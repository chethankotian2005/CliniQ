"""
Run this script to create demo admin user for CliniQ
Execute: python setup_admin.py
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.contrib.auth.models import User
from adminpanel.models import AdminUser

def create_admin():
    # Create demo admin user
    username = 'admin'
    email = 'admin@cliniq.com'
    password = 'admin123'
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f'⚠️  User {username} already exists')
            user = User.objects.get(username=username)
            user.set_password(password)  # Update password
            user.save()
            print(f'✅ Password updated for {username}')
        else:
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='System',
                last_name='Administrator'
            )
            print(f'✅ Superuser {username} created successfully')
        
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
            print(f'✅ Admin profile created for {username}')
        else:
            # Ensure existing profile is active
            admin_profile.is_active = True
            admin_profile.role = 'super_admin'
            admin_profile.save()
            print(f'✅ Admin profile updated for {username}')
        
        print('\n' + '='*50)
        print('🎉 ADMIN LOGIN CREDENTIALS')
        print('='*50)
        print(f'Username: {username}')
        print(f'Password: {password}')
        print(f'Email: {email}')
        print('='*50)
        print('\n📍 Login URL:')
        print('Admin Panel: http://localhost:8000/adminpanel/login/')
        print('\n✅ You can now login to the admin panel!')
        
        return True
        
    except Exception as e:
        print(f'❌ Error creating admin user: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print('🚀 Setting up CliniQ admin user...\n')
    success = create_admin()
    if success:
        print('\n🎯 Admin setup complete! Start the server and login.')
    else:
        print('\n💥 Setup failed. Check the errors above.')