# Generated by Django 2.0.4 on 2018-04-25 22:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vipr', '0005_auto_20180425_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='documenter',
        ),
        migrations.AddField(
            model_name='document',
            name='documenter',
            field=models.ManyToManyField(related_name='document_for', to='vipr.Request'),
        ),
    ]
