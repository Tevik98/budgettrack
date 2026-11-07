from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.expense_list, name='expense_list'),
    path('accounts/signup/', views.signup, name='signup'),
    path('expenses/add/', views.expense_edit, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('categories/', views.categories, name='categories'),
    path('budgets/', views.budgets, name='budgets'),
]
