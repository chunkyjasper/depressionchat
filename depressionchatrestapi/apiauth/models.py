from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from django.db.models import Q
from django.db.models import F
from itertools import chain


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.TextField(max_length=30, blank=True)
    avatar = models.ImageField(blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance, nickname=instance.email)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def get_friend_users(self):
        q1 = Friendship.objects.filter(user1_id=self.user.id).annotate(
           friend_id=F("user2__id"), email=F("user2__email"), nickname=F("user2__profile__nickname"), friendship_id=F("id"))
        q2 = Friendship.objects.filter(user2_id=self.user.id).annotate(
            friend_id=F("user1__id"), email=F("user1__email"), nickname=F("user1__profile__nickname"), friendship_id=F("id"))
        return list(chain(q1, q2))

    def get_friendship_relations(self):
        q1 = Friendship.objects.filter(user1_id=self.user.id)
        q2 = Friendship.objects.filter(user2_id=self.user.id)
        return list(chain(q1, q2))

# TODO: restrict friending yourself
class Friendship(models.Model):
    PENDING = 0
    ACCEPTED = 1
    DECLINED = 2
    BLOCKED = 3
    STATUS_CHOICES = ((PENDING, "PENDING"),
                      (ACCEPTED, "ACCEPTED"),
                      (DECLINED, "DECLINED"),
                      (BLOCKED, "BLOCKED"))
    created_date = models.DateTimeField(default=datetime.now, blank=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')
    status = models.IntegerField(choices=STATUS_CHOICES)
    action_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='+')

    class Meta:
        unique_together = ['user1', 'user2']

    def clean(self):
        if self.user1_id >= self.user2_id:
            raise Exception('user1 id must be smaller than user2 id')

    def get_messages(self):
        return Message.objects.filter((Q(to_user=self.user1_id)&Q(from_user=self.user2_id))|
                                          (Q(to_user=self.user2_id)&Q(from_user=self.user1_id)))

    def get_most_recent_message(self):
        return Message.objects.filter((Q(to_user=self.user1_id)&Q(from_user=self.user2_id))|
                                          (Q(to_user=self.user2_id)&Q(from_user=self.user1_id))).last()


class Message(models.Model):
    text = models.TextField(max_length=1000, blank=False)
    timestamp = models.DateTimeField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")

    class Meta:
        ordering = ['timestamp',]