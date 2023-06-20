from django.urls import path
from .import views

urlpatterns = [

    path('logout/', views.logout_view, name='logout'),
    path('login/', views.user_login, name='login'),

    path('administrator/main', views.admin_main, name='admin-main'),

    path('subjects/', views.subjectListView, name='subject-list'),
    path('subjects/edit/<int:subjectID>/', views.subjectEditView, name='edit-subject'),
    path('subjects/add/', views.subjectAddView, name='add-subject'),
    path('subject/delete/<int:subject_id>/', views.deleteSubject, name='delete-subject'),
    path('subject/<int:subject_id>/enrolled-students/', views.enrolledStudentsView, name='enrolled-students-subjects'),
    path('subject/enrollment-update/', views.admin_enrollment_update, name='admin-enrollment-update'),
    path('subject/list-detail', views.subjectListDetail, name='list-detail'),

    path('student/main', views.student_main, name='student-main'),
    path('student/last-year', views.getNumberOfStudentsOnLastYear, name='students-last-year'),
    path('student/<int:student_id>/', views.student_details, name='student-details'),
    path('student/enroll/<int:subject_id>/', views.enroll_student, name='enroll_student'),
    path('student/remove/<int:subject_id>/', views.remove_enrollment, name='remove_enrollment'),

    path('students/', views.studentList, name='student-list'),
    path('students/add/', views.addStudent, name='add-student'),
    path('students/edit/<int:student_id>/', views.editStudent, name='edit-student'),
    path('students/delete/<int:student_id>/', views.deleteStudent, name='delete-student'),
    
    path('mentor/main', views.mentor_main, name='mentor-main'),
    path('mentor/<int:mentor_id>/', views.mentor_details, name='mentor-details'),
    path('mentors/', views.mentorList, name='mentor-list'),
    path('mentors/add/', views.addMentor, name='add-mentor'),
    path('mentors/edit/<int:mentor_id>/', views.editMentor, name='edit-mentor'),
    path('mentors/delete/<int:mentor_id>/', views.deleteMentor, name='delete-mentor'),
    path('mentors/add-subject', views.add_mentor_subject, name='add-mentor-subject'),
    path('mentor/<int:mentor_id>/subject/<int:subject_id>/remove/', views.remove_mentor_subject, name='remove-mentor-subject'),


    path('enrollment/add-student/<int:student_id>/', views.add_enrollment_student, name='add-enrollment-student'),
    path('enrollment/add/', views.add_enrollment, name='add-enrollment'),
    path('enrollment/edit/<int:enrollment_id>/', views.edit_enrollment, name='edit-enrollment'),
    path('enrollment/delete/<int:enrollment_id>/', views.delete_enrollment, name='delete-enrollment'),

    path('enrolled-students/<int:subject_id>/', views.enrolled_students, name='enrolled-students'),
    path('enrolled-students/<int:subject_id>/all/', views.all_students, name='all-students'),
    path('enrollment-update/', views.enrollment_update, name='enrollment-update'),
]


