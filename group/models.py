from django.db                  import models

from django.utils               import timezone
from django.utils.translation   import gettext_lazy as _
from django.utils               import timezone


class Group(models.Model):
    """
        Group model
    """
    name        = models.CharField(
                    _("Group Name"),
                    unique = True,
                    error_messages={
                        "unique": _("A group with that groupname already exists."),
                    },
                    max_length = 30,
                )
    created_by  = models.ForeignKey("core.User", on_delete = models.CASCADE)
    created_on  = models.DateTimeField(default = timezone.now)
    savings     = models.IntegerField(verbose_name = "Savings", default = 0)
    maintainer  = models.ForeignKey(
                    "core.User", 
                    verbose_name = "Savings Account Maintainer", 
                    on_delete = models.CASCADE,
                    related_name = "maintaining_groups",
                    related_query_name = "maintaining_groups",
                    blank = True,
                    null = True
                )

    def __str__(self):
        return f"{self.name} created by {self.created_by}"

    @property
    def get_members(self):
        """get all members associated with group

        Returns:
            list[User Object]: list of users
        """
        return [x for x in self.members.all().order_by('id')]
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.maintainer = self.created_by
        self.created_by.groups.add(self)
    
    def add_member(self, user):
        user.groups.add(self)
        user.save()
        
    def add_members(self, users):
        for user in users:
            user.groups.add(self)
            user.save()

    @property
    def get_savings_amount(self):
        savings_amount = 0
        
        for transaction in self.transactions.all():
            if transaction.transaction_for != "savings" and transaction.by != User.objects.get("savings"):
                continue

            if transaction.transaction_for == "savings":
                savings_amount += transaction.amount
            if transaction.by == "savings":
                savings_amount -= transaction.amount 

            print("debugger")
             
    def update_savings_amount(self):
        self.savings = self.get_savings_amount
        self.save()
    
class Transaction(models.Model):
    """
        Transaction Model
    """
    transaction_for = models.CharField(verbose_name = "for", max_length = 60) 
    by              = models.ForeignKey("core.User", on_delete = models.CASCADE, related_name = "by")
    to              = models.CharField(verbose_name = "to" , max_length = 60) 
    amount          = models.IntegerField()
    of_group        = models.ForeignKey(Group, on_delete = models.CASCADE, related_name = "transactions")
    on              = models.DateField(default = timezone.now)
    added_by        = models.ForeignKey("core.User", on_delete = models.CASCADE, related_name = "added_by") 
    share_to        = models.ManyToManyField("core.User", related_name = "share_to")

    def __str__(self):
        return f"transaction for {self.transaction_for} by {self.by} on {self.on} to {self.to} of amount {self.amount}"
    
    def save(self, *args, **kwargs):
        # if self.id is None:
        #     if self.transaction_for == "savings" and self.amount > 0:
        #         self.of_group.savings += self.amount
                
        # else:
        #     self.of_group.update_savings_amount()

        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        if self.transaction_for == "savings" and self.amount > 0:
            self.of_group.savings -= self.amount
        if self.by == "savings":
            self.of_group.savings += self.amount
        self.of_group.save()
        super().delete(*args, **kwargs)

