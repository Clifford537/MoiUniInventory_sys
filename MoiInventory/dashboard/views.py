from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Transaction, Store
from .forms import ProductForm, TransactionForm, StoreForm
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.http import HttpResponse
import os
import shutil

@login_required
def dashboard_view(request):
    # Retrieve the latest 15 products, sorted by date (latest first)
    products = Product.objects.order_by('-date')[:15]

    # Retrieve the latest 15 transactions, sorted by date and time (latest first)
    transactions = Transaction.objects.order_by('-date', '-time')[:15]

    # Retrieve all stores
    stores = Store.objects.all()

    return render(request, 'dashboard.html', {
        'products': products,
        'transactions': transactions,
        'stores': stores,
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

            if transaction.transaction_type == 'issue':
                if product.quantity >= transaction.quantity:
                    product.quantity -= transaction.quantity
                    product.save()  # Save product after issuing
                    transaction.save()  # Save issued transaction
                    return redirect('dashboard')
                else:
                    available_quantity = product.quantity
                    form.add_error('quantity', f'Issued quantity exceeds available quantity. Available quantity is {available_quantity}.')

            elif transaction.transaction_type == 'receive':
                issued_quantity = Transaction.objects.filter(
                    product=product,
                    transaction_type='issue'
                ).aggregate(
                    issued_quantity=Sum('quantity')
                )['issued_quantity'] or 0

                received_quantity = Transaction.objects.filter(
                    product=product,
                    transaction_type='receive'
                ).aggregate(
                    received_quantity=Sum('quantity')
                )['received_quantity'] or 0

                total_received = received_quantity + transaction.quantity

                if total_received <= issued_quantity:
                    product.quantity += transaction.quantity
                    product.save()  # Save product after receiving
                    transaction.save()  # Save received transaction
                    return redirect('dashboard')
                else:
                    remaining = issued_quantity - received_quantity
                    form.add_error('quantity', f'Received quantity cannot exceed issued quantity. You can only receive up to {remaining} more.')

    else:
        form = TransactionForm()

    return render(request, 'transaction.html', {'form': form})

@login_required
def add_store_view(request):
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_stores')
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

@login_required
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

    transactions = transactions.order_by('-date', '-time')  # Sort by latest date and time

    # Pagination
    paginator = Paginator(transactions, 10)  # Show 10 transactions per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'product_movement.html', {'page_obj': page_obj})


@login_required
def analysis_view(request):
    # Get data from the request, if available
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Build the query based on the date filters
    transactions = Transaction.objects.all()
    if start_date and end_date:
        transactions = transactions.filter(date__range=[start_date, end_date])

    # Calculate totals
    total_products = Product.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_broken_quantity = transactions.aggregate(total=Sum('broken_quantity'))['total'] or 0
    total_good_condition_quantity = total_products - total_broken_quantity

    # Calculate issued and received quantities
    issued_transactions = transactions.filter(transaction_type='issue')
    total_issued_products = issued_transactions.aggregate(total=Sum('quantity'))['total'] or 0

    received_transactions = transactions.filter(transaction_type='receive')
    total_received_products = received_transactions.aggregate(total=Sum('quantity'))['total'] or 0

    total_product_price = Product.objects.aggregate(total_price=Sum('total_price'))['total_price'] or 0

    # Prepare context
    context = {
        'total_products': total_products,
        'total_broken_quantity': total_broken_quantity,
        'total_good_condition_quantity': total_good_condition_quantity,
        'total_issued_products': total_issued_products,
        'total_received_products': total_received_products,
        'total_product_price': total_product_price,
    }

    return render(request, 'analysis.html', context)


@login_required
def backup_database(request):
    db_path = settings.DATABASES['default']['NAME']
    with open(db_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/x-sqlite3')
        response['Content-Disposition'] = 'attachment; filename="backup.sqlite3"'
        return response