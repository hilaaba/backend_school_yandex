# Generated by Django 2.2.19 on 2022-09-13 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False, unique=True)),
                ('type', models.CharField(choices=[('FILE', 'файл'), ('FOLDER', 'папка')], max_length=6, verbose_name='Тип')),
                ('date', models.DateTimeField(verbose_name='Дата')),
                ('url', models.CharField(max_length=255, null=True, verbose_name='Адрес')),
                ('size', models.PositiveIntegerField(null=True, verbose_name='Размер')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='api.Item', verbose_name='Родитель')),
            ],
            options={
                'verbose_name': 'Элемент',
                'verbose_name_plural': 'Элементы',
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('FILE', 'файл'), ('FOLDER', 'папка')], max_length=6)),
                ('date', models.DateTimeField(verbose_name='Дата')),
                ('url', models.CharField(max_length=255, null=True, verbose_name='Адрес')),
                ('size', models.PositiveIntegerField(null=True, verbose_name='Размер')),
                ('parentId', models.UUIDField(null=True)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='api.Item', verbose_name='Элемент')),
            ],
            options={
                'verbose_name': 'История',
                'verbose_name_plural': 'История',
            },
        ),
    ]
