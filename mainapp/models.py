from django.db import models
from django.utils import timezone
from django.conf import settings

class Student(models.Model):
    student_name = models.CharField(max_length=20, unique=True)
    Enrollment = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student_name

# models.py
class Event(models.Model):
    CATEGORY_CHOICES = [
        ('TECH', 'Tech Events'),
        ('CULTURAL', 'Cultural Events'),
        ('SEMINAR', 'Seminars'),
        ('WORKSHOP', 'Workshops'),
        ('LECTURE', 'Guest Lectures'),
        ('HACKATHON', 'Hackathons'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/', blank=True, null=True)    
    is_completed = models.BooleanField(default=False)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='TECH'
    )

    def __str__(self):
        return self.title

class Participation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participation_date = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    is_registered = models.BooleanField(default=True)  # New field for registration status
    
    class Meta:
        unique_together = ('student', 'event')

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    target = models.CharField(max_length=20, default='all')

    def __str__(self):
        return self.title
    

