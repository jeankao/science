# Generated by Django 2.1.2 on 2019-01-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0003_work_workfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='science1content',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
