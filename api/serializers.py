from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Project, Issue, Comment


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'author', 'contributors', 'title', 'description', 'created_time']
        

class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'author', 'project', 'title', 'description', 'priority', 'type', 'status', 'created_time']
        

class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'issue', 'description', 'created_time']