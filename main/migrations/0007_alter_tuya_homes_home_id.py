# Generated by Django 4.1.3 on 2022-11-19 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_tuya_homes_home_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tuya_homes',
            name='home_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False),
        ),
    ]
