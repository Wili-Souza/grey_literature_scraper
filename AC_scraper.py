from bs4 import BeautifulSoup
import requests
import pandas as pd

#  ---- Minhas funções e classes
from search import searchScrum
from exportar import exportar_df
from AC_scraper_mod.searching_mod import scr_search_page
from AC_scraper_mod.regular_mod import scr_page
from AC_scraper_mod.presentations_mod import scr_presentations_page

data = { # -> diciionário para data frame
    'tipo': [],
    'titulo': [],
    'link': [],
    'data': [],
    'descricao': [],
    'autor': []
}

selectors = {
    'title':'td.views-field.views-field-title',
    'autor':'div.field-name-user-row',
    'date':'div.field-post-date',
    'teaser':'td.views-field.views-field-title'
}

def agileConnection_scraper(s_articles, s_magazine, s_presentations, s_interviews, s_white_papers, first_pgs, last_pgs):
    #busca persoalizada: 
    # articles | better software magazine | conference presentations| 
    # interviews and videos | white papers and download
    search = [s_articles, s_magazine, s_presentations, s_interviews, s_white_papers]

    #intervalo de págs que deseja raspar
    first_pages = first_pgs
    last_pages = last_pgs

    search_index = -1

        #Conectando com a página
    try:
        html = requests.get('https://www.agileconnection.com/')
        soup = BeautifulSoup(html.text, 'html.parser')
    except:
        print('Erro ao conectar-se com o servidor')

                    #Análise agileconnection.com

    #Raspando links de cada tipo de fontes (resources)
    for fonte in soup.find('div', {'id': 'tb-megamenu-column-2'}).find('ul').find_all('li'):
        url = 'https://www.agileconnection.com' + fonte.find('a').get('href')

            # --- Tratamento da string de busca
        search_index += 1
        txt_search = search[search_index]
        searching = False

        #intervalo de pag da categoria:
        firstPage = first_pages[search_index]
        lastPage = last_pages[search_index]

        #setando parâmetro de pesquisa
        if len(txt_search.strip()) > 0:
            url = url.replace('resources', 'search')
            url += f'?title={txt_search}'
            searching = True

        #setando intervalo (página inicial)
        if firstPage > 0:
            pag = url + f'?page={firstPage}'
        else:
            pag = url  #primeira página será a página inicial

            # --- Conectando com a página da fonte (resources)
        try:
            #print('A URL EM TEORIA  --->>> ', pag)
            html = requests.get(pag)
            soup = BeautifulSoup(html.text, 'html.parser')
        except:
            print(f'Erro 1 ao conectar-se com {pag}')
            continue

            # --- Raspando as páginas
        if searching:
            scr_search_page(soup, lastPage, data, search_index)
        
        elif search_index == 2:
            scr_presentations_page(soup, lastPage, data)
            
        elif search_index == 4:
            #scr_paper_page(soup, lastPage, data)
            scr_page(soup, lastPage, selectors, data, search_index)

        else:
            scr_page(soup, lastPage, selectors, data, search_index)
            


    '''if len(data['titulo']) > 0: #se algum resultado for capturado

            # ---- Salvando resultado
        df = pd.DataFrame(data, columns = ['tipo', 'titulo', 'link', 'autor', 'data', 'descricao']) #-> criando dataframe

            # ---- Exportando para excel(xlsx) e/ou csv
        excel_file, csv_file = exportar_df(df, 'xlsx', 'csv', wb='AC')

    print('FIM DA EXECUÇÃO')'''

    return data
   