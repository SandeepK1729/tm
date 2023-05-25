from django.urls        import path, include
from .                  import views

urlpatterns = [
    path('groups', views.groups_view, name = "groups"),
    path('group/<int:id>', views.group_view, name = "group"),
    path('group/<int:id>/remove_member/<str:username>', views.remove_group_member, name = "remove group member"),

    path('group/<int:id>/transactions', views.group_transactions_view, name = "transactions"),
    path('group/<int:id>/transactions/add', views.add_group_transaction_view, name = "add transaction"),

    path('group/<int:id>/api/transactions', views.api_group_transactions_view, name = "transactions api"),

    path('group/<int:id>/monthly_split', views.group_transactions_monthly_split, name = "transactions monthly split"),
]
