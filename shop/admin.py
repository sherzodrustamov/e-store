from django.contrib import admin

from shop.models import Product, Category, ContactUser


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(ContactUser)
