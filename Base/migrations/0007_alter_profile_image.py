# Generated by Django 3.2.9 on 2022-02-26 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Base', '0006_alter_profile_zip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=models.ImageField(default='avatar7.png', upload_to='profile_pics/'),
        ),
    ]
