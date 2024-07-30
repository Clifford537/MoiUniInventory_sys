from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Transaction, Store
from .forms import ProductForm, TransactionForm, StoreForm
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def dashboard_view(request):
    products = Product.objects.order_by('-date')[:15]
    transactions = Transaction.objects.order_by('-date')[:15]
    stores = Store.objects.all()
    return render(request, 'dashboard.html', {
        'products': products,
        'transactions': transactions,
        'stores': stores
    })

@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
def transaction_view(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            product = transaction.product
            if transaction.transaction_type == 'issue' and product.quantity >= transaction.quantity:
                product.quantity -= transaction.quantity
            elif transaction.transaction_type == 'receive':
                product.quantity += transaction.quantity
            product.save()
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm()
    return render(request, 'transaction.html', {'form': form})

@login_required
def add_store_view(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = StoreForm()
    return render(request, 'add_store.html', {'form': form})

@login_required
def manage_items_view(request):
    query = request.GET.get('q')
    store_id = request.GET.get('store')
    date_added = request.GET.get('date_added')
    
    products = Product.objects.all().order_by('-date')  # Default ordering by date, adjust as needed
    
    if query:
        products = products.filter(
            Q(item_name__icontains=query) |
            Q(item_description__icontains=query) |
            Q(remarks__icontains=query)
        ).distinct()
    
    if store_id:
        products = products.filter(store_id=store_id)
    
    if date_added:
        products = products.filter(date=date_added)
    
    paginator = Paginator(products, 30)  # Show 30 products per page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    stores = Store.objects.all()
    
    total_quantity = Product.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_price = Product.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'products': products,
        'stores': stores,
        'total_quantity': total_quantity,
        'total_price': total_price,
    }
    return render(request, 'manage_items.html', context)



@login_required
def manage_stores_view(request):
    stores = Store.objects.all()
    return render(request, 'manage_stores.html', {'stores': stores})

@login_required
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_items')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form})

@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('manage_items')

@login_required
def edit_store_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('manage_stores')
    else:
        form = StoreForm(instance=store)
    return render(request, 'edit_store.html', {'form': form})

@login_required
def delete_store_view(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    store.delete()
    return redirect('manage_stores')

def product_movement_view(request):
    # Retrieve transactions and optionally filter by date and time
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    transactions = Transaction.objects.all()

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if start_time:
        transactions = transactions.filter(time__gte=start_time)
    if end_time:
        transactions = transactions.filter(time__lte=end_time)

    transactions = transactions.order_by('-date')[:15]  # Limit to 15 most recent

    return render(request, 'product_movement.html', {'transactions': transactions})

@login_required
def charts_view(request):
    products = Product.objects.all()
    broken_goods_count = products.filter(remarks__icontains='broken').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_product_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    available_products_count = total_product_quantity - broken_goods_count

    product_names = [product.item_name for product in products]
    product_quantities = [product.quantity for product in products]

    stores = Store.objects.annotate(total_products=Count('products'))
    store_names = [store.name for store in stores]
    store_product_counts = [store.total_products for store in stores]

    total_product_amount = products.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_product_amount = '{:,.3f}'.format(total_product_amount)

    context = {
        'product_names': product_names,
        'product_quantities': product_quantities,
        'store_names': store_names,
        'store_product_counts': store_product_counts,
        'total_product_quantity': total_product_quantity,
        'total_product_amount': total_product_amount,
        'broken_quantity_count': broken_goods_count,
        'available_products_count': available_products_count,
    }

    return render(request, 'charts.html', context)
