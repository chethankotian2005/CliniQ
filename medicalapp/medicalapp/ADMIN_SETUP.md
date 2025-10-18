# 🔐 CliniQ Admin Panel Setup

## Demo Admin Credentials

To access the CliniQ admin panel, you need to create an admin user. Here are the steps:

### Option 1: Using Django Shell
```bash
cd medicalapp
python manage.py shell
```

Then in the Django shell:
```python
from django.contrib.auth.models import User
from adminpanel.models import AdminUser

# Create superuser
user = User.objects.create_superuser(
    username='demo_admin',
    email='admin@cliniq.com',
    password='demo123456',
    first_name='Demo',
    last_name='Administrator'
)

# Create admin profile
admin_profile = AdminUser.objects.create(
    user=user,
    role='super_admin',
    phone_number='+1234567890',
    is_active=True
)

print("Admin user created successfully!")
```

### Option 2: Using Management Command
```bash
cd medicalapp
python manage.py create_demo_admin
```

### Option 3: Using the Script
```bash
cd medicalapp
python create_admin.py
```

## 🎯 Demo Credentials

Once created, use these credentials to login:

- **Username:** `demo_admin`
- **Password:** `demo123456`
- **Email:** `admin@cliniq.com`
- **Role:** Super Administrator

## 📍 Login URLs

- **Django Admin Panel:** http://localhost:8000/admin/
- **CliniQ Admin Panel:** http://localhost:8000/adminpanel/login/

## 🔧 Admin Panel Features

The CliniQ admin panel includes:

1. **Dashboard:** Overview of hospital operations
2. **Department Management:** Manage hospital departments
3. **Doctor Management:** Approve and manage doctors
4. **Queue Management:** Monitor patient queues
5. **Analytics:** View reports and statistics
6. **Notifications:** Manage system notifications
7. **Settings:** Configure system parameters

## 🚀 Quick Start

1. Run the Django development server:
   ```bash
   cd medicalapp
   python manage.py runserver
   ```

2. Create the admin user (use one of the options above)

3. Access the admin panel at: http://localhost:8000/adminpanel/login/

4. Login with the demo credentials

5. Start managing your CliniQ system!

## 🛡️ Security Note

**⚠️ Important:** These are demo credentials for testing purposes only. In production:
- Use strong, unique passwords
- Change default credentials immediately
- Enable two-factor authentication if available
- Regularly update admin passwords