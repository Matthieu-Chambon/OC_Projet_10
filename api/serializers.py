from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.reverse import reverse

from .models import User, Project, Issue, Comment


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'age', 'can_be_contacted', 'can_data_be_shared']


class UserSummarySerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'age', 'can_be_contacted', 'can_data_be_shared']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'author', 'title', 'description', 'created_time']
        read_only_fields = ['id', 'author']


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
        users = User.objects.filter(contributions__project=instance)
        serializer = UserSummarySerializer(users, many=True)
        return serializer.data


class IssueSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'author', 'project', 'title', 'description',
                  'priority', 'type', 'status', 'created_time']
        read_only_fields = ['id', 'project']

    # Vérifier si l'auteur de l'issue est un contributeur du projet
    def validate_author(self, value):
        project_pk = self.context['view'].kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_pk)
        if not project.contributors.filter(user=value).exists():
            raise serializers.ValidationError("L'auteur de l'issue doit être un contributeur du projet.")
        return value


class IssueDetailSerializer(ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = ['id', 'author', 'project', 'title', 'description',
                  'priority', 'type', 'status', 'created_time', 'comments']

    def get_comments(self, instance):
        queryset = instance.comments.all()
        serializer = CommentSerializer(queryset, many=True)
        return serializer.data


class CommentSerializer(ModelSerializer):
    issue_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['uuid', 'author', 'issue', 'description', 'issue_url', 'created_time']
        read_only_fields = ['uuid', 'author', 'issue']

    def get_issue_url(self, instance):
        return reverse(
            'project-issues-detail',
            kwargs={
                'project_pk': instance.issue.project.id,
                'pk': instance.issue.id},
        )
