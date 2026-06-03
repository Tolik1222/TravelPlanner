from rest_framework import serializers
from .models import Project, ProjectPlace
from .services import ArtInstituteService

# Serializer for viewing project places / Серіалізатор для перегляду місць проекту
class ProjectPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlace
        fields = ['id', 'external_id', 'title', 'notes', 'visited']
        read_only_fields = ['id', 'title']


# Serializer for nested place creation / Серіалізатор для створення вкладених місць
class NestedPlaceCreateSerializer(serializers.Serializer):
    external_id = serializers.CharField(max_length=100)
    notes = serializers.CharField(required=False, allow_blank=True, default='')


# Serializer for viewing projects / Серіалізатор для перегляду проектів
class ProjectSerializer(serializers.ModelSerializer):
    places = ProjectPlaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'completed', 'places']
        read_only_fields = ['id', 'completed', 'places']


# Serializer for creating/updating projects / Серіалізатор для створення/оновлення проектів
class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    places = NestedPlaceCreateSerializer(many=True, required=False, write_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'completed', 'places']
        read_only_fields = ['id', 'completed']

    # Custom places validation logic / Кастомна валідація списку місць
    def validate_places(self, value):
        # 1. Enforce limit of maximum 10 places / Перевірка ліміту в 10 місць
        if len(value) > 10:
            raise serializers.ValidationError("A project cannot have more than 10 places.")

        # 2. Prevent duplicate external IDs in request / Запобігання дублюванню ID у запиті
        external_ids = [item['external_id'] for item in value]
        if len(external_ids) != len(set(external_ids)):
            raise serializers.ValidationError("Duplicate external place IDs are not allowed in the same project.")

        # 3. Validate places in external API / Валідація місць у зовнішньому API
        validated_places = []
        for item in value:
            ext_id = item['external_id']
            artwork_details = ArtInstituteService.get_artwork_details(ext_id)
            if not artwork_details:
                raise serializers.ValidationError(f"Place with external ID '{ext_id}' does not exist in the Art Institute of Chicago API.")
            
            validated_places.append({
                'external_id': ext_id,
                'notes': item.get('notes', ''),
                'title': artwork_details['title']
            })
        return validated_places

    # Create project and places inside an atomic transaction / Створення проекту та місць в атомарній транзакції
    def create(self, validated_data):
        places_data = validated_data.pop('places', [])
        
        from django.db import transaction
        with transaction.atomic():
            project = Project.objects.create(**validated_data)
            for place_item in places_data:
                ProjectPlace.objects.create(project=project, **place_item)
            
            project.update_completion_status()
            
        return project

    # Prevent nested place updates via project update / Запобігання оновленню вкладених місць при зміні проекту
    def update(self, instance, validated_data):
        validated_data.pop('places', None)
        return super().update(instance, validated_data)


# Serializer for adding a single place to project / Серіалізатор для додавання одного місця до проекту
class ProjectPlaceAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlace
        fields = ['external_id', 'notes']

    # Custom single place validation / Кастомна валідація одного місця
    def validate(self, attrs):
        project = self.context.get('project')
        if not project:
            raise serializers.ValidationError("Project context is required.")
        
        external_id = attrs.get('external_id')
        
        # 1. Enforce limit of maximum 10 places / Перевірка ліміту в 10 місць
        if project.places.count() >= 10:
            raise serializers.ValidationError({"non_field_errors": "A project cannot have more than 10 places."})

        # 2. Prevent adding the same place twice / Запобігання повторному додаванню
        if project.places.filter(external_id=external_id).exists():
            raise serializers.ValidationError({"external_id": "This place has already been added to this project."})

        # 3. Validate existence in external API / Валідація у зовнішньому API
        artwork_details = ArtInstituteService.get_artwork_details(external_id)
        if not artwork_details:
            raise serializers.ValidationError({"external_id": f"Place with external ID '{external_id}' does not exist in the Art Institute of Chicago API."})

        attrs['title'] = artwork_details['title']
        return attrs


# Serializer for updating place details / Серіалізатор для оновлення деталей місця
class ProjectPlaceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPlace
        fields = ['notes', 'visited']
