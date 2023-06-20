from django.db import models
from django.contrib.auth.models import AbstractUser # used for overriding user table
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password
# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Check if the object is being created for the first time
        if not self.pk:
            # Create the initial roles
            roles = ['ADMIN', 'STUDENT', 'MENTOR']
            for role in roles:
                Role.objects.create(name=role)

        super().save(*args, **kwargs)


class User(AbstractUser):
    class Status(models.TextChoices):
        NONE = "NONE", 'None'
        FULL_TIME_STUDENT = "FULL_TIME_STUDENT", 'Full Time Student'
        PART_TIME_STUDENT = "PART_TIME_STUDENT", 'Part Time Student'

    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=Status.choices)
    
    def save(self, *args, **kwargs):
        if not self.pk:
            if not self.role_id:  # Check if the role is not already set
                self.role = Role.objects.get(name='ADMIN')
            if not self.is_superuser:
                self.password = make_password(self.password)
        return super().save(*args, **kwargs)


    
    def __str__(self):
        return f"User: {self.username}, Role: {str(self.role)}, Status: {self.get_status_display()}"


# STUDENT

class Student(User):

    class Meta: # this class Meta and proxy attribute are important to write, so that Django knows that it should not create new tables in database, yet
        proxy = True # these classes (Student, Teacher) are just extending User class

    def welcome(self):
        return "Only for students"
    
    def __str__(self):
        user_str = super().__str__()  # Call the __str__ method of the User superclass
        return f"{user_str}, Additional Info: Student"

class Mentor(User):

    class Meta:
        proxy = True # do not create new table in the database

    def welcome(self):
        return "Only for mentors"


class Subject(models.Model):
    IZBORNI_CHOICES = (('da', 'Da'), ('ne', 'Ne'), )

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    program = models.TextField()
    ects_points = models.IntegerField()
    sem_redovni = models.IntegerField()
    sem_izvanredni = models.IntegerField()
    izborni = models.CharField(max_length=2, choices=IZBORNI_CHOICES)

    def __str__(self):
        return self.name

class MentorSubject(models.Model):
    mentor = models.ForeignKey(Mentor, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

class Enrollment(models.Model):
    STATUS_CHOICES = (('ENROLLED', 'Enrolled'), ('PASSED', 'Passed'), ('DROPPED', 'Dropped'))

    student = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Enrollment: Student {self.student.username}, Subject {self.subject.name}, Status {self.get_status_display()}"

