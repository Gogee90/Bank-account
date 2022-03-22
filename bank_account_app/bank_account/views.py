from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.views import View
from .models import BankAccount, Transaction
from .forms import BankAccountForm, RegistrationForm, TransactionForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required


# Create your views here.
class LoginView(View):
    def post(self, request):
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return HttpResponseRedirect("/admin")
        if user is not None and not user.is_staff:
            login(request, user)
            return HttpResponseRedirect("/")
        return render(request, "bank_account/login.html")

    def get(self, request):
        return render(request, "bank_account/login.html")


def user_create(request):
    registration_form = RegistrationForm(request.POST)
    if request.method == "POST":
        if registration_form.is_valid():
            username = registration_form.cleaned_data["username"]
            password = registration_form.cleaned_data["password"]
            first_name = registration_form.cleaned_data["first_name"]
            last_name = registration_form.cleaned_data["last_name"]
            email = registration_form.cleaned_data["email"]
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.password2 = password
            user.save()
            return redirect("list_bank_accounts")
        else:
            registration_form = RegistrationForm()
    return render(
        request,
        "bank_account/registration.html",
        {
            "registration_form": registration_form,
        },
    )


@login_required
def list_users(request):
    queryset = User.objects.all()
    if not request.user.is_anonymous:
        queryset = queryset.exclude(username=request.user.username)
    if request.GET.get("search_term"):
        search_term = request.GET.get("search_term")
        queryset = queryset.filter(
            Q(username__icontains=search_term)
            | Q(email__icontains=search_term)
            | Q(first_name__icontains=search_term)
            | Q(last_name__icontains=search_term)
        )
    context = {
        "users": queryset,
    }
    return render(request, "bank_account/users.html", context)


@login_required
def make_transaction(request, pk):
    bank_account = get_object_or_404(BankAccount, pk=pk)
    current_user = request.user if not request.user.is_anonymous else None
    form = TransactionForm(data=request.POST, user=current_user)
    if request.method == "POST":
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.sender = current_user
            transaction.recipient = bank_account.owner
            transaction.amount = form.cleaned_data["amount"]
            transaction.recipient_bank_account = bank_account

            if transaction.amount:
                bank_account.amount += transaction.amount
                bank_account.save()

            subtracted_amount = (
                transaction.amount / form.cleaned_data["bank_account"].count()
            )

            for account in form.cleaned_data["bank_account"]:
                account.amount -= subtracted_amount
                account.save()

            transaction.save()
            form.save_m2m()

            return redirect("list_bank_accounts")

    return render(request, "bank_account/transaction_form.html", {"form": form})


@login_required
def cancel_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)

    returned_amount = transaction.amount / transaction.bank_account.all().count()

    for bank_account in transaction.bank_account.all():
        bank_account.amount += returned_amount
        bank_account.save()

    if transaction.recipient_bank_account:
        transaction.recipient_bank_account.amount -= transaction.amount
        transaction.recipient_bank_account.save()

    transaction.status = False
    transaction.amount -= transaction.amount
    transaction.save()
    return redirect("list_transaction")


@login_required
def list_transactions(request):
    queryset = Transaction.objects.all().order_by("created_at")

    if not request.user.is_anonymous:
        queryset = queryset.filter(sender=request.user)

    if request.GET.get("start_date"):
        queryset = queryset.filter(created_at__gte=request.GET.get("start_date"))

    if request.GET.get("end_date"):
        queryset = queryset.filter(created_at__lte=request.GET.get("end_date"))

    if request.GET.get("start_date") and request.GET.get("end_date"):
        queryset = queryset.filter(
            created_at__gte=request.GET.get("start_date"),
            created_at__lte=request.GET.get("end_date"),
        )
    if request.GET.get("amount"):
        queryset = queryset.filter(amount__icontains=request.GET.get("amount"))

    if request.GET.get("search_term"):
        search_term = request.GET.get("search_term")
        queryset = queryset.filter(
            Q(sender__username__icontains=search_term)
            | Q(recipient__username__icontains=search_term)
            | Q(bank_account__id__icontains=search_term)
        )

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "bank_account/transactions_list.html", {"page_obj": page_obj}
    )


@login_required
def transaction_detail(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    context = {"transaction": transaction}
    return render(request, "bank_account/transaction_detail.html", context)


@login_required
def list_bank_accounts(request):
    current_user = request.user if not request.user.is_anonymous else None
    queryset = BankAccount.objects.filter(owner=current_user)
    context = {"bank_accounts": queryset}
    return render(request, "bank_account/bank_accounts.html", context)


@login_required
def create_bank_account(request):
    form = BankAccountForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            bank_account = form.save(commit=False)
            bank_account.owner = request.user
            bank_account.amount = form.cleaned_data["amount"]
            bank_account.save()
            return redirect("list_users")
        else:
            form = BankAccountForm()
    return render(request, "bank_account/create_bank_account.html", {"form": form})


@login_required
def bank_account_detail(request, pk):
    queryset = get_object_or_404(BankAccount, pk=pk)
    context = {"bank_account": queryset}
    return render(request, "bank_account/bank_account_detail.html", context)
