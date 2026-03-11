from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

from courses.models import Category, Course, Enrollment
from courses.forms import CategoryForm, CourseAdminForm

class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class CategoryListView(AdminRequiredMixin, ListView):
    model = Category
    template_name = 'courses/admin/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(AdminRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'courses/admin/category_form.html'
    success_url = reverse_lazy('courses_admin:category_list')

class CategoryUpdateView(AdminRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'courses/admin/category_form.html'
    success_url = reverse_lazy('courses_admin:category_list')

class CategoryDeleteView(AdminRequiredMixin, DeleteView):
    model = Category
    template_name = 'courses/admin/category_confirm_delete.html'
    success_url = reverse_lazy('courses_admin:category_list')

class CourseAdminListView(AdminRequiredMixin, ListView):
    model = Course
    template_name = 'courses/admin/course_list.html'
    context_object_name = 'courses'

class CourseAdminCreateView(AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseAdminForm
    template_name = 'courses/admin/course_form.html'
    success_url = reverse_lazy('courses_admin:course_list')

class CourseAdminUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseAdminForm
    template_name = 'courses/admin/course_form.html'
    success_url = reverse_lazy('courses_admin:course_list')

class CourseAdminDeleteView(AdminRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/admin/course_confirm_delete.html'
    success_url = reverse_lazy('courses_admin:course_list')


class EnrollmentProgressUpdateView(AdminRequiredMixin, UpdateView):
    model = Enrollment
    fields = ['progress', 'completed', 'completion_date']
    template_name = 'courses/admin/enrollment_progress_form.html'
    context_object_name = 'enrollment'

    def get_success_url(self):
        return reverse_lazy('admin_course_list') # Redirect to course list after update