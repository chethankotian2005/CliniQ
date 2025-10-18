"""
Simple script to create demo admin user for CliniQ
Run this script: python create_admin.py
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.contrib.auth.models import User
from adminpanel.models import AdminUser

def create_demo_admin():
    """Create demo admin user"""
    username = 'demo_admin'
    email = 'admin@cliniq.com'
    password = os.getenv('ADMIN_PASSWORD', 'change_me_123')  # Use environment variable for security
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f'⚠️  User {username} already exists')
            user = User.objects.get(username=username)
        else:
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Demo',
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
            print(f'⚠️  Admin profile already exists for {username}')
        
        print('\n' + '='*50)
        print('🎉 DEMO ADMIN CREDENTIALS')
        print('='*50)
        print(f'Username: {username}')
        print(f'Password: {password}')
        print(f'Email: {email}')
        print('='*50)
        print('\n📍 Login URLs:')
        print('- Django Admin: http://localhost:8000/admin/')
        print('- CliniQ Admin Panel: http://localhost:8000/adminpanel/login/')
        print('\n🔐 Role: Super Administrator')
        print('✅ Setup complete!')
        
    except Exception as e:
        print(f'❌ Error creating admin user: {str(e)}')
        return False
    
    return True

if __name__ == '__main__':
    print('🚀 Creating demo admin user for CliniQ...\n')
    success = create_demo_admin()
    if success:
        print('\n🎯 You can now access the admin panel!')
    else:
        print('\n💥 Failed to create admin user. Check the error above.')