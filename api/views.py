from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .models import User, Project, Issue, Comment
from api.serializers import (
    UserSerializer, UserSummarySerializer, UserCreateSerializer,
    ProjectSerializer, ProjectDetailSerializer,
    IssueSerializer, IssueDetailSerializer,
    CommentSerializer,
)

from rest_framework.permissions import IsAuthenticated
from api.permissions import ProjectPermission, UserPermission, IssueAndCommentPermission


class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action in ['retrieve'] and self.detail_serializer_class is not None:
            return self.detail_serializer_class

        return super().get_serializer_class()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSummarySerializer
    detail_serializer_class = UserSerializer
    permission_classes = [UserPermission]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return self.detail_serializer_class
        if self.action == 'create':
            return UserCreateSerializer
        return super().get_serializer_class()


class ProjectViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    detail_serializer_class = ProjectDetailSerializer
    permission_classes = [IsAuthenticated, ProjectPermission]

    def perform_create(self, serializer):
        author = self.request.user
        serializer.save(author=author)

    @action(detail=True, methods=['post'])
    def add_contributor(self, request, pk):
        user = get_object_or_404(User, id=request.data.get('user'))
        response = self.get_object().add_contributor(user)
        if response:
            return Response({'status': 'Utilisateur ajouté en contributeur'}, status=201)
        return Response({'status': 'Utilisateur déjà contributeur'}, status=400)

    @action(detail=True, methods=['post'])
    def remove_contributor(self, request, pk):
        user = get_object_or_404(User, id=request.data.get('user'))
        response = self.get_object().remove_contributor(user)
        if response:
            return Response({'status': 'Utilisateur retiré des contributeurs'}, status=200)
        return Response({'status': 'Utilisateur n\'est pas contributeur'}, status=400)


class IssueViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    detail_serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IssueAndCommentPermission]

    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        return self.queryset.filter(project__id=project_pk)

    def perform_create(self, serializer):
        project = get_object_or_404(Project, id=self.kwargs.get('project_pk'))
        serializer.save(project=project)


class CommentViewSet(MultipleSerializerMixin, ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IssueAndCommentPermission]

    def perform_create(self, serializer):
        issue = get_object_or_404(Issue, id=self.kwargs.get('issue_pk'))
        author = self.request.user
        serializer.save(issue=issue, author=author)
