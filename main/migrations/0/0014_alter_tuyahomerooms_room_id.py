# Generated by Django 4.1.3 on 2022-11-20 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_tuyahomerooms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tuyahomerooms',
            name='room_id',
            field=models.PositiveIntegerField(primary_key=True, serialize=False),
        ),
    ]