from django.urls import path
from . import views
from .views import stripe_webhook

urlpatterns = [
    path('', views.homePage, name='homePage'),
    path('index', views.homePage, name='index'),
    path('book/<int:pk>', views.bookDetail, name='bookDetail'),
    path('catalog/', views.catalogPage, name='catalogPage'),
    path('news/', views.newsPage, name='newsPage'),
    path('reviews/', views.reviewsPage, name='reviewsPage'),
    path('new/<int:pk>', views.newsDetail, name='newsDetail'),
    path('sign-up/', views.signUp, name='signUp'),
    path('login/', views.signIn, name='signIn'),
    path('sign-out/', views.signOut, name='signOut'),
    path('search/', views.Search.as_view(), name='search'),
    path('add_to_cart/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),
    path('update_quantity/<int:item_id>/<str:action>/', views.update_quantity, name='update_quantity'),
    path('remove_item/<int:item_id>/', views.remove_item, name='remove_item'),
    path('cart/total_price/', views.get_cart_total_price, name='cart_total_price'),
    path('favorite/', views.favorite, name='favorite'),
    path('add_to_favorites/<int:book_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('get_favorites/', views.get_favorites, name='get_favorites'),
    path('create-payment-intent/', views.create_payment_intent, name='create_payment_intent'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
    path('profile/', views.profile, name='profile'),
    path('checkout/', views.checkout, name='checkout'),
    path('change_username/', views.change_username, name='change_username'),
    path('change_email/', views.change_email, name='change_email'),
    path('change_password/', views.change_password, name='change_password'),
    path('change_avatar/', views.change_avatar, name='change_avatar'),
    path('write_review/', views.write_review, name='write_review'),
]
