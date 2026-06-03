# Travel Planner API (Django REST Framework)

This is a RESTful CRUD application designed for managing travel projects and collecting artworks/places to visit. It integrates with the Art Institute of Chicago API to fetch and validate artwork details, implements smart caching, supports automated state recalculations, and enforces strict business rule validations.


## Features

- **Travel Projects**: Create, retrieve, list, update, and delete travel projects.
- **Project Places**: Add, retrieve, list, update notes/visited status for individual places.
- **Third-Party API Integration**: Fetches and validates places using the [Art Institute of Chicago API](https://api.artic.edu/docs/#collections).
- **Business Rule Validations**:
  - A project cannot be deleted if any of its places are marked as visited.
  - A project can contain a maximum of 10 places.
  - The same external place cannot be added to a project more than once.
- **Automatic Project Status Updates**: Projects are automatically marked as `completed` when all of their places are visited.
- **Caching**: Successful external API queries are cached locally for 24 hours to prevent rate-limiting and improve response times.
- **Automated Tests**: Comprehensive test suite consisting of 14 unit tests covering endpoints and validations.

---

## Installation & Setup

### Option 1: Running Locally (Django Dev Server)

1. **Clone the repository and open the project directory**:
   cd TravelPlanner

2. **Create and activate a Python virtual environment**:
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

3. **Install dependencies**:
   pip install -r requirements.txt


4. **Run migrations (Initializes database)**:
   python manage.py migrate

5. **Start the development server**:
   python manage.py runserver
   The API will be available at `http://127.0.0.1:8000/`.


### Option 2: Running with Docker
Make sure Docker Desktop is open and running on your system.

1. **Build and start the container**:
   docker-compose up --build
   This automatically runs migrations and hosts the application


## Running Automated Tests

To execute the test suite:
python manage.py test planner


## API Documentation & Endpoints

### Postman Collection

All endpoints are defined in the Postman collection file in the root of the project:
🔗 **[TravelPlanner.postman_collection.json](./TravelPlanner.postman_collection.json)**

*To use it, import this file directly into your Postman application. Make sure the local server is running on port `8000`.*


### Interactive Web UI (Browsable API)

Django REST Framework provides an interactive web UI. You can open `http://127.0.0.1:8000/api/projects/` directly in your browser to view, create (using the **Raw Data** JSON form at the bottom), and test endpoints visually.

### Endpoints Table

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/projects/` | Create a new project (can include nested places) |
| **GET** | `/api/projects/` | List all projects (supports `?completed=true/false` and `?search=query`) |
| **GET** | `/api/projects/<id>/` | Retrieve details of a single project and its places |
| **PATCH** / **PUT** | `/api/projects/<id>/` | Update project name, description, start date |
| **DELETE** | `/api/projects/<id>/` | Delete project (fails if any place is visited) |
| **GET** | `/api/projects/<id>/places/` | List all places added to a project |
| **POST** | `/api/projects/<id>/places/` | Add a single place to a project (validates in Chicago API) |
| **GET** | `/api/projects/<id>/places/<place_id>/` | Get details of a single place in a project |
| **PATCH** / **PUT** | `/api/projects/<id>/places/<place_id>/` | Update place notes or set `visited` status |
| **DELETE** | `/api/projects/<id>/places/<place_id>/` | Remove a place from a project |


## Example Request Payloads

### 1. Create a Project with Places
**`POST /api/projects/`**
{
    "name": "Art Excursion Chicago",
    "description": "Museum trip plan",
    "start_date": "2026-08-20",
    "places": [
        {
            "external_id": "27992",
            "notes": "A Sunday on La Grande Jatte Georges Seurat"
        },
        {
            "external_id": "16568",
            "notes": "The Bedroom Vincent van Gogh"
        }
    ]
}

### 2. Add a Place to Project
**`POST /api/projects/1/places/`**
{
    "external_id": "28560",
    "notes": "Self-Portrait Van Gogh"
}

### 3. Update Place Status (Mark Visited)
**`PATCH /api/projects/1/places/1/`**
{
    "notes": "Visited today! Spectacular details.",
    "visited": true
}
