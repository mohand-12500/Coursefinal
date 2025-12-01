# from rest_framework import viewsets, status
# from rest_framework.decorators import action, api_view
# from rest_framework.response import Response
# from .models import Course, StudentCourse
# from .serializers import CourseSerializer, StudentCourseSerializer
# import requests

# # 👉 URL du Student Service (Spring Boot)
# STUDENT_SERVICE_BASE = "http://localhost:8090/api"  # ou 8090 selon ton port Spring Boot


# # ========================
# #     COURSE VIEWSET
# # ========================
# class CourseViewSet(viewsets.ModelViewSet):
#     """
#     CRUD complet pour les cours + actions personnalisées pour la relation étudiant-cours
#     """
#     queryset = Course.objects.all()
#     serializer_class = CourseSerializer

#     # ---- POST /api/courses/{id}/enroll/ ----
#     @action(detail=True, methods=['post'])
#     def enroll(self, request, pk=None):
#         """
#         Inscrire un étudiant à un cours (relation).
#         Body JSON: { "student_id": 123 }
#         Vérifie d'abord que l'étudiant existe dans le service Student (Spring Boot).
#         """
#         course = self.get_object()
#         student_id = request.data.get('student_id')

#         if not student_id:
#             return Response({"error": "student_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         # ✅ Vérifie si l'étudiant existe dans le Student Service
#         try:
#             response = requests.get(f"{STUDENT_SERVICE_BASE}/students/{student_id}", timeout=5)
#             if response.status_code != 200:
#                 return Response({"error": "Student not found in Student Service"}, status=status.HTTP_404_NOT_FOUND)
#         except requests.RequestException as e:
#             return Response({"error": "Cannot reach Student Service", "detail": str(e)},
#                             status=status.HTTP_503_SERVICE_UNAVAILABLE)

#         # ✅ Enregistre l'association dans PostgreSQL
#         enrollment = StudentCourse(student_id=student_id, course=course)
#         enrollment.save()

#         return Response(StudentCourseSerializer(enrollment).data, status=status.HTTP_201_CREATED)

#     # ---- GET /api/courses/{id}/students/ ----
#     @action(detail=True, methods=['get'])
#     def students(self, request, pk=None):
#         """
#         Récupérer la liste des étudiants inscrits à ce cours.
#         """
#         course = self.get_object()
#         enrollments = StudentCourse.objects.filter(course=course)
#         student_ids = [e.student_id for e in enrollments]

#         if not student_ids:
#             return Response([], status=status.HTTP_200_OK)

#         # ✅ Appel au Student Service pour récupérer les détails des étudiants
#         try:
#             response = requests.get(f"{STUDENT_SERVICE_BASE}/students", timeout=5)
#             if response.status_code == 200:
#                 all_students = response.json()
#                 # Filtrer ceux appartenant à ce cours
#                 students = [s for s in all_students if s['id'] in student_ids]
#                 return Response(students, status=status.HTTP_200_OK)
#             else:
#                 return Response({"error": "Cannot fetch students from Student Service"},
#                                 status=status.HTTP_502_BAD_GATEWAY)
#         except requests.RequestException as e:
#             return Response({"error": "Cannot reach Student Service", "detail": str(e)},
#                             status=status.HTTP_503_SERVICE_UNAVAILABLE)


# # ========================
# #  STUDENT-COURSE VIEWSET
# # ========================
# class StudentCourseViewSet(viewsets.ModelViewSet):
#     """
#     CRUD sur les inscriptions (StudentCourse)
#     """
#     queryset = StudentCourse.objects.all()
#     serializer_class = StudentCourseSerializer


# # ========================
# #  API pour cours d’un étudiant
# # ========================
# @api_view(['GET'])
# def get_courses_by_student(request, student_id):
#     """
#     Récupérer tous les cours d’un étudiant spécifique (par ID).
#     Utilisé par le Student Service via HTTP.
#     """
#     enrollments = StudentCourse.objects.filter(student_id=student_id)
#     serializer = StudentCourseSerializer(enrollments, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Course, StudentCourse
from .serializers import CourseSerializer, StudentCourseSerializer
import requests

# 👉 URL du microservice Spring Boot (Student Service)
STUDENT_SERVICE_URL = "http://localhost:8090/student/findStudId/"
  # exemple de microservice student
COURSE_SERVICE_URL = "http://localhost:8090/api/courses/" 

# ====================================================

# 📘 CRUD sur les cours  

# ====================================================

@api_view(['POST'])
def add_course(request):
    """
    ➤ Ajouter un nouveau cours
    """
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_courses(request):
    """
    ➤ Lister tous les cours
    """
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_course_by_id(request, course_id):
    """
    ➤ Récupérer un cours par ID
    """
    try:
        course = Course.objects.get(pk=course_id)
        serializer = CourseSerializer(course)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def update_course(request, course_id):
    """
    ➤ Modifier un cours
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CourseSerializer(course, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_course(request, course_id):
    """
    ➤ Supprimer un cours
    """
    try:
        course = Course.objects.get(pk=course_id)
        course.delete()
        return Response({"message": "Course deleted successfully"}, status=status.HTTP_200_OK)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)


# ====================================================
# 📘 Gestion des inscriptions (relation étudiant-cours)
# ====================================================

@api_view(['POST'])
def enroll_student(request):
    """
    ➤ Inscrire un étudiant dans un cours
    body = { "student_id": 1, "course_id": 2 }
    Vérifie que l'étudiant existe via le microservice Spring Boot.
    """
    student_id = request.data.get("student_id")
    course_id = request.data.get("course_id")

    if not student_id or not course_id:
        return Response({"error": "student_id and course_id are required"}, status=400)

    # Vérifier existence de l’étudiant dans le microservice Student
    try:
        res = requests.get(f"{STUDENT_SERVICE_URL}{student_id}")
        if res.status_code != 200:
            return Response({"error": "Student not found in Student Service"}, status=404)
    except Exception as e:
        return Response({"error": "Student Service not available", "details": str(e)}, status=503)

    # Vérifier que le cours existe
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=404)

    # Vérifier que l’étudiant n’est pas déjà inscrit
    if StudentCourse.objects.filter(student_id=student_id, course=course).exists():
        return Response({"message": "Student already enrolled in this course"}, status=400)

    # Créer l’inscription
    enrollment = StudentCourse.objects.create(student_id=student_id, course=course)
    serializer = StudentCourseSerializer(enrollment)
    return Response(serializer.data, status=201)


# @api_view(['GET'])
# def get_enrollments(request):
#     """
#     ➤ Lister toutes les inscriptions (student_id + course_id)
#     """
#     enrollments = StudentCourse.objects.all()
#     serializer = StudentCourseSerializer(enrollments, many=True)
#     return Response(serializer.data)
@api_view(['GET'])
def get_enrollments(request):
    """
    Lister toutes les inscriptions ou filtrer par course_id (query param).
    GET /enrollments/                  -> all
    GET /enrollments/?course_id=5      -> only course 5
    """
    course_id = request.query_params.get('course_id')
    try:
        qs = StudentCourse.objects.all()
        if course_id:
            try:
                cid = int(course_id)
            except (TypeError, ValueError):
                return Response({"error": "invalid course_id"}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(course__id=cid)

        serializer = StudentCourseSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # En DEV : imprime la stack trace dans la console et renvoie les détails
        import traceback
        traceback.print_exc()
        return Response({"error": "internal server error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_enrollment(request, id):
    """
    Supprime l'enrôlement d'ID donné.
    Méthode: DELETE /enrollments/<id>/
    Réponses:
      - 204 No Content : suppression OK
      - 404 Not Found   : enrollment non trouvé
      - 500             : erreur serveur
    """
    try:
        enrollment = StudentCourse.objects.get(id=id)
    except StudentCourse.DoesNotExist:
        return Response({"error": "Enrollment not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        enrollment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({"error": "Failed to delete enrollment", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ====================================================
# 📘 Recherche avancée de cours
# ====================================================

@api_view(['GET'])
def search_courses(request):
    """
    ➤ Rechercher des cours par nom, instructeur ou catégorie
    Exemple : /api/courses/search/?name=python&instructor=Ali
    """
    name = request.GET.get('name')
    instructor = request.GET.get('instructor')
    category = request.GET.get('category')

    courses = Course.objects.all()

    if name:
        courses = courses.filter(name__icontains=name)
    if instructor:
        courses = courses.filter(instructor__icontains=instructor)
    if category:
        courses = courses.filter(category__icontains=category)

    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

