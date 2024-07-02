from django.contrib import admin
from .models import Book, New, Review, Genre, Cart, CartItem, Favorite, Order, OrderItem


admin.site.register(New)
admin.site.register(Review)
admin.site.register(Book)
admin.site.register(Genre)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Favorite)
admin.site.register(Order)
admin.site.register(OrderItem)


