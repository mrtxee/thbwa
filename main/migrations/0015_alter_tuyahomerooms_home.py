# Generated by Django 4.1.3 on 2022-11-20 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_tuyahomerooms_room_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tuyahomerooms',
            name='home',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.tuyahomes'),
        ),
    ]
