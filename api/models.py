from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
import uuid


class User(AbstractUser):
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(15)],
    )
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)
    
    REQUIRED_FIELDS = ['age', 'can_be_contacted', 'can_data_be_shared']
    
    def __str__(self):
        return self.username
    

class Project(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
        
    BACKEND = 'BACKEND'
    FRONTEND = 'FRONTEND'
    IOS = 'IOS'
    ANDROID = 'ANDROID'
    
    description_choices = (
        (BACKEND, 'Backend'),
        (FRONTEND, 'Frontend'),
        (IOS, 'iOS'),
        (ANDROID, 'Android'),
    )
    
    description = models.CharField(max_length=30, choices=description_choices)
    created_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Contributor.objects.get_or_create(
            user=self.author,
            project=self
        )


class Issue(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issues')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2048, blank=True)
        
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    
    PRIORITY_CHOICES = (
        (LOW, 'Basse'),
        (MEDIUM, 'Moyenne'),
        (HIGH, 'Haute'),
    )
    
    BUG = 'BUG'
    FEATURE = 'FEATURE'
    TASK = 'TASK'
    
    TYPE_CHOICES = (
        (BUG, 'Bug'),
        (FEATURE, 'Fonctionnalité'),
        (TASK, 'Tâche'),
    )
    
    TODO = 'TODO'
    IN_PROGRESS = 'IN_PROGRESS'
    FINISHED = 'FINISHED'
    
    STATUS_CHOICES = (
        (TODO, 'À faire'),
        (IN_PROGRESS, 'En cours'),
        (FINISHED, 'Fini'),
    )
    
    priority = models.CharField(max_length=30, choices=PRIORITY_CHOICES)
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=TODO)
    
    created_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    description = models.TextField(max_length=2048)
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.title}"
    
    
class Contributor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributed_projects')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='contributors')