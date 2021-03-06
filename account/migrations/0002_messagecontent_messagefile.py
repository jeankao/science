# Generated by Django 2.1.5 on 2019-01-22 22:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.IntegerField(default=0)),
                ('user_id', models.IntegerField(default=0)),
                ('title', models.CharField(blank=True, max_length=250, null=True)),
                ('filename', models.CharField(blank=True, max_length=250, null=True)),
                ('publication_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='MessageFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_id', models.IntegerField(default=0)),
                ('filename', models.TextField()),
                ('before_name', models.TextField()),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
