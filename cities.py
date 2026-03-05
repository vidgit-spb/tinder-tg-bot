# Города-миллионники России
# Список актуален на 2024 год

RUSSIAN_CITIES = {
    'moscow': {
        'name': 'Москва',
        'name_en': 'Moscow',
        'population': 13000000,
        'emoji': '🏛️'
    },
    'spb': {
        'name': 'Санкт-Петербург',
        'name_en': 'Saint Petersburg',
        'population': 5600000,
        'emoji': '🌉'
    },
    'novosibirsk': {
        'name': 'Новосибирск',
        'name_en': 'Novosibirsk',
        'population': 1600000,
        'emoji': '🏙️'
    },
    'ekaterinburg': {
        'name': 'Екатеринбург',
        'name_en': 'Yekaterinburg',
        'population': 1500000,
        'emoji': '🏔️'
    },
    'kazan': {
        'name': 'Казань',
        'name_en': 'Kazan',
        'population': 1300000,
        'emoji': '🕌'
    },
    'nizhny': {
        'name': 'Нижний Новгород',
        'name_en': 'Nizhny Novgorod',
        'population': 1200000,
        'emoji': '⛪'
    },
    'chelyabinsk': {
        'name': 'Челябинск',
        'name_en': 'Chelyabinsk',
        'population': 1200000,
        'emoji': '🏭'
    },
    'samara': {
        'name': 'Самара',
        'name_en': 'Samara',
        'population': 1100000,
        'emoji': '🚀'
    },
    'omsk': {
        'name': 'Омск',
        'name_en': 'Omsk',
        'population': 1100000,
        'emoji': '🏛️'
    },
    'rostov': {
        'name': 'Ростов-на-Дону',
        'name_en': 'Rostov-on-Don',
        'population': 1100000,
        'emoji': '🌾'
    },
    'ufa': {
        'name': 'Уфа',
        'name_en': 'Ufa',
        'population': 1100000,
        'emoji': '🏞️'
    },
    'krasnoyarsk': {
        'name': 'Красноярск',
        'name_en': 'Krasnoyarsk',
        'population': 1100000,
        'emoji': '🌲'
    },
    'voronezh': {
        'name': 'Воронеж',
        'name_en': 'Voronezh',
        'population': 1000000,
        'emoji': '🌳'
    },
    'perm': {
        'name': 'Пермь',
        'name_en': 'Perm',
        'population': 1000000,
        'emoji': '🏔️'
    },
    'volgograd': {
        'name': 'Волгоград',
        'name_en': 'Volgograd',
        'population': 1000000,
        'emoji': '⚔️'
    }
}

def get_city_keyboard():
    """Возвращает список городов для inline клавиатуры"""
    cities = []
    for city_id, city_data in RUSSIAN_CITIES.items():
        cities.append({
            'id': city_id,
            'display': f"{city_data['emoji']} {city_data['name']}",
            'name': city_data['name']
        })
    return cities

def get_city_name(city_id):
    """Получить название города по ID"""
    if city_id in RUSSIAN_CITIES:
        return RUSSIAN_CITIES[city_id]['name']
    return city_id

def get_city_display(city_id):
    """Получить отображаемое название с эмодзи"""
    if city_id in RUSSIAN_CITIES:
        city = RUSSIAN_CITIES[city_id]
        return f"{city['emoji']} {city['name']}"
    return city_id
