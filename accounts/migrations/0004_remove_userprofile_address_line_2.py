# Generated by Django 3.1 on 2023-05-11 03:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_userprofile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='address_line_2',
        ),
    ]
