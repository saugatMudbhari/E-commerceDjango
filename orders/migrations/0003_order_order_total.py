# Generated by Django 3.1 on 2023-04-15 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20230415_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_total',
            field=models.FloatField(default=0.0),
        ),
    ]
