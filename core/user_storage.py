from core.user_controller import User


class Users:
    users: list[User] = list()

    @staticmethod
    def get_user(chat_id: int):
        for user in Users.users:
            if user == chat_id:
                return user

    @staticmethod
    def add_user(chat_id: int):
        Users.users.append(User(chat_id))
