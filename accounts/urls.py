from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.client, name="home-client"),
    path('users/<int:pk>',views.client, name="home-client-pk"),
    path('save_party',views.save_party,name='save-party'),
    path('manage_party',views.manage_party,name='manage-party'),
    path('manage_form/<int:pk>',views.manage_form,name='manage-form'),
    path('manage_party/<int:pk>',views.manage_party,name='manage-party-pk'),
    path('manage_party_new/<int:pk>',views.manage_party_new,name='manage-party-new'),
    path('delete_party/<int:pk>',views.delete_party,name='delete-party'),
    path('login',views.login_page,name='login-page'),
    path('user_login',views.login_user,name='login-user'),
    path('users',views.home,name='home-page'),
    path('manage_user/<int:pk>',views.manage_user,name='manage-user-pk'),
    path('manage_user',views.manage_user,name='manage-user'),
    path('save_user',views.save_user,name='save-user'),
    path('delete_user/<int:pk>',views.delete_user,name='delete-user'),
    path('logout',views.logout_user,name='logout'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('save_transactions/', views.save_form, name='save-form'),
    path('edit_transactions/<int:pk>', views.edit_transaction, name='edit-transaction'),

]