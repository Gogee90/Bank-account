from django.forms import (
    CharField,
    EmailField,
    ModelForm,
    Form,
    PasswordInput,
    ValidationError,
)
from .models import BankAccount, Transaction


class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = ["bank_account", "amount"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields["bank_account"].queryset = BankAccount.objects.filter(owner=user)

    def clean(self):
        bank_accounts = self.cleaned_data["bank_account"]
        amount = self.cleaned_data["amount"]
        subtracted_amount = amount / bank_accounts.count() if amount else 0

        if amount == 0 or not amount:
            raise ValidationError({"amount": ["The amount cannot be zero or empty!"]})

        for bank_account in bank_accounts:
            if bank_account.amount < subtracted_amount:
                raise ValidationError({"bank_account": ["Insufficient funds!"]})

        return self.cleaned_data


class BankAccountForm(ModelForm):
    class Meta:
        model = BankAccount
        fields = ["amount"]


class RegistrationForm(Form):
    username = CharField(label="Username", max_length=100)
    password = CharField(label="Password", widget=PasswordInput)
    password2 = CharField(label="Password again", widget=PasswordInput)
    email = EmailField(max_length=50)
    first_name = CharField(label="First name", max_length=30)
    last_name = CharField(label="Last name", max_length=50)
