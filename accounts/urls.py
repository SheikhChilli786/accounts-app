from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.login_page,name='home-page'),
    path('login',views.login_page,name='login-page'),
    path('logout',views.logout_user,name='logout'),
    path('user_login',views.login_user,name='login-user'),
    # operation regarding users
    path('users',views.users_list,name='users-list'),
    path('users/<int:pk>',views.parties,name='party-list-pk'),
    path('save_user',views.save_user,name='save-user'),
    path('manage_user',views.manage_user,name='manage-user'),
    path('manage_user/<int:pk>',views.manage_user,name='manage-user-pk'),
    path('delete_user/<int:pk>',views.delete_user,name='delete-user'),
    path('restore_user/<int:pk>',views.restore_user,name='restore-user'),
    ### operations regarding party
    path('parties',views.parties,name='party-list'),
    path('save_party',views.save_party,name='save-party'),
    path('manage_party/<int:pk>',views.manage_party,name='manage-party-pk'),
    path('manage_party_new/<int:pk>',views.manage_party_new,name='manage-party-new'),
    path('delete_party/<int:pk>',views.delete_party,name='delete-party'),
    path('restore_party/<int:pk>',views.restore_party,name='restore-party'),
    ### operations regarding transactions
    path('manage_transaction/<int:pk>',views.manage_transaction,name='manage-transaction'),
    path('save_transactions/', views.save_transaction, name='save-transaction'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('edit_transaction/<int:pk>', views.edit_transaction, name='edit-transaction'),
    path('delete_transaction/<int:pk>', views.delete_transaction, name='delete-transaction'),
    path('restore_transaction/<int:pk>', views.restore_transaction, name='restore-transaction'),
    path('range_transactions/<int:pk>', views.range_transaction, name='range-transactions-pk'),
    path('view_transactions/<int:pk>', views.view_transactions, name='view-transactions'),
    path('recycle_bin/', views.recycle_bin, name='recycle-bin'),

]