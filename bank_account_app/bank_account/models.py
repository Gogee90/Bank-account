import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class BankAccount(models.Model):
    owner = models.ForeignKey(
        User,
        related_name="owner",
        verbose_name="Owner",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    amount = models.FloatField(
        verbose_name="Current Amount", default=0, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.owner.username} {self.amount} $"

    verbose_name = "Bank Account"
    verbose_name_plural = "Bank Accounts"


class Transaction(models.Model):
    sender = models.ForeignKey(
        User,
        related_name="sender",
        verbose_name="Sender",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    recipient = models.ForeignKey(
        User,
        related_name="recipient",
        verbose_name="Recipient",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    recipient_bank_account = models.ForeignKey(
        BankAccount,
        related_name="recipient_bank_account",
        verbose_name="Recipient bank account",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    bank_account = models.ManyToManyField(
        BankAccount, blank=True, verbose_name="Bank Account"
    )
    amount = models.FloatField(verbose_name="Amount", default=0, null=True, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sender.username} {self.amount} {self.recipient.username}"

    verbose_name = "Transaction"
    verbose_name_plural = "Transactions"
