# Generated by Django 2.1.2 on 2019-01-24 06:13

from django.db import migrations, models
import django.utils.timezone
import student.models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_science1content_science1question_science1work_science2json_science3work_science4debug_science4work'),
    ]

    operations = [
        migrations.CreateModel(
            name='Work',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(default=0)),
                ('lesson_id', models.IntegerField(default=0)),
                ('typing', models.IntegerField(default=0)),
                ('index', models.IntegerField()),
                ('memo', models.TextField()),
                ('memo_c', models.IntegerField(default=0)),
                ('memo_e', models.IntegerField(default=0)),
                ('publish', models.BooleanField(default=False)),
                ('publication_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('score', models.IntegerField(default=-2)),
                ('scorer', models.IntegerField(default=0)),
                ('file', models.FileField(upload_to='')),
                ('picture', models.ImageField(default='/static/python/null.jpg', upload_to=student.models.upload_path_handler)),
                ('code', models.TextField(default='')),
                ('helps', models.IntegerField(choices=[(0, '全部靠自己想'), (1, '同學幫一點忙'), (2, '同學幫很多忙'), (3, '老師幫一點忙'), (4, '老師幫很多忙')], default=0)),
                ('answer', models.BooleanField(default=False)),
                ('youtube', models.TextField(default='')),
                ('comment', models.TextField(default='')),
            ],
        ),
        migrations.CreateModel(
            name='WorkFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('work_id', models.IntegerField(default=0)),
                ('filename', models.TextField()),
                ('upload_date', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]