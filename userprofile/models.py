from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    userAllergies = models.ManyToManyField('products.Allergy', blank=True, verbose_name=u"Allergies")
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class FreshUserIp(models.Model):
    user_id = models.AutoField(primary_key=True, editable=False)
    ip_address = models.CharField(verbose_name=u"ip_address", max_length=150)
    location = models.CharField(verbose_name=u"location", max_length=150)

    def __str__(self):
        return self.ip_address

    class Meta:
        ordering = ["user_id"]
