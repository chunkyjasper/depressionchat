# Generated by Django 2.0 on 2017-12-24 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiauth', '0007_auto_20171222_2100'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['timestamp']},
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, upload_to=''),
        ),
    ]
