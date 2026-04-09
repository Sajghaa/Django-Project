from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Category, Product, Order, OrderItem
from .cart import Cart
from .forms import CheckoutForm
from decimal import Decimal

def home(request):
    """Home page view"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    new_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
    }
    return render(request, 'store/home.html', context)

def product_list(request, category_slug=None):
    """Product listing page"""
    category = None
    products = Product.objects.filter(is_active=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    context = {
        'products': products,
        'category': category,
        'categories': Category.objects.all(),
    }
    return render(request, 'store/product_list.html', context)

def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'store/product_detail.html', context)

@require_POST
def cart_add(request, product_id):
    """Add product to cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    
    messages.success(request, f'{product.name} added to cart!')
    return redirect('store:cart_detail')

def cart_remove(request, product_id):
    """Remove product from cart"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    
    messages.success(request, f'{product.name} removed from cart!')
    return redirect('store:cart_detail')

def cart_detail(request):
    """View cart details"""
    cart = Cart(request)
    return render(request, 'store/cart_detail.html', {'cart': cart})

def cart_update(request, product_id):
    """Update cart item quantity"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, f'Cart updated!')
    else:
        cart.remove(product)
        messages.success(request, f'{product.name} removed from cart!')
    
    return redirect('store:cart_detail')

def checkout(request):
    """Checkout process"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty!')
        return redirect('store:product_list')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create order
            order = form.save(commit=False)
            order.total_amount = cart.get_total_price()
            
            # If user is logged in, associate order with user
            if request.user.is_authenticated:
                order.user = request.user
                order.email = request.user.email
            
            order.save()
            
            # Create order items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )
            
            # Clear cart
            cart.clear()
            
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('store:order_confirmation', order_id=order.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'store/checkout.html', {
        'form': form,
        'cart': cart
    })

def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'store/order_confirmation.html', {'order': order})

@login_required
def my_orders(request):
    """User's order history"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/orders.html', {'orders': orders})