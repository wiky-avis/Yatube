# Generated by Django 2.2.6 on 2021-04-06 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_delete_topic'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='profile',
            options={'verbose_name': 'Профиль пользователя', 'verbose_name_plural': 'Профили пользователей'},
        ),
    ]
