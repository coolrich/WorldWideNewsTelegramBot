from user_controller import User
import pickle
from google.cloud import storage


class Users:
    def __init__(self, bucket_name: str = "users_news_data"):
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()
        self.bucket: storage.Bucket = self.storage_client.bucket(bucket_name)
        if not Users.__is_bucket_exists(bucket_name):
            self.bucket = self.storage_client.create_bucket(bucket_name)

    @staticmethod
    def __is_bucket_exists(bucket_name):
        storage_client = storage.Client()
        buckets: list = storage_client.list_buckets()
        if bucket_name in [bucket.name for bucket in buckets]:
            return True
        return False

    def add_user(self, user: User):
        """Зберігає об'єкт User у Cloud Storage."""
        user_pickle = pickle.dumps(user)  # Серіалізуємо об'єкт User у Pickle
        blob = self.bucket.blob(f"user_{user.chat_id}.pickle")  # Створюємо blob
        blob.upload_from_string(user_pickle)  # Завантажуємо blob у сховище

    def get_user(self, chat_id: int) -> User:
        """Завантажує об'єкт User з Cloud Storage."""
        blob = self.bucket.blob(f"user_{chat_id}.pickle")  # Отримуємо blob за ключем
        if blob.exists():
            user_pickle = blob.download_as_string()  # Завантажуємо вміст blob
            user = pickle.loads(user_pickle)  # Десеріалізуємо Pickle у словник
            return user  # Повертаємо об'єкт User зі словника
        else:
            return None  # Повертаємо None, якщо об'єкт не знайдено
