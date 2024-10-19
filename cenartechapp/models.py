from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        """
        Creates and saves a regular user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The Username field is required')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given username, email, and password.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        school_name = input("Enter the school name: ")
        school, created = School.objects.get_or_create(name=school_name)

        # Create a default Term associated with the school
        Term.objects.get_or_create(term="One", school=school)

        # Assign the school to the superuser
        extra_fields['school'] = school

        return self.create_user(username, email, password, **extra_fields)







class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    number = models.CharField(max_length=100, null=True, blank=True)
    slogan = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to="schools_logo", default="blank.webp")
    def __str__(self):
        return f"{self.name} at {self.address}"
        

class CustomUser(AbstractUser):
    USER_CHOICE = (
        ('HOD', 'HOD'),
        ('STAFF', 'STAFF'),
        ('STUDENT', 'STUDENT'),
    )
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    user_type = models.CharField(choices=USER_CHOICE, max_length=50, default="HOD")
    profile_pic = models.ImageField(upload_to="profile_pic", default="blank.webp")
    middle_name = models.CharField(max_length=200, blank=True)
    
    objects = CustomUserManager()



    

class Staff(models.Model):
    staff_name = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address = models.TextField()
    qualification = models.TextField()
    experience = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    stafftype = models.CharField(max_length=100)
    class_managed = models.ManyToManyField("Class_Form", related_name='staff_managers')
    subject_teacher_subject = models.ManyToManyField("Subject", related_name='subject_teacher')
    subject_teacher_class = models.ManyToManyField("Class_Form", related_name='class_for_subject')
    religion = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Staff {self.staff_name.get_full_name()} from {self.address}"


    
class Class_Form(models.Model):
    name = models.CharField(max_length=100)
    managed_by = models.ForeignKey(Staff, null=True , blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


    
    

class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    class_Form = models.ForeignKey(Class_Form, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    managed_by = models.ForeignKey(Staff, null=True , blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.class_Form} sub {self.subject_name}"
    


    

class Student(models.Model):
    NURSERY = ['Nursery One', "Nursery Two"]
    KINDERGARTEN = ['Kindergarten One', "Kindergarten Two"]
    FORMS = ["Form One", "Form Two", "Form Three"]
    LOWER_CLASSES = ["Class One", "Class Two", "Class Three", "Class Four", "Class Five", "Class Six"]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address1 = models.TextField()
    address2 = models.TextField()
    dob = models.CharField(max_length=100)
    religion = models.CharField(max_length=100)
    phone = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    father_name = models.CharField(max_length=100, blank=True)
    father_number = models.CharField(max_length=100, blank=True)
    father_email = models.CharField(max_length=100, blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    mother_email = models.CharField(max_length=100, blank=True)
    mother_number = models.CharField(max_length=100, blank=True)
    class_id = models.ForeignKey(Class_Form, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subjects = models.ManyToManyField(Subject, blank=True)
    interest = models.CharField(max_length=255, blank=True)
    conduct = models.TextField(default="Very Good")
    remarks = models.TextField(default="Very Good")
    year_completed = models.CharField(max_length=100, blank=True)
    year_stopped = models.CharField(max_length=100, blank=True)
    term_stopped = models.CharField(max_length=100, blank=True)
    attendance = models.CharField(max_length=100)
    promoted_to = models.ForeignKey(Class_Form, on_delete=models.DO_NOTHING, null=True, related_name="moved")


    
    
    
    
    # New fields for storing total marks per term
    total_marks_term_one = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    total_marks_term_two = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    total_marks_term_three = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    overall_total_marks = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    
    
    
    

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s details"

    def assign_subjects(self):
        # Determine which subjects to add based on the student's class/form
        if self.class_id.name in self.LOWER_CLASSES:
            subjects_to_add = ["English", "Our World Our People", "Creative Arts", "Mathematics", "Integrated Science", "History", "Asante Twi", "French", "Religious & Moral Education", "Computing"]
            
            
        elif self.class_id.name in self.FORMS:
            subjects_to_add = ["English", "Social", "Creative Arts", "Mathematics", "Integrated Science", "Career Technology", "Asante Twi", "French", "Religious & Moral Education", "Computing"]
            
            
        elif self.class_id.name in self.NURSERY:
            subjects_to_add = ["Language & Literacy", "Numeracy", "Environmental Studies", "Creative Arts", "Physical Development", "Personal, Social, & Emotional Development", "Religious & Moral Education"]
            
            
        elif self.class_id.name in self.KINDERGARTEN:
            subjects_to_add = ["Language & Literacy", "Numeracy", "Environmental Studies", "Creative Arts", "Physical Development", "Personal, Social, & Emotional Development", "Religious & Moral Education", "Information & Communication Technology (ICT)"]
        else:
            subjects_to_add = []

        for subject_name in subjects_to_add:
            subject, created = Subject.objects.get_or_create(subject_name=subject_name, class_Form=self.class_id)
            self.subjects.add(subject)
        self.save()


class PassedStudents(models.Model):
    class_form = models.CharField(max_length=30)
    term = models.CharField(max_length=30)
    year = models.CharField(max_length=30)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Passed Students {self.class_form} in {self.term} {self.year}"
    
  
  
class YearlyPassedStudents(models.Model):
    year = models.CharField(max_length=30)
    number = models.IntegerField(default=0)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    
    
    def __str__(self):
        return f"Yearly Passed Students {self.number} in {self.year}"



class AdmittedStudents(models.Model):
    class_form = models.CharField(max_length=30)
    term = models.CharField(max_length=30)
    year = models.CharField(max_length=30)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    
    
    def __str__(self):
        return f"Admitted Students {self.class_form} in {self.term} {self.year}"
    
  
  
class YearlyAdmittedStudents(models.Model):
    year = models.CharField(max_length=30)
    number = models.IntegerField(default=0)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    
    
    def __str__(self):
        return f"Yearly Adimitted Students {self.number} in {self.year}"




class Term(models.Model):
    term = models.CharField(max_length=30, default="One")
    hod_remarks = models.TextField(default="Very Good")
    cutOfPoint = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    vacation_date = models.CharField(max_length=30, blank=True)
    reopening_date = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    
    
    def __str__(self):
        return f"Term {self.term}"




class StudentResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='sresults')
    subject = models.CharField(max_length=100)
    exercise_score = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    homework_score = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    project_work_score = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    exam_score = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_score = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, editable=False)
    grade = models.CharField(max_length=2, blank=True)
    profi = models.CharField(max_length=2, blank=True)
    term = models.CharField(max_length=10)
    previous_class = models.CharField(max_length=50)
    year = models.CharField(max_length=10)
    sum_class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    total_class_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    exams_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        # Ensure valid Decimal values
        self.exercise_score = Decimal(self.exercise_score or 0)
        self.homework_score = Decimal(self.homework_score or 0)
        self.project_work_score = Decimal(self.project_work_score or 0)
        self.exam_score = Decimal(self.exam_score or 0)
        
        
        s_class_score = self.exercise_score + self.homework_score + self.project_work_score
        self.sum_class_score = s_class_score
        
        # Calculate the class score as 30% of the combined scores
        class_score = (s_class_score / Decimal(100)) * Decimal(30)
        # Store the calculated class score
        self.total_class_score = class_score.quantize(Decimal('1'), rounding=ROUND_HALF_UP).quantize(Decimal('0.00'))
        
        # Calculate the exam score as 70% of the exam score
        exam_score = (self.exam_score / Decimal(100) * Decimal(70))
        self.exams_score = exam_score.quantize(Decimal('1'), rounding=ROUND_HALF_UP).quantize(Decimal('0.00'))
        
        # Calculate the total score
        total_score = class_score + exam_score
        self.total_score = total_score.quantize(Decimal('1'), rounding=ROUND_HALF_UP).quantize(Decimal('0.00'))
        
        # Determine and assign the grade based on the total score
        if self.total_score >= 80:
            self.profi = 'A'
            self.grade = '1'
        elif 70 <= self.total_score < 80:
            self.profi = 'P'
            self.grade = '2'
        elif 60 <= self.total_score < 70:
            self.profi = 'AP'
            self.grade = '3'
        elif 50 <= self.total_score < 60:
            self.profi = 'D'
            self.grade = '4'
        else:
            self.profi = 'B'
            self.grade = '5'
            
            
        # Call the parent save method to persist the changes to the current result
        super(StudentResult, self).save(*args, **kwargs)

        # Recalculate the total marks for the current term for this student
        total_marks = StudentResult.objects.filter(student=self.student, term=self.term, year=self.year).aggregate(Sum('total_score'))['total_score__sum'] or 0
        
       # Clear previous total marks and update with the new total
        student = self.student
        if self.term == "One":
            student.total_marks_term_one = total_marks
        elif self.term == "Two":
            student.total_marks_term_two = total_marks
        elif self.term == "Three":
            student.total_marks_term_three = total_marks
        
        # Make sure None values are treated as 0 before summing the overall total marks
        student.total_marks_term_one = student.total_marks_term_one or 0
        student.total_marks_term_two = student.total_marks_term_two or 0
        student.total_marks_term_three = student.total_marks_term_three or 0
        
        # Calculate overall total marks
        student.overall_total_marks = student.total_marks_term_one + student.total_marks_term_two + student.total_marks_term_three
        student.save()

        # Update the student's interest based on top subjects
        self.update_student_interest()
    
    


    def update_student_interest(self):
        # Get all results for the student
        all_results = StudentResult.objects.filter(student=self.student).order_by('-total_score')

        # Select top 2 subjects
        top_results = all_results[:2]

        # In case of ties, ensure only unique subjects are selected
        unique_subjects = list({result.subject for result in top_results})

        # Update student's interest field
        if len(unique_subjects) > 1:
            interest = f"{unique_subjects[0]} and {unique_subjects[1]}"
        elif unique_subjects:
            interest = unique_subjects[0]
        else:
            interest = None

        # Save the interest to the student's profile
        self.student.interest = interest
        self.student.save()

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject} - {self.total_score} ({self.grade})"
    
    



class StudentClasses(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classes = models.ManyToManyField(Class_Form)
    year = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()}'s Repeated Classes"
