import requests
import csv
import time
from bs4 import BeautifulSoup

# Коды провинций Китая
province_data = [
    {"code": "11:1000", "name": "Beijing"},
    {"code": "12:1000", "name": "Tianjin"},
    {"code": "13:1000", "name": "Hebei"},
    {"code": "14:1000", "name": "Shanxi"},
    {"code": "15:1000", "name": "Inner Mongolia"},
    {"code": "21:1000", "name": "Liaoning"},
    {"code": "22:1000", "name": "Jilin"},
    {"code": "23:1000", "name": "Heilongjiang"},
    {"code": "31:1000", "name": "Shanghai"},
    {"code": "32:1000", "name": "Jiangsu"},
    {"code": "33:1000", "name": "Zhejiang"},
    {"code": "34:1000", "name": "Anhui"},
    {"code": "35:1000", "name": "Fujian"},
    {"code": "36:1000", "name": "Jiangxi"},
    {"code": "37:1000", "name": "Shandong"},
    {"code": "41:1000", "name": "Henan"},
    {"code": "42:1000", "name": "Hubei"},
    {"code": "43:1000", "name": "Hunan"},
    {"code": "44:1000", "name": "Guangdong"},
    {"code": "45:1000", "name": "Guangxi"},
    {"code": "46:1000", "name": "Hainan"},
    {"code": "51:1000", "name": "Sichuan"},
    {"code": "52:1000", "name": "Guizhou"},
    {"code": "53:1000", "name": "Yunnan"},
    {"code": "54:1000", "name": "Tibet"},
    {"code": "61:1000", "name": "Shaanxi"},
    {"code": "62:1000", "name": "Gansu"},
    {"code": "63:1000", "name": "Qinghai"},
    {"code": "64:1000", "name": "Ningxia"},
    {"code": "65:1000", "name": "Xinjiang"},
    {"code": "71:1000", "name": "Taiwan"},
    {"code": "81:1000", "name": "Hong Kong"},
    {"code": "82:1000", "name": "Macao"},
    {"code": "50:1000", "name": "Chongqing"}
]

# Ключевые слова для скрэпинга
with open('keywords.txt', 'r', encoding='utf-8') as f:
    keywords = [line.strip() for line in f if line.strip()]
# URL для поиска в Weibo (десктопная версия)
base_url = "https://s.weibo.com/weibo"

# Заголовки для имитации браузерного запроса
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": "ALF=1746289158; SCF=Ag7OtO7dhiaabrSoHlLz_nEfstLeBgTI4nY6xz9MfInvliBwLL1XcizDiiL80NXJS_sG4Qb4BCmNxcpjDc6cb60.; SUB=_2A25K6sVWDeRhGeFH41oV9yzOzTqIHXVphlierDV8PUJbkNANLUT-kW1NejMfq1ioxbY39PEItSIsvNvmInnl9Pnw; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFNdnyUBpu8HvNjcYBKXMh15JpX5KMhUgL.FoM41hnXS0zESoq2dJLoIEQLxKqL1heLBoeLxKqL1-eL1h.LxK-LB--L1-BLxKML1-qLBoSXUPiXds-t; WBPSESS=dcPDDyYPzIPBJqki5xJyV0wNKTbkUzWyKoOGugK4xY3Me3OjAu83NvoukMPipRA7DC03pe9tLQsM_FiZBA1o_cBpeh-_4Quc08R_YBaweA2TbYZ6BS5dTABZLSpLmmED"
    # cookie от Weibo, полученные при регистрации на платформе
}

# Инициализация CSV файла с заголовками
with open('weibo-scraping.csv', 'w', newline='', encoding='utf-8-sig') as file:
    writer = csv.writer(file)
    writer.writerow(["Geotag", "Time", "Content", "Reposts", "Comments", "Likes", "Keyword"])

# Множество для отслеживания уже обработанных постов (чтобы избежать дубликатов)
seen_posts = set()


# Функция для обработки одного поста
def process_post(post, keyword, province_name):
    try:
        # Извлекаем ID поста
        post_id = post.get('mid')  # Уникальный ID поста
        if post_id in seen_posts:
            print(f"Обнаружен дубликат поста: {post_id}")
            return
        seen_posts.add(post_id)

        # Проверяем, является ли аккаунт верифицированным - верифицированные аккаунты являются представителями частных организаций.
        verified_account = post.find('span', title="微博官方认证")  # Ищем значок верификации
        if verified_account:
            print(f"Пропускаем пост от верифицированного аккаунта: {post_id}")
            return

        # Извлекаем время публикации
        post_time_elem = post.find('div', class_='from').find('a')
        post_time = post_time_elem.text.strip() if post_time_elem else 'Unknown'

        # Извлекаем содержание поста
        content_elem = post.find('p', class_='txt')
        content = content_elem.text.strip() if content_elem else 'No Content'

        # Извлекаем метрики вовлеченности (репосты, комментарии, лайки)
        engagement_metrics = post.find('div', class_='card-act').find_all('li')
        reposts = engagement_metrics[1].text.strip() if len(engagement_metrics) > 1 else '0'
        comments = engagement_metrics[2].text.strip() if len(engagement_metrics) > 2 else '0'
        likes = engagement_metrics[3].text.strip() if len(engagement_metrics) > 3 else '0'

        # Сохраняем данные в CSV-файл
        with open('weibo-scraping.csv', 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow([province_name, post_time, content, reposts, comments, likes, keyword])

        print(f"Собран пост из {province_name} от {post_time}: {content[:50]}...")

    except Exception as e:
        print(f"Ошибка при обработке поста: {e}")


# Функция для скрапинга одной страницы
def scrape_page(keyword, page, year, region_code, province_name):
    try:
        # Определяем диапазон дат для года
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"

        # Параметры для поискового запроса
        params = {
            "q": keyword,
            "typeall": 1,
            "suball": 1,
            "timescope": f"custom:{start_date}:{end_date}",
            "page": page,
            "region": f"custom:{region_code}"
        }

        # Отправляем запрос
        response = requests.get(base_url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Не удалось получить страницу {page} для {province_name}. Код статуса: {response.status_code}")
            return False

        # Парсим HTML-ответ
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем все посты на странице
        posts = soup.find_all('div', class_='card-wrap')
        if not posts:
            print(f"На странице {page} для {province_name} постов не найдено.")
            return False

        # Обрабатываем каждый пост
        for post in posts:
            process_post(post, keyword, province_name)

        # Проверяем наличие следующей страницы
        next_page = soup.find('a', class_='next')
        if not next_page:
            print(f"Больше страниц не найдено для ключевого слова: {keyword} в {province_name}")
            return False

        return True

    except Exception as e:
        print(f"Ошибка при скрапинге страницы {page} для {province_name}: {e}")
        return False


# Основной цикл скрапинга
for province in province_data:
    region_code = province["code"].split(":")[0]  # Извлекаем код до ":1000"
    province_name = province["name"]
    print(f"\nНачинаем сбор данных для {province_name} (код: {region_code})")

    for keyword in keywords:
        print(f"\nИщем по ключевому слову: {keyword}")
        for year in range(2021, 2025):  # С 2021 по 2024 год
            print(f"Год: {year}")
            page = 1
            while page <= 50:  # На одно ключевое слово нельзя проматывать более 50 страниц
                print(f"Страница: {page}")
                success = scrape_page(keyword, page, year, region_code, province_name)
                if not success:
                    break
                page += 1
                time.sleep(5)  # Задержка для избежания блокировки