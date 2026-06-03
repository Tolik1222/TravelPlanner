# Travel Planner API (Django REST Framework)

[English Version](#english-version) | [Українська версія](#українська-версія)

---

## English Version

This is a RESTful CRUD application designed for managing travel projects and collecting artworks/places to visit. It integrates with the Art Institute of Chicago API to fetch and validate artwork details, implements smart caching, supports automated state recalculations, and enforces strict business rule validations.

### Features
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

### Installation & Setup

#### Option 1: Running Locally (Django Dev Server)
1. **Clone the repository and open the project directory**:
   ```bash
   cd TravelPlanner
   ```
2. **Create and activate a Python virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run migrations (Initializes database)**:
   ```bash
   python manage.py migrate
   ```
5. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://127.0.0.1:8000/`.

#### Option 2: Running with Docker
Make sure Docker Desktop is open and running on your system.
1. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```
   This automatically runs migrations and hosts the application on `http://localhost:8000/`.

### Running Automated Tests
To execute the test suite:
```bash
python manage.py test planner
```

### API Documentation & Endpoints

#### Postman Collection
All endpoints are defined in the Postman collection file in the root of the project:
🔗 **[TravelPlanner.postman_collection.json](./TravelPlanner.postman_collection.json)**
*To use it, import this file directly into your Postman application. Make sure the local server is running on port `8000`.*

#### Interactive Web UI (Browsable API)
Django REST Framework provides an interactive web UI. You can open `http://127.0.0.1:8000/api/projects/` directly in your browser to view, create (using the **Raw Data** JSON form at the bottom), and test endpoints visually.

#### Endpoints Table
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

### Example Request Payloads

#### 1. Create a Project with Places
**`POST /api/projects/`**
```json
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
```

#### 2. Add a Place to Project
**`POST /api/projects/1/places/`**
```json
{
    "external_id": "28560",
    "notes": "Self-Portrait Van Gogh"
}
```

#### 3. Update Place Status (Mark Visited)
**`PATCH /api/projects/1/places/1/`**
```json
{
    "notes": "Visited today! Spectacular details.",
    "visited": true
}
```

---

## Українська версія

Це CRUD-додаток на базі REST API, розроблений для керування туристичними проектами та збору визначних місць/експонатів для відвідування. Додаток інтегрується з API Художнього інституту Чикаго для перевірки існування та назви місць, підтримує розумне кешування відповідей, автоматично перераховує статус готовності подорожі та забезпечує суворі бізнес-валідації.

### Функціонал
- **Туристичні проекти**: Створення, отримання, перегляд списку, оновлення та видалення проектів.
- **Місця у проекті**: Додавання, перегляд списку, оновлення нотаток та статусу відвідування для кожного місця.
- **Інтеграція з API**: Валідація місць через офіційний [Art Institute of Chicago API](https://api.artic.edu/docs/#collections).
- **Суворі бізнес-правила та валідації**:
  - Проект не можна видалити, якщо хоча б одне з його місць позначено як відвідане (`visited: true`).
  - Проект може містити максимум 10 місць.
  - Одне й те саме місце не може бути додано до проекту двічі.
- **Автоматичне оновлення статусів**: Проект автоматично маркується як завершений (`completed: true`), коли всі його місця стають відвіданими.
- **Кешування**: Успішні запити до стороннього API зберігаються локально на 24 години для зменшення навантаження та прискорення роботи.
- **Автоматичні тести**: Набір з 14 юніт-тестів, що покривають ключові ендпоінти, моделі та валідації.

### Встановлення та запуск

#### Варіант 1: Локальний запуск (Django Development Server)
1. **Перейдіть у папку проекту**:
   ```bash
   cd TravelPlanner
   ```
2. **Створіть та активуйте віртуальне оточення Python**:
   ```bash
   python -m venv venv
   # Для Windows:
   venv\Scripts\activate
   # Для macOS/Linux:
   source venv/bin/activate
   ```
3. **Встановіть залежності**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Запустіть міграції для створення бази даних**:
   ```bash
   python manage.py migrate
   ```
5. **Запустіть сервер розробки**:
   ```bash
   python manage.py runserver
   ```
   Додаток буде доступний за адресою `http://127.0.0.1:8000/`.

#### Варіант 2: Запуск через Docker
Переконайтеся, що на вашому комп'ютері запущено Docker Desktop.
1. **Зберіть та запустіть контейнер**:
   ```bash
   docker-compose up --build
   ```
   Це автоматично запустить міграції бази даних і зробить додаток доступним на `http://localhost:8000/`.

### Запуск автоматичних тестів
Щоб запустити тести, виконайте:
```bash
python manage.py test planner
```

### Документація API та ендпоінти

#### Колекція Postman
Усі запити описані в колекції Postman у корені проекту:
🔗 **[TravelPlanner.postman_collection.json](./TravelPlanner.postman_collection.json)**
*Імпортуйте цей файл у Postman для зручного тестування.*

#### Інтерактивний вебінтерфейс (Browsable API)
Django REST Framework надає вбудовану веб-панель. Ви можете відкрити посилання `http://127.0.0.1:8000/api/projects/` у браузері, щоб візуально створювати та редагувати проекти (використовуючи форму **Raw Data** внизу сторінки).

#### Таблиця ендпоінтів
| Метод | Ендпоінт | Опис |
| :--- | :--- | :--- |
| **POST** | `/api/projects/` | Створити проект (можна з вкладеним масивом місць) |
| **GET** | `/api/projects/` | Отримати список проектів (підтримує `?completed=true/false` та `?search=запит`) |
| **GET** | `/api/projects/<id>/` | Отримати деталі одного проекту та список його місць |
| **PATCH** / **PUT** | `/api/projects/<id>/` | Оновити назву, опис, дату початку проекту |
| **DELETE** | `/api/projects/<id>/` | Видалити проект (заблокує, якщо є відвідані місця) |
| **GET** | `/api/projects/<id>/places/` | Список усіх місць, доданих до конкретного проекту |
| **POST** | `/api/projects/<id>/places/` | Додати одне місце до проекту (валідується через API музею) |
| **GET** | `/api/projects/<id>/places/<place_id>/` | Деталі одного місця в межах проекту |
| **PATCH** / **PUT** | `/api/projects/<id>/places/<place_id>/` | Оновити нотатки або статус відвідання місця |
| **DELETE** | `/api/projects/<id>/places/<place_id>/` | Видалити місце з проекту |

### Приклади JSON-запитів

#### 1. Створення проекту з місцями
**`POST /api/projects/`**
```json
{
    "name": "Арт-екскурсія в Чикаго",
    "description": "План поїздки до музею мистецтв",
    "start_date": "2026-08-20",
    "places": [
        {
            "external_id": "27992",
            "notes": "Картина Гранд-Жатт, автор Жорж Сьора"
        },
        {
            "external_id": "16568",
            "notes": "Спальня в Арлі, автор Вінсент ван Гог"
        }
    ]
}
```

#### 2. Додавання одного місця до проекту
**`POST /api/projects/1/places/`**
```json
{
    "external_id": "28560",
    "notes": "Автопортрет Ван Гога"
}
```

#### 3. Позначення місця як відвіданого
**`PATCH /api/projects/1/places/1/`**
```json
{
    "notes": "Вже відвідав сьогодні! Неймовірні деталі.",
    "visited": true
}
```

---

## Example Artwork IDs for Testing / Реальні ID витворів мистецтва для тестування

Here are 10 valid artwork IDs from the Art Institute of Chicago API that you can use to test the validation and creation logic:
Ось 10 валідних ідентифікаторів експонатів з API Художнього інституту Чикаго, які можна використовувати для тестування:

1.  **`27992`** — *A Sunday on La Grande Jatte — 1884* (Georges Seurat) / «Недільний день на острові Гранд-Жатт — 1884» (Жорж Сьора)
2.  **`16568`** — *The Bedroom* (Vincent van Gogh) / «Спальня в Арлі» (Вінсент ван Гог)
3.  **`28560`** — *Self-Portrait* (Vincent van Gogh) / «Автопортрет» (Вінсент ван Гог)
4.  **`21979`** — *Water Lilies* (Claude Monet) / «Водяні лілії» (Клод Моне)
5.  **`65514`** — *American Gothic* (Grant Wood) / «Американська готика» (Грант Вуд)
6.  **`81548`** — *Nighthawks* (Edward Hopper) / «Полуночники» (Едвард Гоппер)
7.  **`11153`** — *Sky above Clouds IV* (Georgia O'Keeffe) / «Небо над хмарами IV» (Джорджія О'Кіфф)
8.  **`27993`** — *The Market-Woman* (Albrecht Dürer) / «Ринкова торговка» (Альбрехт Дюрер)
9.  **`27995`** — *Landscape with Cannon* (Albrecht Dürer) / «Пейзаж із гарматою» (Альбрехт Дюрер)
10. **`24645`** — *The Old Guitarist* (Pablo Picasso) / «Старий гітарист» (Пабло Пікассо)

---

## Future Improvements for a Successful Project / Подальші можливі удосконалення для успішного проекту

To scale this application into a fully-featured, production-ready product, the following enhancements are recommended:
Для перетворення цього проекту на повноцінний ринковий продукт рекомендується реалізувати наступні покращення:

1.  **User Authentication & Security (Авторизація користувачів)**:
    - Implement JWT token authorization (e.g. `django-rest-framework-simplejwt`) and connect projects to specific user accounts so that users can only manage their own trip plans.
    - Впровадження авторизації за JWT-токенами та прив'язка проектів до користувачів, щоб кожен міг бачити та редагувати лише власні плани.
2.  **Search Proxy Endpoint (Ендпоінт для пошуку експонатів)**:
    - Create a search endpoint on our backend (e.g. `/api/places/search/?q=...`) that acts as a proxy to query the Art Institute of Chicago API and return list of suggestions with titles and IDs to make it easier for clients to choose artworks.
    - Створення проксі-ендпоінту на нашому бекенді для зручного пошуку експонатів за назвою прямо через зовнішнє API, щоб фронтенд міг пропонувати підказки.
3.  **Detailed Metadata & Image URLs (Збереження додаткових метаданих та зображень)**:
    - Save additional artwork metadata like artist name, year of creation, style, and high-resolution image URLs to enhance the frontend visualization.
    - Збереження додаткової інформації про експонати (ім'я художника, рік створення, стиль, посилання на зображення) для красивого відображення на фронтенді.
4.  **Interactive Museum Mapping (Інтерактивна навігація)**:
    - Map the artworks to their actual physical exhibition room IDs in the museum to generate optimal walking paths for travellers.
    - Прив'язка експонатів до номерів виставкових залів музею для побудови оптимального маршруту прогулянки туриста між обраними точками.
5.  **Trip Sharing & Collaboration (Спільне планування)**:
    - Enable collaborative travel projects where multiple users can add notes, chat, and check off places together.
    - Можливість ділитися планами подорожей із друзями та спільно редагувати нотатки й відмічати відвідані місця в реальному часі.
