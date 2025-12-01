import requests
from rest_framework import serializers


from .models import Course, StudentCourse
STUDENT_SERVICE_URL = "http://localhost:8090/student/findStudId/"
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class StudentCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student = serializers.SerializerMethodField()
    class Meta:
        model = StudentCourse
        fields = '__all__'

    def get_student(self, obj):
        try:
            res = requests.get(f"{STUDENT_SERVICE_URL}{obj.student_id}")
            if res.status_code == 200:
                return res.json()
            return {"error": "Student not found"}
        except Exception as e:
            return {"error": "Student Service unavailable", "details": str(e)}