from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from .models import Project, ProjectPlace
from .serializers import (
    ProjectSerializer,
    ProjectCreateUpdateSerializer,
    ProjectPlaceSerializer,
    ProjectPlaceAddSerializer,
    ProjectPlaceUpdateSerializer
)

# ViewSet for managing Projects / В’юсет для керування проектами
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    # Returns appropriate serializer based on action / Повертає потрібний серіалізатор відповідно до дії
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProjectCreateUpdateSerializer
        return ProjectSerializer

    # Filters projects by completion status / Фільтрує проекти за статусом завершеності
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtering by completed status (e.g. ?completed=true) / Фільтрація за статусом завершеності (?completed=true)
        completed_param = self.request.query_params.get('completed')
        if completed_param is not None:
            if completed_param.lower() == 'true':
                queryset = queryset.filter(completed=True)
            elif completed_param.lower() == 'false':
                queryset = queryset.filter(completed=False)
                
        return queryset

    # Prevents deleting projects with visited places / Запобігає видаленню проектів із відвіданими місцями
    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        
        # A project cannot be deleted if any of its places are already marked as visited / Проект не можна видалити, якщо хоча б одне місце відвідано
        if project.places.filter(visited=True).exists():
            return Response(
                {"detail": "Cannot delete project because some of its places have been visited."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return super().destroy(request, *args, **kwargs)


# ViewSet for managing Places within a Project / В’юсет для керування місцями в межах проекту
class ProjectPlaceViewSet(viewsets.ModelViewSet):
    
    # Returns places filtered by project_id / Повертає місця, відфільтровані за project_id
    def get_queryset(self):
        project_pk = self.kwargs.get('project_pk')
        # Check if project exists to return 404 / Перевірка існування проекту для повернення 404
        get_object_or_404(Project, pk=project_pk)
        return ProjectPlace.objects.filter(project_id=project_pk)

    # Returns appropriate place serializer / Повертає відповідний серіалізатор для місця
    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectPlaceAddSerializer
        elif self.action in ['update', 'partial_update']:
            return ProjectPlaceUpdateSerializer
        return ProjectPlaceSerializer

    # Injects project context into serializer during creation / Передає контекст проекту в серіалізатор при створенні
    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'create':
            project_pk = self.kwargs.get('project_pk')
            project = get_object_or_404(Project, pk=project_pk)
            context['project'] = project
        return context

    # Saves place associated with current project / Зберігає місце, прив'язане до поточного проекту
    def perform_create(self, serializer):
        project_pk = self.kwargs.get('project_pk')
        project = get_object_or_404(Project, pk=project_pk)
        serializer.save(project=project)
