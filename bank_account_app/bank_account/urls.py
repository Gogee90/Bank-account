from . import views
from django.urls import path


urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login_user"),
    path("registration/", views.user_create, name="user_create"),
    path("", views.list_users, name="list_users"),
    path("list-bank-accounts/", views.list_bank_accounts, name="list_bank_accounts"),
    path(
        "list-bank-accounts/<int:pk>",
        views.bank_account_detail,
        name="bank_account_detail",
    ),
    path("create-bank-account/", views.create_bank_account, name="create_bank_account"),
    path("make-transaction/<int:pk>", views.make_transaction, name="make_transaction"),
    path("list-transactions/", views.list_transactions, name="list_transaction"),
    path(
        "transaction-detail/<int:pk>/",
        views.transaction_detail,
        name="transaction_detail",
    ),
]
