# Generated by Django 2.0 on 2017-12-22 19:21

from django.db import migrations


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('apiauth', '0002_auto_20171222_1911'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Chat',
            new_name='FriendRelation',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='chat',
            new_name='friends_relation',
        ),
    ]