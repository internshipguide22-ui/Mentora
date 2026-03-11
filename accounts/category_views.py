from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required
from courses.models import Category

@login_required
@admin_required
def manage_categories(request):
    categories = Category.objects.all()
    return render(request, 'management/categories.html', {'categories': categories})

@login_required
@admin_required
def create_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        Category.objects.create(name=name, description=description)
        messages.success(request, 'Category created successfully!')
        return redirect('manage_categories')
    return render(request, 'management/create_category.html')

@login_required
@admin_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('manage_categories')
    return render(request, 'management/edit_category.html', {'category': category})

@login_required
@admin_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('manage_categories')
    return render(request, 'management/delete_category.html', {'category': category})
