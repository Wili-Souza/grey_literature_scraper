from bs4 import BeautifulSoup
import requests
import pandas as pd

#  ---- Minhas funções e classes
from conversaoData import converterData
from search import searchScrum
from exportar import exportar_df

data = { # -> diciionário para data frame 
    'tipo': [],
    'titulo': [],
    'link': [],
    'data': [],
    'descricao': []
}

def scrum_scraper(s_nome, s_tag, s_tipo, firstPg, lastPg):

    #intervalo de págs que deseja raspar
    firstPage = firstPg
    lastPage = lastPg

    #filtrar -> searchScrum(s_nome, s_tag, s_tipo)
    #Tratamento de parâmetros
    params = []
    if isinstance(s_nome, str) and s_nome is not None:
        params.append(s_nome)
    if isinstance(s_tag, str) and s_tag is not None:
        params.append(s_tag)
    if isinstance(s_tipo, str) and s_tipo is not None:
        params.append(s_tipo)
    
    search = searchScrum(*params)

    break_next = False

    for page in range(firstPage, lastPage):

        try:
            html = requests.get('https://www.scrum.org/resources?{}trainer_only_enable=0&page={}' .format(search, str(page)))
            soup = BeautifulSoup(html.text, 'html.parser')
        except:
            print('Erro ao conectar-se com o servidor')
            break


            #Conferindo se a página existe -> (no scrum n dá erro, ent precisa conferir):
        try:
            link_pag_atual = soup.find('li', 'pager__item is-active').find('a').get('href')
            print('page='+str(page))
            if ('page='+str(page)) not in str(link_pag_atual):
                break

        except: #Se não existir 'pager__item is-active', só executa essa vez
            break_next = True


                        #Análise Scrum.org

        #Por poster encontrado na página:
        for poster in soup.select('.list-view-item'):
                #Recebemos o tipo    
            tipo_poster = poster.select_one('.list-view-item-type')
                #Tratamento
            if tipo_poster == None: #Caso o tipo não exista
                tipo_poster = ''
            else:
                tipo_poster = tipo_poster.text.strip()

                #Recebemos o título
            titulo_poster_tag = poster.select_one('.list-view-item-title')
            if titulo_poster_tag == None:
                titulo_poster = ''
            else:
                titulo_poster = titulo_poster_tag.text.strip()

            #Recebendo o href do titulo -> tranformar no link completo
            href = titulo_poster_tag.get('href')
            if href == None:
                link_poster = ''
            else:
                link_poster = 'https://www.scrum.org' + str(href)

            #Recebendo data
            data_poster = poster.select_one('.list-view-item-date')
            if data_poster == None:
                data_poster = ''
            else:
                data_poster = converterData(data_poster.text)

            #Recebendo a descrição    
            descricao_poster = poster.select_one('.list-view-item-teaser')
            if descricao_poster == None:
                descricao_poster = ''
            else:
                descricao_poster = descricao_poster.text.strip()
            

                #Salvando no dicionario do dataframe
            data['tipo'].append(tipo_poster)
            data['titulo'].append(titulo_poster)
            data['link'].append(link_poster)
            data['data'].append(data_poster)
            data['descricao'].append(descricao_poster)

        if break_next:
            break

    '''if len(data['titulo']) > 0: #se algum resultado for capturado

            # ---- Salvando resultado
        df = pd.DataFrame(data, columns = ['tipo', 'titulo', 'link', 'data', 'descricao']) #-> criando dataframe

            # ---- Exportando para excel(xlsx) e/ou csv
        excel_file, csv_file = exportar_df(df, 'xlsx', 'csv', wb='S')'''

    print('FIM DA EXECUÇÃO')

    return data
    