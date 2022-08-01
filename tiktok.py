from playwright.sync_api import sync_playwright, Page
from random import randint
from tqdm import tqdm
from time import perf_counter
import pandas as pd


# url для примера
URLS = [
    '@rad.miru',
    '@f.lauraegiulia_',
    '@kozah033987',
    '@ttfdcz',
    '@ananmart9'
]

def main():
    start = perf_counter()
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch() # headless=False чтоб отобразить браузер
        page = browser.new_page() 
        for url in tqdm(URLS):
            try:
                page.goto(f'https://www.tiktok.com/{url}')
                page.wait_for_timeout(randint(700,1800)) # задержка в миллисекундах
                followers = page.query_selector('//strong[@data-e2e="followers-count"]')
                data.append([url, followers.inner_text()])
            except Exception as e:
                data.append([url, False])
                print(url, ' - ', e)
        browser.close()
    end = perf_counter()
    data = pd.DataFrame(columns=['nickname', 'followers'], data=data)
    data['followers'] = data['followers'].apply(check_thousands)
    data.to_csv('followers.csv', index=False)
    print(f'Время работы скрипта - {end - start:.2f} сек')
   

def check_thousands(row: str):
    '''Функция для приведения в порядок кол-во подписчиков
    31.3М -> 31300000
    1.2K -> 1200
    '''
    if not row:
        return
    if '.' in row:
        row = row.replace('.', '').replace('K', '00').replace('M', '00000')
    else:
        row = row.replace('M', '000000').replace('K', '000')

    return int(row)


if __name__ == '__main__':
    main()
