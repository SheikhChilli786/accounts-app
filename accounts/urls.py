from django.urls import path
from accounts.views import *

app_name='accounts'
urlpatterns = [
    path('',user_detail,name='user-detail-pk'),
    path("auth/users/<int:pk>", user_detail,name = 'user-detail-pk'),
    path("parties", user_detail,name = 'user-detail'),
    path('manage_party',manage_party,name='manage-party'),
    path('save_party',save_party,name='save-party'),
    path('manage_party/<int:pk>',manage_party,name='manage-party-pk'),
    path('delete_party/<int:pk>',delete_party,name='delete-party'),
    path('manage_transaction/<int:pk>/',manage_transaction,name='manage-transaction'),
    path('manage_transaction/',manage_transaction,name='manage-transaction'),
    path('save_transactions/', save_transaction, name='save-transaction'),
    path('transactions_list/',transaction_list, name='transaction_list'),
    path('delete_transaction/<int:pk>', delete_transaction, name='delete-transaction'),
    path('view_transactions/<int:pk>', view_transactions, name='view-transactions'),
    path('manage_sales_purchase',manage_sales_purchases,name='manage-sales-purchase'),
    path('manage_sales_purchase/<int:pk>/',manage_sales_purchases,name='manage-sales-purchase'),
    path('save_trade',save_trade,name="save-trade"),
    path('sales_list/',sales_list, name='sales_list'),
    path('purchases_list/',purchases_list, name='purchases_list'),
    path('products/',products,name="products"),
    path('products/<int:pk>',products,name="products-pk"),
    path('manage_products/',manage_products,name="manage-products"),
    path('manage_products/<int:pk>',manage_products,name="manage-products-pk"),
    path('save_products/',save_product,name="save-product"),
    path('delete_product/<int:pk>',delete_product,name="delete-product"),
    path('print/<int:pk>',print_veiw,name="print-view-pk"),
]