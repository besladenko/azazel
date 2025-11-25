import vk_api
import re
from collections import defaultdict

# Функция для авторизации и получения лайков
def get_likes(vk, post_id, owner_id):
    likes = []
    try:
        response = vk.likes.getList(type='post', owner_id=owner_id, item_id=post_id, filter='likes', count=1000)
        likes += response['items']
        while 'next_from' in response:
            response = vk.likes.getList(type='post', owner_id=owner_id, item_id=post_id, filter='likes', count=1000, start_from=response['next_from'])
            likes += response['items']
    except vk_api.VkApiError as e:
        print(f"Ошибка при получении лайков для поста {owner_id}_{post_id}: {e}")
    return likes

# Функция для сбора статистики по лайкам
def collect_likes(vk, post_links):
    user_likes_count = defaultdict(int)  # Количество лайков на каждом посте
    post_count = len(post_links)  # Общее количество постов

    # Словарь для хранения пользователей, которым нужно записать в файлы
    high_percentage_users_50 = []  # Для пользователей, поставивших лайк на 50% и более постов
    high_percentage_users_75 = []  # Для пользователей, поставивших лайк на 75% и более постов

    # Регулярное выражение для извлечения owner_id и post_id
    pattern = r'https://vk.com/wall(-?\d+)_(\d+)'

    for link in post_links:
        link = link.strip()

        match = re.match(pattern, link)
        if not match:
            print(f"Пропущена некорректная ссылка: {link}")
            continue

        # Извлекаем owner_id и post_id из ссылки
        owner_id = int(match.group(1))  # Первый захваченный блок - owner_id
        post_id = int(match.group(2))  # Второй захваченный блок - post_id

        # Получаем лайки для поста
        likes = get_likes(vk, post_id, owner_id)

        # Собираем пользователей, поставивших лайк на посте
        for user_id in likes:
            user_likes_count[user_id] += 1  # Увеличиваем количество лайков у пользователя

    # Проверяем пользователей и делим их на группы
    for user_id, count in user_likes_count.items():
        percentage = (count / post_count) * 100  # Процент лайков
        print(f"Пользователь {user_id} поставил лайки на {count} постах ({percentage:.2f}%)")  # Для отладки

        if percentage >= 40:
            high_percentage_users_75.append(f"https://vk.com/id{user_id}")
        elif percentage >= 50:
            high_percentage_users_50.append(f"https://vk.com/id{user_id}")

    return high_percentage_users_50, high_percentage_users_75

# Основной скрипт
def main():
    # Токен доступа
    token = "Сюда токен"
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    # Проверка подключения
    try:
        user_info = vk.users.get()[0]
        print(f"Подключение успешно, это ваш пользователь: {user_info['first_name']} {user_info['last_name']}")
    except vk_api.VkApiError as e:
        print(f"Ошибка при подключении к API ВКонтакте: {e}")
        return

    # Чтение ссылок из файла
    with open("links.txt", "r") as file:
        post_links = file.readlines()

    print(f"Обрабатывается {len(post_links)} постов.")  # Для отладки

    # Сбор статистики по лайкам
    high_percentage_users_50, high_percentage_users_75 = collect_likes(vk, post_links)

    # Запись пользователей с 50% лайков в файл "lol.txt"
    if high_percentage_users_50:
        with open("lol.txt", "a") as file:  # Используем 'a', чтобы добавлять данные
            for user_url in high_percentage_users_50:
                file.write(f"{user_url}\n")  # Записываем пользователей с 50% лайков
        print("\nПользователи с 50% лайков были записаны в lol.txt.")
    else:
        print("\nНе было найдено пользователей с 50% лайков.")

    # Запись пользователей с 75% и более лайков в файл "lol2.txt"
    if high_percentage_users_75:
        with open("lol2.txt", "a") as file:  # Используем 'a', чтобы добавлять данные
            for user_url in high_percentage_users_75:
                file.write(f"{user_url}\n")  # Записываем пользователей с 75% и более лайков
        print("\nПользователи с 75% лайков были записаны в lol2.txt.")
    else:
        print("\nНе было найдено пользователей с 75% лайков.")

    # Выводим информацию по лайкам
    print("\nПользователи с 50% лайков:")
    for user_url in high_percentage_users_50:
        print(user_url)

    print("\nПользователи с 75% лайков:")
    for user_url in high_percentage_users_75:
        print(user_url)

if __name__ == "__main__":
    main()
