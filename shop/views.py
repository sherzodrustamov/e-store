from shop.models import Product, Category
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
import json
import requests
from aiogram import Bot, Dispatcher
import asyncio
from django.core.paginator import Paginator
from shop.forms import ContactForm

BOT_TOKEN = '7989356838:AAFdDxBggL1BFvXFB3AOitSAmDqavK0JJNc'
CHAT_ID = '6360630311'
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def index(request):
    products = Product.objects.all().order_by('-created_date')
    category_id = request.GET.get('category', None)
    categories = Category.objects.all()
    context = {
        'products': products,
        'category_id': category_id,
        'categories': categories
    }

    return render(request, 'index.html', context)


def shop(request):
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', None)
    products = Product.objects.order_by('-title').all()
    if query:
        products = products.filter(title__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'category_id': category_id,
    }

    return render(request, 'shop.html', context)


def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:8]
    return render(request, 'product-detail.html', {'product': product, 'related_products': related_products})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)] += 1
    else:
        cart[str(product_id)] = 1

    request.session['cart'] = cart
    return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


def cart_view(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = [
        {
            'product': product,
            'quantity': cart[str(product.id)],
            'subtotal': cart[str(product.id)] * product.price
        }
        for product in products
    ]

    total_price = sum(item['subtotal'] for item in cart_items)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        del cart[str(product_id)]

    request.session['cart'] = cart
    return JsonResponse({'success': True, 'cart_count': sum(cart.values())})


def clear_cart(request):
    request.session['cart'] = {}
    return JsonResponse({'success': True})


def update_cart(request, product_id):
    cart = request.session.get('cart', {})
    data = json.loads(request.body)
    action = data.get('action')

    if action == 'increase':
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    elif action == 'decrease' and cart.get(str(product_id), 0) > 1:
        cart[str(product_id)] -= 1

    request.session['cart'] = cart
    return JsonResponse({'success': True})


def checkout_view(request):
    if request.method == 'POST':

        full_name = request.POST.get('full_name')
        card_number = request.POST.get('card_number')
        phone_number = request.POST.get('phone_number')
        cart = request.session.get('cart', {})

        if not full_name and not phone_number or not card_number:
            return render(request, 'checkout.html', {'error': 'Please fill out all fields.'})

        products = Product.objects.filter(id__in=cart.keys())
        total_price = sum(cart[str(product.id)] * product.price for product in products)

        telegram_message = "🛍 **Yangi Buyurtma**\n"
        telegram_message += f"**Shaxs:** {full_name}\n"
        telegram_message += f"**Telefon:** {phone_number}\n"
        telegram_message += "**Mahsulotlar:**\n"

        for product in products:
            quantity = cart[str(product.id)]
            subtotal = quantity * product.price
            telegram_message += f"• {product.title} (x{quantity}) - ${subtotal:.2f}\n\n"

        telegram_message += f"**Jami To'lov:** ${total_price:.2f}"

        bot_token = '8102922732:AAGgJZFI9xRS-usEkCqtSEV03kW5Ur4Lst8'
        chat_id = '7380593368'
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            data={'chat_id': chat_id, 'text': telegram_message, 'parse_mode': 'Markdown'}
        )
        request.session['cart'] = {}
        return render(request, 'success.html', {'full_name': full_name, 'total_price': total_price})

    return render(request, 'checkout.html')


def contact(request):
    contact_form = ContactForm()
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        if not name and not surname or not phone:
            return render(request, 'contact.html', {'error': 'Please fill out all fields.'})

        contact_message = f"Sizga yangi xabar 💬\n\nIsmi: {name}\nFamiliyasi: {surname}\nTel raqami: {phone}\nXabar: {message}"

        bot_token = '7989356838:AAFdDxBggL1BFvXFB3AOitSAmDqavK0JJNc'
        chat_id = '6360630311'
        requests.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            data={'chat_id': chat_id, 'text': contact_message, 'parse_mode': 'Markdown'}
        )
        return render(request, 'contact_success.html', {'name': name, 'message': message})

    context = {
        'contact_form': contact_form
    }
    return render(request, 'contact.html', context)


def custom_404_view(request, exception):
    return render(request, '404.html', status=404)
