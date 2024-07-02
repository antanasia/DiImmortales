from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .forms import RegisterForm, ChangeUsernameForm, ChangeEmailForm, ChangePasswordForm, AvatarChangeForm, ReviewForm
from .models import Book, New, Review, Genre, Cart, CartItem, Favorite, Order, OrderItem, Profile
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse,  HttpResponse, HttpResponseBadRequest
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import logging
from django.contrib.auth import update_session_auth_hash


def homePage(request):
    books = Book.objects.all()
    news = New.objects.all()
    reviews = Review.objects.all()
    return render(request, "index.html", {
        'books': books,
        'news': news,
        'reviews': reviews
    })


def bookDetail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, "book-detail.html", {
        'book': book
    })


def catalogPage(request):
    books = Book.objects.all()
    genres = Genre.objects.all()

    GENREID = request.GET.get('genre')
    if GENREID:
        books = Book.objects.filter(genre=GENREID)
    else:
        books = Book.objects.all()

    return render(request, "catalog.html", {
        'books': books,
        'genres': genres,
    })


class Search(ListView):
    template_name = 'catalog.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.filter(bookName__icontains=self.request.GET.get('q'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q')
        return context


def newsPage(request):
    news = New.objects.all()
    return render(request, "news.html", {
        'news': news,
    })


def reviewsPage(request):
    reviews = Review.objects.all()
    return render(request, "reviews.html", {
        'reviews': reviews
    })


def newsDetail(request, pk):
    new = get_object_or_404(New, pk=pk)
    return render(request, "news-detail.html", {
        'new': new,
    })


def signUp(request):
    if request.user.is_authenticated:
        return redirect('/login')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Успешно создан аккаунт ' + user)
                return redirect('/login')
        else:
            form = RegisterForm()

        return render(request, 'registration/sign-up.html', {
            'form': form
        })


def signIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/index')
        else:
            messages.info(request, 'Имя пользователя или пароль введены неправильно')

    context = {}
    return render(request, 'registration/login.html', context)


def signOut(request):
    context = {}
    return render(request, 'registration/sign-out.html', context)


@login_required(login_url='/login/')
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, book=book)

    if not item_created:
        cart_item.quantity += 1
        cart_item.save()

    cart.calculate_total_price()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='/login/')
def view_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    stripe_public_key = settings.STRIPE_PUBLISHABLE_KEY if request.user.is_authenticated else None
    return render(request, 'cart_template.html', {'cart': cart, 'stripe_public_key': stripe_public_key})


@login_required(login_url='/login/')
def update_quantity(request, item_id, action):
    cart_item = get_object_or_404(CartItem, id=item_id)

    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()

    cart_item.save()

    cart_item.cart.calculate_total_price()

    return JsonResponse({
        'quantity': cart_item.quantity,
        'total_price': cart_item.total_price,
        'cart_total_price': cart_item.cart.total_price,
    })


@login_required(login_url='/login/')
def remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart = cart_item.cart
    cart_item.delete()
    cart.calculate_total_price()

    return JsonResponse({
        'success': True,
        'cart_total_price': cart.total_price,
    })


@login_required(login_url='/login/')
def get_cart_total_price(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return JsonResponse({'total_price': cart.total_price})


def favorite(request):
    favorite_items = Favorite.objects.all()
    return render(request, 'favorite.html', {'favorite_items': favorite_items})


def add_to_favorites(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    user = request.user if request.user.is_authenticated else None
    try:
        favorite = Favorite.objects.get(user=user, book_id=book_id)
        favorite.delete()
        return JsonResponse({'status': 'success'})
    except Favorite.DoesNotExist:
        Favorite.objects.create(user=user, book=book)
        return JsonResponse({'status': 'success'})


def get_favorites(request):
    favorite_books = list(Favorite.objects.all().values_list('book_id', flat=True))
    return JsonResponse({'favorite_books': favorite_books})


stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def create_payment_intent(request):
    if request.method == 'POST':
        try:
            cart = request.user.cart
            total_price = cart.total_price

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'kzt',
                        'product_data': {
                            'name': 'Total Order',
                        },
                        'unit_amount': int(total_price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://127.0.0.1:8000/write_review/',
            )

            order = Order.objects.create(
                user=request.user,
                stripe_payment_intent_id=session.payment_intent,
            )

            for item in cart.cart_items.all():
                OrderItem.objects.create(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    total_price=item.total_price,
                )

            return JsonResponse({'sessionId': session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=403)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def stripe_webhook(request):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only POST requests are allowed')

    payload = request.body
    sig_header = request.headers.get('Stripe-Signature', None)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    else:
        return HttpResponse(status=200)


def handle_checkout_session_completed(session):
    try:
        order = Order.objects.get(stripe_payment_intent_id=session['payment_intent'])
        order.status = 'completed'
        order.save()
    except Order.DoesNotExist:
        return
    except Exception as e:
        return


@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    user_reviews = Review.objects.filter(user=user)
    return render(request, 'profile.html', {'user': user, 'orders': orders, 'user_reviews': user_reviews})


@login_required
def change_avatar(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        avatar_form = AvatarChangeForm(request.POST, request.FILES, instance=profile)
        if avatar_form.is_valid():
            avatar_form.save()
            messages.success(request, 'Аватар успешно обновлен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки.')
    else:
        avatar_form = AvatarChangeForm(instance=profile)

    return render(request, 'changing/change_avatar.html', {'avatar_form': avatar_form})


def checkout(request):
    return render(request, 'stripe_checkout.html')


@login_required
def change_username(request):
    if request.method == 'POST':
        form = ChangeUsernameForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.username = form.cleaned_data['new_username']
            request.user.save()
            messages.success(request, 'Имя пользователя успешно изменено.')
            return redirect('profile')
    else:
        form = ChangeUsernameForm(user=request.user)
    return render(request, 'changing/change_username.html', {'form': form})


@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, user=request.user)
        if form.is_valid():
            request.user.email = form.cleaned_data['new_email']
            request.user.save()
            messages.success(request, 'Электронная почта успешно изменена.')
            return redirect('profile')
    else:
        form = ChangeEmailForm(user=request.user)
        return render(request, 'changing/change_email.html', {'form': form})


@login_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Пароль успешно изменен.')
            return redirect('profile')
        else:
            messages.error(request, 'Произошла ошибка при изменении пароля.')
    else:
        form = ChangePasswordForm(user=request.user)
    return render(request, 'changing/change_password.html', {'form': form})


@login_required
def write_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('reviewsPage')
    else:
        form = ReviewForm()
    return render(request, 'write_review.html', {'form': form})



