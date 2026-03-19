from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from courses.models import Course, Category

class CourseSearchAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.category1 = Category.objects.create(name='Programming')
        self.category2 = Category.objects.create(name='Design')
        self.course1 = Course.objects.create(
            title='Python Basics',
            description='Learn Python from scratch',
            instructor=self.user,
            category=self.category1
        )
        self.course2 = Course.objects.create(
            title='Web Design Fundamentals',
            description='Introduction to web design',
            instructor=self.user,
            category=self.category2
        )
        self.course3 = Course.objects.create(
            title='Advanced Python',
            description='Deep dive into Python programming',
            instructor=self.user,
            category=self.category1
        )
        self.url = reverse('course_search')

    def test_search_by_title(self):
        response = self.client.get(self.url, {'q': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Python Basics')
        self.assertEqual(response.data[1]['title'], 'Advanced Python')

    def test_search_by_description(self):
        response = self.client.get(self.url, {'q': 'scratch'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Python Basics')

    def test_search_by_category(self):
        response = self.client.get(self.url, {'q': 'Design'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Web Design Fundamentals')

    def test_no_query_returns_bad_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], 'Please provide a search query.')

    def test_no_results_found(self):
        response = self.client.get(self.url, {'q': 'NonExistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
