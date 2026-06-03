from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProjectPlaceViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

# Custom routing for nested places
project_places_list = ProjectPlaceViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
project_places_detail = ProjectPlaceViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', include(router.urls)),
    path('projects/<int:project_pk>/places/', project_places_list, name='project-places-list'),
    path('projects/<int:project_pk>/places/<int:pk>/', project_places_detail, name='project-places-detail'),
]
