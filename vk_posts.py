import vk_api
import re

# Функция для получения списка репостов пользователя
def get_reposts(vk, user_id):
    repost_links = []

    try:
        # Получаем посты со стены пользователя
        response = vk.wall.get(owner_id=user_id, count=100)  # Максимум 100 постов за раз
        posts = response['items']

        # Проходим по постам и проверяем, есть ли репосты
        for post in posts:
            if 'copy_history' in post:  # Если есть репост
                for repost in post['copy_history']:
                    # Проверка на существование оригинального поста
                    try:
                        # Получаем подробную информацию об оригинальном посте
                        vk.wall.getById(posts=[f"{repost['owner_id']}_{repost['id']}"])
                        original_post_link = f"https://vk.com/wall{repost['owner_id']}_{repost['id']}"
                        repost_links.append(original_post_link)
                        print(f"Найден репост: {original_post_link}")
                    except vk_api.VkApiError as e:
                        print(f"Ошибка при получении оригинального поста: {e}. Пропускаем пост.")
                        continue  # Пропускаем удаленные посты

    except vk_api.VkApiError as e:
        print(f"Ошибка при получении репостов: {e}")
    
    return repost_links

# Основной скрипт
def main():
    # Токен доступа
    token = "vk1.a.r6u6VQJwtyswpQEeAb1BLQkqg0GL3MkyIUUiRC2G6xixk8wUnywowQW3zv80hBB9mBIdEypKVTmS0Ew-ZAbcYnVDahwG3B4vL8HYY3hK90zuZdqU8-JTxu4DI7Dx0fmEX_nN9BhvkOvJib4ivs651zl9WCGkKOp2EZKA56hs8K0x5FkY3S4YuXWjgepJCzgoB3n5dcTWsfU1fgJqihexYg"
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    # Проверка подключения
    try:
        user_info = vk.users.get()[0]
        print(f"Подключение успешно, это ваш пользователь: {user_info['first_name']} {user_info['last_name']}")
    except vk_api.VkApiError as e:
        print(f"Ошибка при подключении к API ВКонтакте: {e}")
        return

    # Чтение ссылок на пользователей из файла "user_links.txt"
    with open("user_links.txt", "r") as file:
        user_links = file.readlines()

    # Для каждого пользователя собираем репосты
    for user_url in user_links:
        user_url = user_url.strip()
        
        # Извлекаем ID пользователя из ссылки
        match = re.search(r"vk.com/((id\d+)|([a-zA-Z0-9_]+))", user_url)
        if match:
            user_id = match.group(1)
            print(f"\nСобираем репосты для пользователя с ID: {user_id}")
            
            # Получаем репосты
            repost_links = get_reposts(vk, user_id)

            # Записываем ссылки на оригинальные посты в файл
            if repost_links:
                with open("reposts.txt", "a") as file:
                    for link in repost_links:
                        file.write(f"{link}\n")
                print(f"\nСсылки на репосты для пользователя {user_id} записаны в файл 'reposts.txt'.")
            else:
                print(f"\nДля пользователя {user_id} не найдено репостов.")
        else:
            print(f"Неверная ссылка на пользователя: {user_url}")

if __name__ == "__main__":
    main()
