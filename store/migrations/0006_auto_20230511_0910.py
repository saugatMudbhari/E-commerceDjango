# Generated by Django 3.1 on 2023-05-11 03:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_remove_reviewrating_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color')], max_length=100),
        ),
    ]
