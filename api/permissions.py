from rest_framework.permissions import BasePermission
from django.shortcuts import get_object_or_404
from api.models import Project


class UserPermission(BasePermission):
    """
    Un utilisateur non authentifié peut créer un compte (POST)
    Un utilisateur authentifié peut lister les utilisateurs
    Un utilisateur ne peut consulter / modifier / supprimer que son propre profil
    """
    def has_permission(self, request, view):
        # Autorise tout le monde à la méthode OPTIONS
        if request.method == 'OPTIONS':
            return True

        # Autorise un user à crer un compte s'il n'est pas authentifié
        if request.method == 'POST':
            return not request.user.is_authenticated

        # Autorise les utilisateurs authentifiés à lister les utilisateurs
        if request.method in ('GET', 'HEAD'):
            return request.user.is_authenticated

        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            # Autorise l'utilisateur à lire, modifier ou supprimer son propre profil
            if obj == request.user:
                return True

        return False


class ProjectPermission(BasePermission):
    """
    L'auteur du projet peut modifier ou supprimer le projet
    L'auteur du projet peut ajouter ou retirer des contributeurs
    Un contributeur peut lire le projet
    Les autres utilisateurs peuvent seulement lister les projets
    """
    def has_object_permission(self, request, view, obj):
        # Autorise tout le monde à la méthode OPTIONS
        if request.method == 'OPTIONS':
            return True

        # Autorise les méthodes de lectures uniquement si l'user est un contributeur
        if request.method in ('GET', 'HEAD'):
            if obj.contributors.filter(user=request.user).exists():
                return True

        # Autorise l'auteur à tout faire
        return obj.author == request.user


class IssueAndCommentPermission(BasePermission):
    """
    L'auteur et les contributeurs d'un projet peuvent créer ou lister des issues/comments
    L'auteur d'une issue/comment peut la modifier ou la supprimer
    Les autres utilisateurs peuvent uniquement consulter les options
    """
    def has_permission(self, request, view):
        project_pk = view.kwargs.get('project_pk')

        if not project_pk:
            return False

        project = get_object_or_404(Project, pk=project_pk)

        # Autorise tout le monde à la méthode OPTIONS
        if request.method == 'OPTIONS':
            return True

        # Autorise les contributeurs et l'auteur du projet à créer ou lister les issues/comments
        if request.method in ('GET', 'HEAD', 'POST'):
            return (
                project.contributors.filter(user=request.user).exists()
                or project.author == request.user
            )

        return True

    def has_object_permission(self, request, view, obj):
        project_pk = view.kwargs.get('project_pk')

        if not project_pk:
            return False

        project = get_object_or_404(Project, pk=project_pk)

        # Authorise l'auteur ou les contributeurs du projet à lire le détail de l'issue/comment
        if request.method in ('GET', 'HEAD'):
            return (
                project.contributors.filter(user=request.user).exists() or
                project.author == request.user
            )

        # Autorise l'auteur à modifier ou supprimer
        if request.method in ('PUT', 'PATCH', 'DELETE'):
            return obj.author == request.user

        return True
