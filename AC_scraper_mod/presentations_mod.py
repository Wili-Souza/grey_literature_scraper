from conversaoData import converterData
import requests
from bs4 import BeautifulSoup

#Meus imports
from AC_scraper_mod.regular_mod import scr_page

def scr_presentations_page(soup, lastPage, data, data_intervalo):
    num_events = 0
    class_selector_container = 'view view-conference-presentations view-id-conference_presentations view-display-id-conference_page tw-article-list view-dom-id-06a6053d96ef855f6524d2fc825e1f07'
    #class_selector_event = 'ds-1col taxonomy-term vocabulary-event-conference view-mode-token clearfix'
    
    for presentation in soup.select_one('div', {'class': class_selector_container}).find_all('div', 'more-link'):
        num_events += 1
        if num_events == 6: #O sexto elemento é intruso
            break

        selectors = {
            'title':'td.views-field.views-field-body',
            'autor':'div.user',
            'date':'div.field-post-date',
            'teaser':'td.views-field.views-field-body'
        }
        
        href = presentation.select_one('a').get('href')
        if 'https://' not in href and 'http://' not in href:
            if 'https/' not in href:
                url = 'https://www.agileconnection.com' + href
            else:
                url = href.replace("https/", "https://")
        

        try:
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
        except:
            print(f'Erro na conexão com {url}')
            continue

        scr_page(soup, lastPage, selectors, data, 2, data_intervalo)