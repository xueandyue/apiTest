# Generated by Django 2.0.3 on 2019-12-12 02:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Index', '0002_debugtalk_envinfo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectinfo',
            old_name='dev',
            new_name='dev_user',
        ),
        migrations.RenameField(
            model_name='projectinfo',
            old_name='tester',
            new_name='test_user',
        ),
    ]
