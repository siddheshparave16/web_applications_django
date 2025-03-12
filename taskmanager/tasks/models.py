from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F
from datetime import timedelta
from django.utils import timezone



# Model for Epic

class Epic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField( blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)        # Set once, at creation
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name='created_epics', on_delete=models.CASCADE)
    sprints = models.ManyToManyField('Sprint', related_name='epics')  # Fix: String reference for Sprint



# Create your models here.

class VersionMixing:
    version = models.IntegerField(default=0)


class Task( VersionMixing, models.Model):
    STATUS_CHOICES = [
        ('UNASSIGNED', 'Unassigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Completed'),
        ('ARCHIVED', 'Archived')
    ]

    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low')
    ]

    title = models.CharField(max_length=200)
    description = models.TextField( blank=True, null=False, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, 
                              default='UNASSIGNED', db_comment="Can be Assigned, In Progress, Done, or Archived")
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='LOW', db_comment='Can be High, Medium, Low')
    created_at = models.DateTimeField(auto_now_add=True)        # Set once, at creation
    updated_at = models.DateTimeField(auto_now=True)            # Updated every save
    due_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='owned_tasks', on_delete= models.SET_NULL, 
                              null=True, blank=True, db_comment="Foreign key to the User who currently owns the task")
    
    epic = models.ForeignKey(Epic, on_delete=models.SET_NULL, null=True, blank=True)
    
    file_upload = models.FileField(upload_to='tasks/files/', null=True, blank=True)
    image_upload = models.ImageField(upload_to='tasks/images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set `created_at` for the first save if it doesn't exist
        if not self.created_at:
            self.created_at = timezone.now()

        # Set or adjust `due_date` if not provided
        if not self.due_date:
            if self.status == 'DONE':
                # If status is DONE, set due_date to the current date
                self.due_date = timezone.now().date()
            else:
                # For other statuses, set due_date to created_at + 7 days
                self.due_date = (self.created_at + timedelta(days=7)).date()

        # Ensure due_date is strictly greater than or equal to created_at
        if self.due_date <= self.created_at.date():
            self.due_date = (self.created_at + timedelta(days=1)).date()

        super().save(*args, **kwargs)

    class Meta:
        db_table_comment = "Hold Information about tasks"

        constraints = [
            models.CheckConstraint(check= models.Q(status__in=['UNASSIGNED', 'IN_PROGRESS', 'DONE', 'ARCHIVED']), name='check_status'),
            models.CheckConstraint(check= models.Q(due_date__gte= F('created_at')), name='due_date_after_created_date'),
        ]



# Model for Sprint

class Sprint(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField( blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)        # Set once, at creation
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name='created_sprints', on_delete=models.CASCADE)
    tasks = models.ManyToManyField(Task, related_name='sprints', blank=True)


    class Meta:
        constraints = [
            models.CheckConstraint(check= models.Q(end_date__gt=models.F('start_date')), name='end_date_after_start_date'),
        ]


class SubscribedEmail(models.Model):
    email = models.EmailField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='watchers')


# Model for store Unique UUID to prevent duplication.
class Formsubmission(models.Model):
    uuid = models.UUIDField(unique=True)

