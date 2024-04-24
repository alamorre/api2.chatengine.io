import uuid

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

from projects.models import Person


class Session(models.Model):
    person = models.OneToOneField(Person, related_name="session", on_delete=models.CASCADE, blank=True, null=True)
    token = models.CharField(editable=False, max_length=100, null=True, blank=True, default='')
    expiry = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return '{}: {}'.format(self.person.username, self.token)

    class Meta:
        ordering = ('person', '-expiry',)
        indexes = [
            models.Index(fields=['person', '-expiry']),
            models.Index(fields=['token']),
        ]
    def save(self, *args, **kwargs):
        if not self.pk:
            self.token = 'st-{}'.format(str(uuid.uuid4()))
        super(Session, self).save(*args, **kwargs)
