from django.urls import path
from . import views

urlpatterns = [
    # Cours
    path('courses/', views.get_all_courses),
    path('courses/add/', views.add_course),
    path('courses/<int:course_id>/', views.get_course_by_id),
    path('courses/update/<int:course_id>/', views.update_course),
    path('courses/delete/<int:course_id>/', views.delete_course),
    path('courses/search/', views.search_courses),

    # Inscriptions
        path('enrollments/', views.get_enrollments),
        path('enrollments/enroll/', views.enroll_student),
        path('enrollments/<int:id>/', views.delete_enrollment),
    ]
