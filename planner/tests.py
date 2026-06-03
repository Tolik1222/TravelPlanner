from unittest.mock import patch
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Project, ProjectPlace

class TravelPlannerTests(APITestCase):

    def setUp(self):
        # Create a sample project to be used in various tests
        self.project = Project.objects.create(
            name="Paris Getaway",
            description="A trip to the City of Light",
            start_date="2026-07-01"
        )
        # Create sample places for the project
        self.place1 = ProjectPlace.objects.create(
            project=self.project,
            external_id="12345",
            title="A Sunday on La Grande Jatte",
            notes="Must see",
            visited=False
        )
        self.place2 = ProjectPlace.objects.create(
            project=self.project,
            external_id="67890",
            title="The Bedroom",
            notes="Vincent van Gogh masterpiece",
            visited=False
        )

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_create_project_without_places(self, mock_get_details):
        url = reverse('project-list')
        data = {
            "name": "Japan Exploration",
            "description": "Visiting Tokyo and Kyoto",
            "start_date": "2026-10-10"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 2)
        project = Project.objects.get(name="Japan Exploration")
        self.assertEqual(project.completed, False)
        self.assertEqual(project.places.count(), 0)

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_create_project_with_places_success(self, mock_get_details):
        # Mocking Art Institute of Chicago API responses
        mock_get_details.side_effect = lambda ext_id: {'title': f"Artwork {ext_id}"} if ext_id in ["111", "222"] else None

        url = reverse('project-list')
        data = {
            "name": "Chicago Museums",
            "description": "Art tour",
            "start_date": "2026-08-15",
            "places": [
                {"external_id": "111", "notes": "Fascinating painting"},
                {"external_id": "222", "notes": "Famous sculpture"}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(name="Chicago Museums")
        self.assertEqual(project.places.count(), 2)
        self.assertEqual(project.places.filter(external_id="111").first().title, "Artwork 111")
        self.assertEqual(project.completed, False)

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_create_project_with_places_validation_error_not_exists(self, mock_get_details):
        # Mock API returns None (artwork does not exist)
        mock_get_details.return_value = None

        url = reverse('project-list')
        data = {
            "name": "Invalid Places Project",
            "places": [
                {"external_id": "999"}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Ensure project was not created due to validation error
        self.assertFalse(Project.objects.filter(name="Invalid Places Project").exists())

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_create_project_exceeding_max_places(self, mock_get_details):
        url = reverse('project-list')
        data = {
            "name": "Too Many Places",
            "places": [{"external_id": str(i)} for i in range(11)]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("places", response.data)

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_create_project_duplicate_places(self, mock_get_details):
        url = reverse('project-list')
        data = {
            "name": "Duplicate Places",
            "places": [
                {"external_id": "111"},
                {"external_id": "111"}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_project_prevented_if_visited(self):
        # Mark one place as visited
        self.place1.visited = True
        self.place1.save()

        # Try to delete the project
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Verify project is still in database
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project_allowed_if_not_visited(self):
        # Ensure all places are visited=False
        self.assertEqual(self.project.places.filter(visited=True).count(), 0)

        # Delete the project
        url = reverse('project-detail', args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Verify project is deleted
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_project_completion_auto_recalculation(self):
        self.project.update_completion_status()
        self.assertEqual(self.project.completed, False)

        # Mark first place as visited
        self.place1.visited = True
        self.place1.save()
        self.project.refresh_from_db()
        self.assertEqual(self.project.completed, False)

        # Mark second place as visited
        self.place2.visited = True
        self.place2.save()
        self.project.refresh_from_db()
        self.assertEqual(self.project.completed, True)

        # Mark first place back to unvisited
        self.place1.visited = False
        self.place1.save()
        self.project.refresh_from_db()
        self.assertEqual(self.project.completed, False)

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_add_place_to_existing_project_success(self, mock_get_details):
        mock_get_details.return_value = {'title': 'Water Lilies'}

        url = reverse('project-places-list', args=[self.project.id])
        data = {
            "external_id": "999",
            "notes": "Beautiful Impressionist painting"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.project.places.count(), 3)
        self.assertEqual(self.project.places.filter(external_id="999").first().title, "Water Lilies")

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_add_place_duplicate_prevented(self, mock_get_details):
        # We try to add place1's ID again
        url = reverse('project-places-list', args=[self.project.id])
        data = {
            "external_id": "12345",
            "notes": "Duplicate entry"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("external_id", response.data)

    @patch('planner.services.ArtInstituteService.get_artwork_details')
    def test_add_place_limit_exceeded(self, mock_get_details):
        mock_get_details.side_effect = lambda ext_id: {'title': f"Artwork {ext_id}"}
        
        # Add 8 more places to reach the limit of 10
        for i in range(8):
            ProjectPlace.objects.create(
                project=self.project,
                external_id=f"extra_{i}",
                title=f"Extra {i}"
            )
        self.assertEqual(self.project.places.count(), 10)

        # Attempt to add the 11th place
        url = reverse('project-places-list', args=[self.project.id])
        data = {
            "external_id": "eleventh",
            "notes": "Should fail"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_place_notes_and_visited(self):
        url = reverse('project-places-detail', args=[self.project.id, self.place1.id])
        data = {
            "notes": "Updated notes",
            "visited": True
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.place1.refresh_from_db()
        self.assertEqual(self.place1.notes, "Updated notes")
        self.assertEqual(self.place1.visited, True)
        
        # Check if project completion updated
        self.project.refresh_from_db()
        self.assertEqual(self.project.completed, False) # Because place2 is still unvisited

    def test_list_places_for_project(self):
        url = reverse('project-places-list', args=[self.project.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify the structure/count of results (paginated)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['external_id'], self.place1.external_id)

    def test_get_single_place_within_project(self):
        url = reverse('project-places-detail', args=[self.project.id, self.place1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['external_id'], self.place1.external_id)
        self.assertEqual(response.data['title'], self.place1.title)
