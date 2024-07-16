from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Transaction, Store
from .forms import ProductForm, TransactionForm, StoreForm
from django.db.models import Q

@login_required
def dashboard_view(request):
    products = Product.objects.all()
    transactions = Transaction.objects.all()
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
        ).distinct()  # Adjust to include other searchable fields
    
    if store_id:
        products = products.filter(store_id=store_id)
    
    if date_added:
        products = products.filter(date=date_added)
    
    stores = Store.objects.all()
    context = {
        'products': products,
        'stores': stores,
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