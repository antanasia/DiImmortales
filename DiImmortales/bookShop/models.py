from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime


class Genre(models.Model):
    genreName = models.CharField(_("Название жанра"), max_length=255)

    class Meta:
        verbose_name = _("Жанр")
        verbose_name_plural = _("Жанры")

    def __str__(self):
        return self.genreName


class Book(models.Model):
    bookName = models.CharField(_("Название книги"), max_length=255)
    bookAuthor = models.CharField(_("Автор книги"), max_length=255)
    pages = models.IntegerField(_("Количество страниц"))
    description = models.TextField(_("Описание книги"))
    price = models.FloatField(_("Цена"))
    bookImage = models.CharField(_("Изображение книги"), max_length=255, default="")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name=_("Жанр"))

    class Meta:
        verbose_name = _("Книга")
        verbose_name_plural = _("Книги")

    def __str__(self):
        return self.bookName


class New(models.Model):
    title = models.CharField(_("Заголовок"), max_length=255)
    content = models.TextField(_("Содержание новости"))
    newsDate = models.DateTimeField(_("Дата"), default=datetime.now)
    newsImage = models.CharField(_("Изображение новости"), max_length=255, default="")

    class Meta:
        verbose_name = _("Новость")
        verbose_name_plural = _("Новости")

    def __str__(self):
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE, null=True)
    review_content = models.TextField("Содержание отзыва", blank=True)
    avatar = models.ImageField("Аватар пользователя", upload_to='review_avatars/', null=True, blank=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        if self.user:
            return f"Отзыв от {self.user.username}"
        else:
            return "Отзыв без пользователя"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    books = models.ManyToManyField(Book, through='CartItem', verbose_name=_("Книги"))
    total_price = models.FloatField(_("Общая цена"), default=0.0)

    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")

    def calculate_total_price(self):
        self.total_price = sum(item.total_price for item in self.cart_items.all())
        self.save()

    def __str__(self):
        return f"Корзина для {self.user.username}"


class CartItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_("Книга"))
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items', verbose_name=_("Корзина"))
    quantity = models.PositiveIntegerField(_("Количество"), default=1)
    total_price = models.FloatField(_("Общая цена"), default=0.0)

    class Meta:
        verbose_name = _("Элемент корзины")
        verbose_name_plural = _("Элементы корзины")

    def save(self, *args, **kwargs):
        self.total_price = self.book.price * self.quantity
        super().save(*args, **kwargs)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, verbose_name=_("Пользователь"))
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name=_("Книга"))

    class Meta:
        verbose_name = _("Избранное")
        verbose_name_plural = _("Избранные")

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.book.bookName}"
        else:
            return f"Неавторизованный - {self.book.bookName}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='ID платежного намерения Stripe')
    status = models.CharField(max_length=50, default='pending', verbose_name='Статус')

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Заказ')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая цена')

    def __str__(self):
        return f"{self.book.bookName} ({self.quantity})"

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg', verbose_name="Аватар")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username
