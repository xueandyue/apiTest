# Generated by Django 2.0.3 on 2020-04-04 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Index', '0004_auto_20200403_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='testreports',
            name='userid',
            field=models.IntegerField(default=0),
        ),
    ]
