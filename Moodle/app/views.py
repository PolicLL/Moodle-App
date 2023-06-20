from django.shortcuts import render, get_object_or_404, redirect
from .models import Subject, User
from .forms import SubjectForm, StudentForm, MentorForm, LoginForm, EnrollmentForm, EnrollmentFormStudent
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .authorization import admin_required, student_required, mentor_required, mentor_or_admin_required
from django.contrib.auth import logout
from .models import Mentor, Subject, MentorSubject, Enrollment, Role
from django.contrib import messages
from django.contrib.auth.hashers import make_password


# LOGIN & LOGOUT

def logout_view(request):
    logout(request)
    return redirect('login')

# def areSubjectsInYearPassed(student_id, year, isFullTime):

def user_login(request):
    print(doesHaveSubjectOnLastYear(26))
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == Role.objects.get(name='STUDENT'):  # Redirect to student main page
                    return redirect('student-main')
                elif user.role == Role.objects.get(name='MENTOR'):  # Redirect to mentor main page
                    return redirect('mentor-main')
                elif user.role == Role.objects.get(name='ADMIN'):  # Redirect to admin main page
                    return redirect('admin-main')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})



# STUDENT

def get_student_status(is_full_time_student):
    if is_full_time_student:
        return 'sem_redovni'
    else:
        return 'sem_izvanredni'

def get_subjects_for_student_in_semester(is_full_time_student, semester_number):
    subjects = Subject.objects.all()

    if is_full_time_student: 
        return subjects.filter(sem_redovni=semester_number)

    return subjects.filter(sem_izvanredni=semester_number)

@student_required
def student_main(request):
    tempStudent = request.user
    enrollments = Enrollment.objects.filter(student_id=tempStudent.id)
    subjects = Subject.objects.all()

    is_full_time_student = tempStudent.status == tempStudent.Status.FULL_TIME_STUDENT

    student_status = get_student_status(is_full_time_student)
    
    number_of_semestars = set(subjects.values_list(student_status, flat=True))

    student_subjects_list_of_lists = []

    for temp_semestar in number_of_semestars:

        temp_semestar_subjects = get_subjects_for_student_in_semester(is_full_time_student, temp_semestar)

        tempSemestarList = []
        
        for subject in temp_semestar_subjects:
            enrollment = enrollments.filter(subject=subject).first()
            status = enrollment.status if enrollment else 'NOT_SELECTED'
            subject_data = (subject, status)
            tempSemestarList.append(subject_data)

        student_subjects_list_of_lists.append(tempSemestarList)

    # for element in student_subjects_list_of_lists:
    #     print(str(element) + "\n")

    context = {
        'student_subjects': student_subjects_list_of_lists,
    }

    return render(request, 'student/student/main_student.html', context)

def getSubjectForYear(year, isFullTime):
    if isFullTime == True:
        result = Subject.objects.filter(sem_redovni = year)
    else:
        result = Subject.objects.filter(sem_izvanredni = year)
    return result

def isSubjectPassedForStudent(student_id, subject_id):
    return Enrollment.objects.filter(student_id=student_id, subject_id=subject_id, status = "PASSED").exists()

def areSubjectsInYearPassed(student_id, year, isFullTime):
    allTempSubjects = getSubjectForYear(year, isFullTime)

    for tempSubject in allTempSubjects:
        if isSubjectPassedForStudent(student_id, tempSubject.id) == False:
            return False
    return True

def canUserEnrollInSubjectFromLastYear(student):
    if student.status == User.Status.FULL_TIME_STUDENT:
        return areSubjectsInYearPassed(student.id, 1, True)
    else:
        return areSubjectsInYearPassed(student.id, 1, False) and areSubjectsInYearPassed(student.id, 2, False)

@student_required
def enroll_student(request, subject_id):
    if request.method == 'POST':
        student = request.user
        subject = Subject.objects.get(id=subject_id)

        print(str(student.status == "FULL_TIME_STUDEN") + " " + str(subject.sem_redovni == 3) + " " + str(canUserEnrollInSubjectFromLastYear(student) == False))
        print((student.status))

        if student.status == User.Status.FULL_TIME_STUDENT:
            print("IT IS FULL TIME.")

        # Check if the student is already enrolled in the subject
        if Enrollment.objects.filter(student=student, subject_id=subject_id).exists():
            messages.error(request, 'Student is already enrolled in this subject.')
        elif student.status == User.Status.FULL_TIME_STUDENT and subject.sem_redovni >= 3 and canUserEnrollInSubjectFromLastYear(student) == False:
            messages.error(request, 'Student cannot enroll in this subject.')
        elif student.status == User.Status.PART_TIME_STUDENT and subject.sem_izvanredni >= 4 and canUserEnrollInSubjectFromLastYear(student) == False:
            messages.error(request, 'Student cannot enroll in this subject.')

        else:
            # Create a new enrollment for the student
            Enrollment.objects.create(student=student, subject_id=subject_id, status='ENROLLED')
            messages.success(request, 'Student enrolled successfully.')

    return redirect('student-main')

def doesHaveSubjectOnLastYear(student_id):
    student = get_object_or_404(User, id=student_id)
    allEnrollements = Enrollment.objects.filter(student_id=student_id)

    if student.status == User.Status.FULL_TIME_STUDENT:
        for element in allEnrollements:
            if element.subject.sem_redovni >= 3:
                if element.status == "PASSED" or element.status == "ENROLLED":
                    return True

    if student.status == User.Status.PART_TIME_STUDENT:
        for element in allEnrollements:
            if element.subject.sem_izvanredni >= 4:
                if element.status == "PASSED" or element.status == "ENROLLED":
                    return True

    return False

def getNumberOfStudentsOnLastYear(request):
    students = User.objects.filter(role_id=Role.objects.get(name='STUDENT').id)
    counter = 0
    for stud in students:
        if doesHaveSubjectOnLastYear(stud.id):
            counter += 1

    return render(request, 'student/students_last_year.html', {'counter': counter})

    





@student_required
def remove_enrollment(request, subject_id):
    if request.method == 'POST':
        #subject_id = request.POST.get('subject_id')
        student = request.user

        # Check if the student is enrolled in the subject
        enrollment = Enrollment.objects.filter(student=student, subject_id=subject_id).first()
        if enrollment:
            # Remove the enrollment
            enrollment.delete()
            messages.success(request, 'Student removed from the subject.')
        else:
            messages.error(request, 'Student is not enrolled in this subject.')

    return redirect('student-main')

@admin_required
def student_details(request, student_id):
    student = get_object_or_404(User, id=student_id)
    enrollments = Enrollment.objects.filter(student=student)

    return render(request, 'student/student_details.html', {'student': student, 'enrollments': enrollments})

@admin_required
def studentList(request):
    students = User.objects.filter(role_id=Role.objects.get(name='STUDENT').id)
    return render(request, 'student/student_list.html', {'students': students})

@admin_required
def addStudent(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)  
            student.role = Role.objects.get(name='STUDENT')
            student.save()  

            return redirect('student-list') 
    else:
        form = StudentForm()

    return render(request, 'student/add_student.html', {'form': form})

@admin_required
def editStudent(request, student_id):
    student = User.objects.get(id=student_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']: # is password provided after validation
                user.password = make_password(form.cleaned_data['password']) # hash password
            user.save()
            return redirect('student-list')
    else:
        form = StudentForm(instance=student)

    context = {
        'form': form,
        'student_id': student_id,
    }
    return render(request, 'student/edit_student.html', context)


@admin_required
def deleteStudent(request, student_id):
    student = User.objects.get(id=student_id)

    if request.method == 'POST':
        student.delete()
        return redirect('student-list')

    context = {
        'student_id': student_id,
    }
    return render(request, 'student/delete_student.html', context)

# MENTOR AND STUDENT

@admin_required
def add_mentor_subject(request):
    if request.method == 'POST':
        mentor_id = request.POST.get('mentor_id')
        subject_id = request.POST.get('subject_id')

        mentor = Mentor.objects.get(id=mentor_id)
        subject = Subject.objects.get(id=subject_id)

        if not MentorSubject.objects.filter(mentor=mentor, subject=subject).exists():
            MentorSubject.objects.create(mentor=mentor, subject=subject)

        return redirect('mentor-details', mentor_id=mentor_id) 

    mentors = Mentor.mentor.all()
    subjects = Subject.objects.all()

    return render(request, 'mentor-subject/add_mentor_subject.html', {'mentors': mentors, 'subjects': subjects})

# MENTOR

@mentor_required
def mentor_main(request):
    mentor = request.user
    mentor_subjects = MentorSubject.objects.filter(mentor=mentor)
    subjects = [ms.subject for ms in mentor_subjects]

    return render(request, 'mentor/mentor/main_mentor.html', {'subjects': subjects})


@admin_required
def mentorList(request):
    mentors = User.objects.filter(role_id=Role.objects.get(name='MENTOR').id)
    return render(request, 'mentor/mentor_list.html', {'mentors': mentors})

@admin_required
def addMentor(request):
    if request.method == 'POST':
        form = MentorForm(request.POST)
        if form.is_valid():
            mentor = form.save(commit=False)  # Save the form data without committing to the database
            mentor.role = Role.objects.get(name='MENTOR')  # Set the role field to "MENTOR"
            mentor.save()  # Save the mentor object to the database

            return redirect('mentor-list')  
    else:
        form = MentorForm()
    return render(request, 'mentor/add_mentor.html', {'form': form})

@admin_required
def editMentor(request, mentor_id):
    mentor = User.objects.get(id=mentor_id) 

    if request.method == 'POST':
        form = MentorForm(request.POST, instance=mentor)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.password = make_password(form.cleaned_data['password'])
            user.save()
            return redirect('mentor-list')
    else:
        form = MentorForm(instance=mentor)

    context = {
        'form': form,
        'mentor_id': mentor_id,
    }
    return render(request, 'mentor/edit_mentor.html', context)


@admin_required
def deleteMentor(request, mentor_id):
    mentor = User.objects.get(id=mentor_id)

    if request.method == 'POST':
        mentor.delete()
        return redirect('mentor-list')

    context = {
        'mentor_id': mentor_id,
    }
    return render(request, 'mentor/delete_mentor.html', context)

def get_subjects_by_mentor_id(mentor_id):
    mentor = get_object_or_404(Mentor, pk=mentor_id)
    mentor_subjects = MentorSubject.objects.filter(mentor=mentor)
    subjects = [ms.subject for ms in mentor_subjects]
    return subjects

@admin_required
def mentor_details(request, mentor_id):
    mentor = get_object_or_404(Mentor, id=mentor_id)
    subjects = get_subjects_by_mentor_id(mentor_id)
    all_subjects = Subject.objects.all()
    return render(request, 'mentor/mentor_details.html', 
                  {'mentor': mentor, 'subjects': subjects, 'all_subjects': all_subjects})

@admin_required
def remove_mentor_subject(request, mentor_id, subject_id):
    mentor = get_object_or_404(Mentor, id=mentor_id)
    subject = get_object_or_404(Subject, id=subject_id)

    MentorSubject.objects.filter(mentor=mentor, subject=subject).delete()

    return redirect('mentor-details', mentor_id=mentor_id)

# SUBJECT

@admin_required
def subjectListView(request):
    subjects = Subject.objects.all()
    return render(request, 'subject/subject_list.html', {'subjects': subjects})

@admin_required
def subjectEditView(request, subjectID):
    subject = get_object_or_404(Subject, id=subjectID)
    # check if request is POST and if there is data in request.POST, if no set None
    form = SubjectForm(request.POST or None, instance=subject)

    if form.is_valid():
        form.save()
        return redirect('subject-list')
    
    return render(request, 'subject/edit_subject.html', {'form': form})

@admin_required
def subjectAddView(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('subject-list')
    return render(request, 'subject/add_subject.html', {'form': form})

@admin_required
def deleteSubject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject.delete()
    
    return redirect('subject-list')


@admin_required
def enrolledStudentsView(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    enrollments = Enrollment.objects.filter(subject=subject)

    return render(request, 'subject/enrolled_students.html', {'subject': subject, 'enrollments': enrollments})

@admin_required
def admin_enrollment_update(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        enrolled_students = Enrollment.objects.filter(subject_id=subject_id)
        
        for enrollment in enrolled_students:
            enrollment_status = request.POST.get('status_' + str(enrollment.student_id))
            enrollment_status = enrollment_status.upper()
            enrollment.status = enrollment_status
            enrollment.save()

    return redirect('subject-list')

def subjectListDetail(request):
    subjects = Subject.objects.all()
    passedStudentsCount = Enrollment.objects.filter(status='PASSED', subject__name='Your Subject Name').count()
    passed_full_time_count = User.objects.filter(enrollment__status='PASSED',status=User.Status.FULL_TIME_STUDENT).distinct().count()
    passed_part_time_count = User.objects.filter(enrollment__status='PASSED',status=User.Status.PART_TIME_STUDENT).distinct().count()

    map = {}

    for tempSubject in subjects:
        passed_students_count = Enrollment.objects.filter(status='PASSED', subject__name=tempSubject).count()
        # passed_full_time_count = Enrollment.objects.filter(enrollment__status='PASSED',status=User.Status.FULL_TIME_STUDENT).distinct().count()
        # passed_part_time_count = Enrollment.objects.filter(enrollment__status='PASSED',status=User.Status.PART_TIME_STUDENT).distinct().count()
        map[tempSubject] = passed_students_count

    for element in map:
        print(str(element) + str(map[element]) + "\n")


    return render(request, 'subject/subject_list_detail.html', {'map': map})

# ADMIN

@admin_required
def admin_main(request):
    return render(request, 'administrator/main_admin.html')

# ENROLLEMENT

@admin_required
def add_enrollment(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            # Check if enrollment already exists for the student and subject
            if Enrollment.objects.filter(student=form.cleaned_data['student'], subject=form.cleaned_data['subject']).exists():
                messages.error(request, 'Enrollment already exists for this student and subject.')
                return redirect('enrollment-add')

            form.save()
    else:
        form = EnrollmentForm()

    return render(request, 'enrollment/add_enrollment.html', {'form': form})


@admin_required
def add_enrollment_student(request, student_id):
    student = get_object_or_404(User, id=student_id)

    if request.method == 'POST':
        # Check if enrollment already exists for the student and subject
        if Enrollment.objects.filter(student=student, subject=request.POST['subject']).exists():
            messages.error(request, 'Enrollment already exists for this student and subject.')
            return redirect('student-details', student_id=student_id)

        data = request.POST.copy()
        data['student'] = student_id
        form = EnrollmentFormStudent(data=data)

        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.save()
            return redirect('student-details', student_id=student_id)
    else:
        form = EnrollmentFormStudent(initial={'student': student_id})

    return render(request, 'enrollment/add_enrollment_for_student.html', {'form': form, 'student': student})

@admin_required
def edit_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            return redirect('student-details', student_id=enrollment.student.id)
    else:
        form = EnrollmentForm(instance=enrollment)

    context = {
        'form': form,
        'enrollment_id': enrollment_id,
    }
    return render(request, 'enrollment/edit_enrollment.html', context)

@admin_required
def delete_enrollment(request, enrollment_id):
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        enrollment.delete()
        return redirect('student-details', student_id=enrollment.student.id)

    context = {
        'enrollment_id': enrollment_id,
    }
    return redirect("student-details")

# ENROLLMENT- STUDENTS

@mentor_or_admin_required
def enrolled_students(request, subject_id):
    tempUser = "ADMIN"
    if request.user.role ==  Role.objects.get(name='MENTOR'):
        tempUser = "MENTOR"
    tempSubject = get_object_or_404(Subject, id=subject_id)
    enrollments = Enrollment.objects.filter(subject=tempSubject, status__in=['ENROLLED', 'PASSED', 'DROPPED'])
    return render(request, 'student-subject/enrolled-students.html',
                   {'subject': tempSubject, 'enrollments': enrollments, "temp_user" : tempUser})

@mentor_required
def enrollment_update(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        enrolled_students = Enrollment.objects.filter(subject_id=subject_id)
        
        for enrollment in enrolled_students:
            enrollment_status = request.POST.get('status_' + str(enrollment.student_id))
            enrollment_status = enrollment_status.upper()
            enrollment.status = enrollment_status
            enrollment.save()

    return redirect('mentor-main')


@mentor_required
def all_students(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    enrollments = Enrollment.objects.filter(subject=subject)
    
    enrolled_students = []
    passed_students = []
    dropped_students = []
    
    for enrollment in enrollments:
        student = enrollment.student
        status = enrollment.status
        
        if status == 'ENROLLED':
            enrolled_students.append((student.username, status))
        elif status == 'PASSED':
            passed_students.append((student.username, status))
        elif status == 'DROPPED':
            dropped_students.append((student.username, status))
    
    return render(request, 'mentor/mentor/all_students.html', {
        'subject': subject,
        'enrolled_students': enrolled_students,
        'passed_students': passed_students,
        'dropped_students': dropped_students
    })





