# Generated by Django 4.1.7 on 2023-02-28 14:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthtoken',
            name='access_token',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='oauthtoken',
            name='refresh_token',
            field=models.CharField(max_length=255),
        ),
    ]