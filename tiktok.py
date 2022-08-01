from playwright.sync_api import sync_playwright, Page
from random import randint
import pandas as pd
from tkinter.filedialog import askopenfilename


def prepare_date():
    filename = askopenfilename()
    with open(filename, 'r') as file:
        urls = file.read().split('\n')
    urls = list(filter(lambda row: row != '0' and row != '', urls))
    return urls
    

def parsing(urls):
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch() # headless=False чтоб отобразить браузер
        page = browser.new_page() 
        for url in urls:
            try:
                page.goto(url)
                page.wait_for_timeout(randint(700,1800)) # задержка в миллисекундах
                followers = page.query_selector('//strong[@data-e2e="followers-count"]')
                likes = page.query_selector('//strong[@data-e2e="likes-count"]')
                data.append([url, followers.inner_text(), likes.inner_text()])
            except Exception as e:
                data.append([url, False, False])
        browser.close()
    data = pd.DataFrame(columns=['nickname', 'followers', 'likes'], data=data)
    data['followers'] = data['followers'].apply(check_thousands)
    data['likes'] = data['likes'].apply(check_thousands)
    data.to_csv('followers.csv', index=False, sep='\t')
   

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
    urls = prepare_date()
    parsing(urls)