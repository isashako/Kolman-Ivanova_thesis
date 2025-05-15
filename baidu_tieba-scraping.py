import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Загрузка клбчевых слов из текстового файла
def load_search_terms(filename='search_terms.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File {filename} not found")
        return []

# Сбор комментариев с поста
def scrape_comments(post_url):
    try:
        response = requests.get(post_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        comments = []
        for comment in soup.find_all('div', class_='l_post'):
            content = comment.find('div', class_='d_post_content')
            if not content:
                continue

            comment_data = {
                'Content': content.text.strip(),
                'Time': None,
                'Geotag': None,
                'post_url': post_url
            }

            post_tail = comment.find('div', class_='post-tail-wrap')
            if post_tail:
                location = post_tail.find('span', text=lambda x: x and 'IP属地:' in x)
                if location:
                    comment_data['Geotag'] = location.text.replace('IP属地:', '').strip()

                time_span = post_tail.find_all('span', class_='tail-info')[-1]
                if time_span:
                    comment_data['Time'] = time_span.text.strip()

            comments.append(comment_data)

        return comments

    except Exception as e:
        print(f"Error processing post {post_url}")
        return None

# Поиск по ключевому слову
def search_posts(search_term):
    try:
        response = requests.get(
            "https://tieba.baidu.com/f/search/res",
            params={'ie': 'utf-8', 'qw': search_term},
            timeout=10
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        return list({
            f"https://tieba.baidu.com{link['href']}"
            for link in soup.find_all('a', class_='bluelink')
            if link.get('href', '').startswith('/p/')
        })

    except Exception as e:
        print(f"Error searching for '{search_term}'")
        return []

def main():
    search_terms = load_search_terms()
    if not search_terms:
        return

    all_comments = []

    for term in search_terms:
        print(f"Processing: '{term}'")

        post_links = search_posts(term)
        time.sleep(3)

        if not post_links:
            continue

        for url in post_links:
            comments = scrape_comments(url)
            time.sleep(2)

            if comments:
                all_comments.extend([{**c, 'Keyword': term} for c in comments])

    if all_comments:
        pd.DataFrame(all_comments).to_excel('baidu_tieba-scraping.xlsx', index=False)
        print(f"Completed. Saved {len(all_comments)} comments")
    else:
        print("No comments found")

if __name__ == "__main__":
    main()