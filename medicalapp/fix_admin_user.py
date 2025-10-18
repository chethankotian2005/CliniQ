#!/usr/bin/env python3
"""
Fix Admin User Setup
Creates proper AdminUser profile for the admin user
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.contrib.auth.models import User
from adminpanel.models import AdminUser

def fix_admin_user():
    """Create AdminUser profile for admin user"""
    try:
        # Get or create admin user
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
            admin_user.set_password('admin123')
            admin_user.save()
            print("✅ Admin user created")
        else:
            print("✅ Admin user already exists")
            # Ensure password is correct
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            admin_user.save()
            print("✅ Admin user updated")
        
        # Create or update AdminUser profile
        admin_profile, created = AdminUser.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'super_admin',
                'phone_number': '+1-555-0123',
                'is_active': True
            }
        )
        
        if created:
            print("✅ AdminUser profile created")
        else:
            admin_profile.role = 'super_admin'
            admin_profile.is_active = True
            admin_profile.save()
            print("✅ AdminUser profile updated")
        
        print("\n" + "="*50)
        print("🎉 ADMIN SETUP COMPLETE")
        print("="*50)
        print(f"Username: {admin_user.username}")
        print("Password: admin123")
        print(f"Role: {admin_profile.role}")
        print("="*50)
        print("\n📍 Login URLs:")
        print("Custom Admin Panel: http://localhost:8000/adminpanel/login/")
        print("Django Admin: http://localhost:8000/admin/")
        print("\n✅ Both should work now!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_admin_user()