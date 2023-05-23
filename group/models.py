from django.db import models

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Group(models.Model):
    name    = models.CharField(
                _("Group Name"),
                unique = True,
                error_messages={
                    "unique": _("A group with that groupname already exists."),
                },
                max_length = 30,
            )
    created_by = models.ForeignKey("core.User", on_delete = models.CASCADE)
    created_on = models.DateTimeField(default = timezone.now)

    def __str__(self):
        return f"{self.name} created by {self.created_by}"

    @property
    def get_members(self):
        return [x for x in self.members.all()]
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.created_by.groups.add(self)
    
    def add_member(self, user):
        user.groups.add(self)
        
    def add_members(self, users):
        for user in users:
            user.groups.add(self)
        