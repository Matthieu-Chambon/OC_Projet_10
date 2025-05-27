from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import User, Contributor, Project, Issue, Comment


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'age', 'can_be_contacted', 'can_data_be_shared']
        

class UserSummarySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        

class ContributorSerializer(ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project']
        

class ContributorDetailSerializer(ModelSerializer):
    user = UserSummarySerializer()
    project = serializers.SerializerMethodField()
    
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project']
        
    def get_project(self, instance):
        project = instance.project
        serializer = ProjectSerializer(project)
        return serializer.data


class ProjectSerializer(ModelSerializer):
    contributors = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'author', 'contributors', 'title', 'description', 'created_time']
        
    def get_contributors(self, instance):
        contributor_ids = list(
            instance.contributors.values_list('user__id', flat=True)
        )
        return contributor_ids


class ProjectDetailSerializer(ModelSerializer):
    issues = serializers.SerializerMethodField()
    contributors = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'author', 'contributors', 'title', 'description', 'created_time', 'issues']
        
    def get_issues(self, instance):
        queryset = instance.issues.all()
        serializer = IssueSerializer(queryset, many=True)
        return serializer.data

    def get_contributors(self, instance):
        users = User.objects.filter(contributed_projects__project=instance)
        serializer = UserSummarySerializer(users, many=True)
        return serializer.data


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'author', 'project', 'title', 'description', 'priority', 'type', 'status', 'created_time']


class IssueDetailSerializer(ModelSerializer):
    author = UserSummarySerializer()
    project = ProjectSerializer()
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = ['id', 'author', 'project', 'title', 'description', 'priority', 'type', 'status', 'created_time', 'comments']

    def get_comments(self, instance):
        queryset = instance.comments.all()
        serializer = CommentSerializer(queryset, many=True)
        return serializer.data
        

class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'issue', 'description', 'created_time']
        

class CommentDetailSerializer(ModelSerializer):
    author = UserSummarySerializer()
    issue = IssueSerializer()
    
    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'issue', 'description', 'created_time']