# Generated by Django 4.1.3 on 2022-11-21 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_rename_tuyadevicesxxx_tuyadevices'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TuyaDevices',
        ),
    ]