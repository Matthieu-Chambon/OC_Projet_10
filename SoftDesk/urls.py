"""
URL configuration for SoftDesk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import UserViewSet, ProjectViewSet, IssueViewSet, CommentViewSet


router = routers.SimpleRouter()
router.register('user', UserViewSet, basename='user')
router.register('project', ProjectViewSet, basename='project')

projects_router = routers.NestedSimpleRouter(router, r'project', lookup='project')
projects_router.register(r'issue', IssueViewSet, basename='project-issues')

issues_router = routers.NestedSimpleRouter(projects_router, r'issue', lookup='issue')
issues_router.register(r'comment', CommentViewSet, basename='issue-comments')

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='tokent_refresh'),

    path('api/', include(router.urls)),
    path('api/', include(projects_router.urls)),
    path('api/', include(issues_router.urls)),
]
