from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from tasks.enums import TaskStatus


# Model for Epic


class Epic(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Set once, at creation
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="created_epics", on_delete=models.CASCADE,
    )
    tasks = models.ManyToManyField("Task",related_name="epics", blank=True)
    # sprints = models.ManyToManyField(
    #     "Sprint", related_name="epics"
    # )  # Fix: String reference for Sprint


# Create your models here.


class VersionMixing:
    version = models.IntegerField(default=0)


class Task(VersionMixing, models.Model):
    # Before API we use this for Task Status choice
    """
    STATUS_CHOICES = [
        ("UNASSIGNED", "Unassigned"),
        ("IN_PROGRESS", "In Progress"),
        ("DONE", "Completed"),
        ("ARCHIVED", "Archived"),
    ]
    """

    """
    STATUS_CHOICES is used for the status field in the Task model.

    - The first element (status.value) is stored in the database as the canonical value 
    (e.g., "UNASSIGNED"). This ensures a consistent programmatic representation.
    
    - The second element (status.name.replace("_", " ").title()) is a human-readable label 
    (e.g., "Unassigned") displayed in forms and the admin interface. This improves 
    user experience while keeping the stored values clean and standardized.

    By generating STATUS_CHOICES dynamically from the TaskStatus Enum, we ensure consistency 
    and make it easier to add or modify statuses in the future.
    """

    STATUS_CHOICES = [
        (status.value, status.name.replace("_", " ").title()) for status in TaskStatus
    ]

    PRIORITY_CHOICES = [("HIGH", "High"), ("MEDIUM", "Medium"), ("LOW", "Low")]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=False, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=TaskStatus.UNASSIGNED.value,
        db_comment="Can be Assigned, In Progress, Done, or Archived",
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="LOW",
        db_comment="Can be High, Medium, Low",
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Set once, at creation
    updated_at = models.DateTimeField(auto_now=True)  # Updated every save
    due_date = models.DateField(null=True, blank=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_tasks",
        on_delete=models.PROTECT,   # Protect user deletion
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_tasks",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_comment="Foreign key to the User who currently owns the task",
    )

    epic = models.ForeignKey(Epic, on_delete=models.SET_NULL, null=True, blank=True)

    file_upload = models.FileField(upload_to="tasks/files/", null=True, blank=True)
    image_upload = models.ImageField(upload_to="tasks/images/", null=True, blank=True)

    def save(self, *args, **kwargs):
        # Set `created_at` for the first save if it doesn't exist
        if not self.created_at:
            self.created_at = timezone.now()

        # Set or adjust `due_date` if not provided
        if not self.due_date:
            if self.status == "DONE":
                # If status is DONE, set due_date to the current date
                self.due_date = timezone.now().date()
            else:
                # For other statuses, set due_date to created_at + 7 days
                self.due_date = (self.created_at + timedelta(days=7)).date()

        # Ensure due_date is strictly greater than or equal to created_at
        if self.due_date <= self.created_at.date():
            self.due_date = (self.created_at + timedelta(days=1)).date()

        if self.owner and self.status == "UNASSIGNED":
            self.status = "IN_PROGRESS"

        super().save(*args, **kwargs)

    class Meta:
        db_table_comment = "Hold Information about tasks"

        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    status__in=["UNASSIGNED", "IN_PROGRESS", "DONE", "ARCHIVED"]
                ),
                name="check_status",
            ),
            models.CheckConstraint(
                check=models.Q(due_date__gte=F("created_at")),
                name="due_date_after_created_date",
            ),
        ]

        permissions = [
            ("custom_task", "Custom Task Permission"),
        ]


# Model for Sprint


class Sprint(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)  # Set once, at creation
    updated_at = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_sprints",
        on_delete=models.PROTECT,
    )
    tasks = models.ManyToManyField(Task, related_name="sprints", blank=True)
    epic = models.ForeignKey(Epic, related_name="sprints", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F("start_date")),
                name="end_date_after_start_date",
            ),
        ]


class SubscribedEmail(models.Model):
    email = models.EmailField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="watchers")


# Model for store Unique UUID to prevent duplication.
class Formsubmission(models.Model):
    uuid = models.UUIDField(unique=True)


class Comment(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, related_name="comments_authored")
    comment = models.TextField(max_length=500)
    created_at = models.DateField(auto_now_add=True)
    reply = models.ForeignKey("Comment", on_delete=models.CASCADE, related_name="replies",blank=True, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        return f'{self.comment} - {self.author}'

    
    class Meta:
        ordering = ['-created_at']      # latest comment will be display first
