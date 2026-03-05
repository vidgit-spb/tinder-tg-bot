import unittest
import sqlite3
import os
from database import Database
from cities import get_city_keyboard, get_city_name, get_city_display, RUSSIAN_CITIES

class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Создаём тестовую базу данных перед каждым тестом"""
        self.test_db_path = "test_dating_bot.db"
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = Database(self.test_db_path)
    
    def tearDown(self):
        """Удаляем тестовую базу после каждого теста"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_create_user(self):
        """Тест создания пользователя"""
        self.db.create_user(
            user_id=123,
            username="testuser",
            first_name="Test",
            name="Test User",
            age=25,
            gender="male",
            looking_for="female",
            bio="Test bio",
            photo_id="test_photo_id",
            city="Москва"
        )
        
        user = self.db.get_user(123)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], "Test User")
        self.assertEqual(user['age'], 25)
        self.assertEqual(user['gender'], "male")
        self.assertEqual(user['city'], "Москва")
    
    def test_user_exists(self):
        """Тест проверки существования пользователя"""
        self.assertFalse(self.db.user_exists(999))
        
        self.db.create_user(
            user_id=999,
            username="test",
            first_name="Test",
            name="Test",
            age=25,
            gender="male",
            looking_for="female",
            bio="Test"
        )
        
        self.assertTrue(self.db.user_exists(999))
    
    def test_add_like(self):
        """Тест добавления лайка"""
        # Создаём двух пользователей
        self.db.create_user(1, "user1", "User", "User 1", 25, "male", "female", "Bio 1")
        self.db.create_user(2, "user2", "User", "User 2", 23, "female", "male", "Bio 2")
        
        # Первый лайк - не матч
        is_match = self.db.add_like(1, 2)
        self.assertFalse(is_match)
        
        # Взаимный лайк - матч!
        is_match = self.db.add_like(2, 1)
        self.assertTrue(is_match)
    
    def test_get_matches(self):
        """Тест получения матчей"""
        self.db.create_user(1, "user1", "User", "User 1", 25, "male", "female", "Bio 1")
        self.db.create_user(2, "user2", "User", "User 2", 23, "female", "male", "Bio 2")
        self.db.create_user(3, "user3", "User", "User 3", 24, "female", "male", "Bio 3")
        
        # Создаём матчи
        self.db.add_like(1, 2)
        self.db.add_like(2, 1)  # Матч с user 2
        
        self.db.add_like(1, 3)
        self.db.add_like(3, 1)  # Матч с user 3
        
        matches = self.db.get_matches(1)
        self.assertEqual(len(matches), 2)
    
    def test_save_and_get_messages(self):
        """Тест сохранения и получения сообщений"""
        self.db.create_user(1, "user1", "User", "User 1", 25, "male", "female", "Bio 1")
        self.db.create_user(2, "user2", "User", "User 2", 23, "female", "male", "Bio 2")
        
        # Сохраняем сообщения
        self.db.save_message(1, 2, "Привет!")
        self.db.save_message(2, 1, "Привет! Как дела?")
        self.db.save_message(1, 2, "Отлично!")
        
        messages = self.db.get_messages(1, 2)
        self.assertEqual(len(messages), 3)
        # Проверяем что все сообщения есть
        message_texts = [msg['message'] for msg in messages]
        self.assertIn("Привет!", message_texts)
        self.assertIn("Привет! Как дела?", message_texts)
        self.assertIn("Отлично!", message_texts)
    
    def test_age_filter(self):
        """Тест фильтра по возрасту"""
        # Создаём пользователя с фильтром 25-35
        self.db.create_user(1, "user1", "User", "User 1", 30, "male", "female", "Bio 1")
        self.db.set_age_filter(1, 25, 35)
        
        # Создаём кандидатов разного возраста
        self.db.create_user(2, "user2", "User", "User 2", 20, "female", "male", "Bio 2")  # Слишком молодая
        self.db.create_user(3, "user3", "User", "User 3", 28, "female", "male", "Bio 3")  # Подходит
        self.db.create_user(4, "user4", "User", "User 4", 40, "female", "male", "Bio 4")  # Слишком старая
        
        candidates = self.db.get_candidates(1, limit=10)
        
        # Должен быть только один кандидат (28 лет)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]['age'], 28)
    
    def test_statistics_tracking(self):
        """Тест отслеживания статистики"""
        self.db.create_user(1, "user1", "User", "User 1", 25, "male", "female", "Bio 1")
        self.db.create_user(2, "user2", "User", "User 2", 23, "female", "male", "Bio 2")
        
        # Отслеживаем просмотр
        self.db.track_profile_view(1, 2)
        self.db.track_profile_view(1, 2)
        
        stats = self.db.get_user_stats(2)
        self.assertIsNotNone(stats)
        self.assertEqual(stats['total_views'], 2)
        
        # Отслеживаем лайк
        self.db.update_like_stats(1, 2)
        
        stats = self.db.get_user_stats(1)
        self.assertEqual(stats['total_likes_sent'], 1)
        
        stats = self.db.get_user_stats(2)
        self.assertEqual(stats['total_likes_received'], 1)
    
    def test_admin_stats(self):
        """Тест админской статистики"""
        # Создаём тестовые данные
        self.db.create_user(1, "user1", "User", "User 1", 25, "male", "female", "Bio 1")
        self.db.create_user(2, "user2", "User", "User 2", 23, "female", "male", "Bio 2")
        
        self.db.add_like(1, 2)
        self.db.add_like(2, 1)
        
        self.db.save_message(1, 2, "Test message")
        
        stats = self.db.get_admin_stats()
        
        self.assertEqual(stats['total_users'], 2)
        self.assertEqual(stats['total_matches'], 1)
        self.assertEqual(stats['total_messages'], 1)
    
    def test_top_users(self):
        """Тест топа пользователей"""
        # Создаём пользователей
        self.db.create_user(1, "user1", "User", "User 1", 25, "male", "female", "Bio 1")
        self.db.create_user(2, "user2", "User", "User 2", 23, "female", "male", "Bio 2")
        self.db.create_user(3, "user3", "User", "User 3", 24, "female", "male", "Bio 3")
        
        # User 2: 10 просмотров, 8 лайков = 80%
        for _ in range(10):
            self.db.track_profile_view(1, 2)
        for _ in range(8):
            self.db.update_like_stats(1, 2)
        
        # User 3: 10 просмотров, 5 лайков = 50%
        for _ in range(10):
            self.db.track_profile_view(1, 3)
        for _ in range(5):
            self.db.update_like_stats(1, 3)
        
        top_users = self.db.get_top_users(limit=10)
        
        # User 2 должен быть первым (80% > 50%)
        self.assertEqual(top_users[0]['user_id'], 2)
        self.assertEqual(top_users[0]['like_rate'], 80.0)
        
        self.assertEqual(top_users[1]['user_id'], 3)
        self.assertEqual(top_users[1]['like_rate'], 50.0)


class TestCities(unittest.TestCase):
    def test_get_city_keyboard(self):
        """Тест получения списка городов для клавиатуры"""
        cities = get_city_keyboard()
        
        self.assertIsInstance(cities, list)
        self.assertGreater(len(cities), 0)
        
        # Проверяем структуру
        for city in cities:
            self.assertIn('id', city)
            self.assertIn('display', city)
            self.assertIn('name', city)
    
    def test_get_city_name(self):
        """Тест получения названия города"""
        name = get_city_name('moscow')
        self.assertEqual(name, 'Москва')
        
        name = get_city_name('spb')
        self.assertEqual(name, 'Санкт-Петербург')
        
        # Несуществующий город
        name = get_city_name('unknown')
        self.assertEqual(name, 'unknown')
    
    def test_get_city_display(self):
        """Тест получения отображаемого названия города"""
        display = get_city_display('moscow')
        self.assertIn('Москва', display)
        self.assertIn('🏛️', display)
    
    def test_all_cities_have_required_fields(self):
        """Тест что все города имеют необходимые поля"""
        for city_id, city_data in RUSSIAN_CITIES.items():
            self.assertIn('name', city_data)
            self.assertIn('name_en', city_data)
            self.assertIn('population', city_data)
            self.assertIn('emoji', city_data)
            
            self.assertIsInstance(city_data['population'], int)
            self.assertGreater(city_data['population'], 0)


class TestConfig(unittest.TestCase):
    def test_config_imports(self):
        """Тест что конфигурация импортируется без ошибок"""
        try:
            from config import (
                BOT_TOKEN, STARS_TO_SEE_LIKES, BOT_NAME, 
                WELCOME_MESSAGE, DATABASE_PATH, ADMIN_USER_IDS
            )
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import config: {e}")
    
    def test_stars_price(self):
        """Тест что цена Stars корректна"""
        from config import STARS_TO_SEE_LIKES
        self.assertIsInstance(STARS_TO_SEE_LIKES, int)
        self.assertGreater(STARS_TO_SEE_LIKES, 0)
        self.assertLessEqual(STARS_TO_SEE_LIKES, 1000)


def run_tests():
    """Запуск всех тестов"""
    # Создаём test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем все тесты
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestCities))
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Возвращаем True если все тесты прошли
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
