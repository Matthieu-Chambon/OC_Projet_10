from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import User, Contributor, Project, Issue, Comment
from api.serializers import (
    UserSerializer,
    ContributorSerializer, ContributorDetailSerializer,
    ProjectSerializer, ProjectDetailSerializer,
    IssueSerializer, IssueDetailSerializer,
    CommentSerializer, CommentDetailSerializer
)


class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class ContributorViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Contributor.objects.all()
    serializer_class = ContributorSerializer
    detail_serializer_class = ContributorDetailSerializer


class ProjectViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer


class IssueViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer
    

class CommentViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    detail_serializer_class = CommentDetailSerializer