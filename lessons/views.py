from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import LessonCompletion
from courses.models import Module, Lesson
from .serializers import LessonSerializer, LessonCompletionSerializer
from courses.views import InstructorRequiredMixin
from .forms import LessonForm

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all().order_by('module__course__id', 'order')
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course_id')
        if course_id:
            queryset = queryset.filter(module__course__id=course_id)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_completed(self, request, pk=None):
        lesson = self.get_object()
        student = request.user
        
        # Check if already completed
        if LessonCompletion.objects.filter(lesson=lesson, student=student).exists():
            return Response({"detail": "Lesson already marked as completed."}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        completion = LessonCompletion.objects.create(lesson=lesson, student=student)
        serializer = LessonCompletionSerializer(completion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class LessonCreateView(InstructorRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_success_url(self):
        # Assuming the URL name is 'course_detail' and it takes a 'pk'
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.module.course.id})

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, pk=self.kwargs['module_pk'], course__pk=self.kwargs['course_pk'])
        if self.module.course.instructor != self.request.user:
            # This was not correctly redirecting.
            return redirect('courses:course_detail', pk=self.kwargs['course_pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Pass the course to the form if needed, but it's not used by the default ModelForm
        kwargs['course'] = self.module.course
        return kwargs

    def form_valid(self, form):
        form.instance.module = self.module
        return super().form_valid(form)

class LessonUpdateView(InstructorRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.module.course.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['course'] = self.get_object().module.course
        return kwargs

    def get_queryset(self):
        return self.model.objects.filter(module__course__instructor=self.request.user)

class LessonDeleteView(InstructorRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lessons/lesson_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'pk': self.object.module.course.id})

    def get_queryset(self):
        return self.model.objects.filter(module__course__instructor=self.request.user)
