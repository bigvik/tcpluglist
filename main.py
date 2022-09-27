from bs4 import BeautifulSoup
from flask import Flask
from flask import render_template
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Parser:
    def __init__(self):
        self.info = []
        self.uri = [
            'http://wincmd.ru/directory/fsplugin.html',
            'http://wincmd.ru/directory/lister.html',
            'http://wincmd.ru/directory/packer.html',
            'http://wincmd.ru/directory/content.html'
        ]
        logger.info('Init is OK')

    def get_html(self, uri):
        try:
            html = requests.get(uri)
            html.encoding = 'windows-1251'
        except:
            logger.error(uri)
            return False
        logger.info(f'Из {uri} ({len(html.text)}):')
        return html.text

    def get_description(self, uri):
        description = []
        download = []
        html = self.get_html(uri)
        if html:
            bs = BeautifulSoup(html, 'lxml')
            p = bs.find('p', class_='opis')
            p_next = p.find_next('p', class_='opis')
            description.append(p.text)
            for child in range(len(p_next.contents)):
                if child in [2, 6, 11, 15, 19, 23]:
                    description.append(p_next.contents[child])
            for li in bs.find_all('li'):
                try:
                    download.append(li.find('a'))
                except:
                    continue
            description.append(download)
            logger.info('   - получено описание')
            return description
        else:
            return False

    def get_download(self, link):
        download = []
        soup = BeautifulSoup(self.get_html(link), 'lxml')
        for li in soup.find_all('li'):
            try:
                download.append(li.find('a'))
            except:
                continue
        logger.info(f'  получено  {len(download)} ссыл(ка/ок)')
        return download

    def parse(self):
        for x in range(4):
            soup = BeautifulSoup(self.get_html(self.uri[x]), 'lxml')
            names = soup.find_all('h3', class_='name')

            for y in range(len(names)):
                link = names[y].find('a').attrs['href']
                desc = self.get_description(link)
                if desc:
                    self.info.append([names[y].text, link]+desc)
                else:
                    continue
                #logger.info([names[y].text, names[y].find('a').attrs['href']])
            logger.info(f'@@@   - получили {len(names)} плагин(а/ов)')


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html', title='Таблица плагинов Total Commander`a', body=plugins.info)


if __name__ == '__main__':
    plugins = Parser()
    plugins.parse()
    app.run()
