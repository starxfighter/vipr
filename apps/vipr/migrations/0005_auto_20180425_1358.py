# Generated by Django 2.0.4 on 2018-04-25 20:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vipr', '0004_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='documenter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='document_for', to='vipr.Request'),
        ),
    ]
