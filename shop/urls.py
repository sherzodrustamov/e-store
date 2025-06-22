from django.urls import path
from shop.views import shop, product_detail, add_to_cart, cart_view, clear_cart, remove_from_cart, update_cart, checkout_view, contact, index
urlpatterns = [
    path('', index, name='index'),
    path('shop/', shop, name='shop'),
    path('cart/checkout/', checkout_view, name='checkout'),
    path('contact/', contact, name='contact'),
    path('detail/<int:product_id>/', product_detail, name='product-detail'),
    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', update_cart, name='update_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),

]