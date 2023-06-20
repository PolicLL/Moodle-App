from django.db import migrations


def create_roles(apps, schema_editor):
    Role = apps.get_model('app', 'Role')
    roles = ['ADMIN', 'STUDENT', 'MENTOR']
    Role.objects.bulk_create([Role(name=role) for role in roles])


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_role_alter_user_role'),  # Replace with the previous migration file name
    ]

    operations = [
        migrations.RunPython(create_roles),
    ]
