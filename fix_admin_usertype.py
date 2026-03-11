import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from accounts.models import User

# Update all superusers to have user_type='admin'
superusers = User.objects.filter(is_superuser=True)
for user in superusers:
    user.user_type = 'admin'
    user.save()
    print(f"Updated {user.username} to admin user_type")

print("Done!")
