# Generated by Django 2.0.4 on 2018-04-25 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vipr', '0002_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='charge_id',
            field=models.CharField(default=0, max_length=234),
            preserve_default=False,
        ),
    ]
