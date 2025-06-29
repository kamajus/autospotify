import json
from logging import ERROR
from typing import List

import autospotify.settings as settings
from autospotify.settings import accounts_path
from autospotify.utils.logs import log
from autospotify.utils.proxies import transform_proxy
from autospotify.utils.schemas import AccountFilter, User


def read_proxies_from_txt():
    try:
        with open(settings.proxies_path, "r") as file:
            proxies_result = file.readlines()

        proxies = [
            transform_proxy(line.strip()) for line in proxies_result if line.strip()
        ]

        return proxies

    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading TXT file: {e}")
        return []


def read_user_from_json(username: str) -> User:
    try:
        with open(accounts_path, "r", encoding="utf-8") as file:
            users = json.load(file)

        for user in users:
            if user["username"] == username:
                return user
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        log(f"Error: The file '{accounts_path}' is not a valid JSON.", ERROR)
        raise
    except Exception as e:
        log(f"Error reading JSON file: {e}", ERROR)
        raise


def read_users_from_json(filters: AccountFilter = None) -> List[User]:
    try:
        final_users = []

        with open(accounts_path, "r", encoding="utf-8") as file:
            users = json.load(file)

        if filters:
            filtered_data = {
                k: v for k, v in filters.model_dump().items() if v is not None
            }

            for user in users:
                if all(user.get(k) == v for k, v in filtered_data.items()):
                    final_users.append(User(**user))
        else:
            final_users = [User(**user) for user in users]
        return final_users
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        log(f"Error: The file '{accounts_path}' is not a valid JSON.", ERROR)
        raise
    except Exception as e:
        log(f"Error reading JSON file: {e}", ERROR)
        raise


def write_users_to_json(users: List[User]):
    with open(accounts_path, "w") as file:
        json.dump([user.model_dump() for user in users], file, indent=4)


def upsert_user(user: User):
    try:
        users = read_users_from_json()
        user_found = False

        for i, existing_user in enumerate(users):
            if existing_user.username == user.username:
                users[i] = user
                user_found = True
                break

        if not user_found:
            users.append(user)

        write_users_to_json(users)
        action = "mis à jour 🔄" if user_found else "généré ✅"
        log(f"Le compte {user.username} a été {action}.")

    except Exception as e:
        log(f"Error inserting/updating user: {e}", ERROR)
        raise
