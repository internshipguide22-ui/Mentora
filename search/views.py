from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course


class CourseSearchView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response(
                {'message': 'Please provide a search query.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        courses = Course.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
            | Q(instructor__username__icontains=query)
        ).select_related('category', 'instructor').order_by('id')

        data = [
            {
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'category': course.category.name if course.category else None,
                'instructor': course.instructor.username,
            }
            for course in courses
        ]
        return Response(data, status=status.HTTP_200_OK)
