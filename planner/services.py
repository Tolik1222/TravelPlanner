import requests
from django.core.cache import cache

# Service to interact with the Art Institute of Chicago API / Сервіс для взаємодії з API Art Institute of Chicago
class ArtInstituteService:
    BASE_URL = "https://api.artic.edu/api/v1/artworks"

    @classmethod
    def get_artwork_details(cls, external_id):
        # Cache lookup based on external_id / Пошук у кеші за ідентифікатором external_id
        cache_key = f"artwork_{external_id}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        url = f"{cls.BASE_URL}/{external_id}"
        try:
            # Set polite User-Agent headers / Налаштування заголовка User-Agent для ідентифікації клієнта
            headers = {
                'User-Agent': 'TravelPlannerApp/1.0 (contact@travelplanner.local)'
            }
            # Fetch data from Art Institute API / Отримання даних з API Art Institute
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                artwork_data = json_data.get('data')
                if artwork_data and 'title' in artwork_data:
                    result = {
                        'title': artwork_data['title']
                    }
                    # Cache result for 24 hours / Збереження результату в кеші на 24 години
                    cache.set(cache_key, result, timeout=86400)
                    return result
        except requests.RequestException:
            # Silence HTTP errors / Заглушення помилок HTTP-запитів
            pass

        return None
