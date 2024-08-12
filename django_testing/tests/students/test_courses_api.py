import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from students.models import Course, Student


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(**kwargs):
        return baker.make(Course, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(**kwargs):
        return baker.make(Student, **kwargs)

    return factory


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])
    response = api_client.get(url)

    assert response.status_code == 200
    assert response.data['id'] == course.id
    assert response.data['name'] == course.name


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    courses = course_factory(_quantity=3)
    url = reverse('courses-list')
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == len(courses)


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    courses = course_factory(_quantity=3)
    target_course = courses[0]
    url = reverse('courses-list')
    response = api_client.get(url, data={'id': target_course.id})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['id'] == target_course.id


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    course_factory(name="Python Basics")
    course_factory(name="Django Basics")
    url = reverse('courses-list')
    response = api_client.get(url, data={'name': "Python Basics"})

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == "Python Basics"


@pytest.mark.django_db
def test_create_course(api_client):
    url = reverse('courses-list')
    data = {'name': 'New Course'}
    response = api_client.post(url, data=data)

    assert response.status_code == 201
    assert Course.objects.filter(name='New Course').exists()


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    course = course_factory(name="Old Course Name")
    url = reverse('courses-detail', args=[course.id])
    data = {'name': 'Updated Course Name'}
    response = api_client.put(url, data=data)

    assert response.status_code == 200
    course.refresh_from_db()
    assert course.name == 'Updated Course Name'


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    course = course_factory()
    url = reverse('courses-detail', args=[course.id])
    response = api_client.delete(url)

    assert response.status_code == 204
    assert not Course.objects.filter(id=course.id).exists()
