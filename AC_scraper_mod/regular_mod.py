from conversaoData import converterData
import requests
from bs4 import BeautifulSoup

from AC_scraper_mod.types import type_by_index

def scr_page(soup, lastPage, selec, data, search_index, data_intervalo):
    page_exist = True
    num_pag = 0

    tipo_post = type_by_index(search_index)

    while page_exist:

        #Por poster encontrado na página:
        num_posts = 0 
        for post in soup.select_one('div', {'id': 'content'}).find_all('tr'):

            #Recebendo o título
            try:
                titulo_post_tag = post.select_one(selec['title']).select_one('a')
                print('PASSOU', titulo_post_tag.text.strip())

                if search_index != 4:
                    titulo_post = titulo_post_tag.text.strip()
                else:
                    list_titulo_post_tag = titulo_post_tag.text.split('|')

                    if len(list_titulo_post_tag) == 2:
                        titulo_post, autor_post = list_titulo_post_tag
                    else:
                        titulo_post, autor_post = [list_titulo_post_tag[0], ' ']

            except:
                break

            #Recebendo o href do titulo -> tranformar no link completo
            href = titulo_post_tag.get('href')
            if href == None:
                link_post = ''
            else:
                link_post = str(href)
                if 'http://' not in link_post and 'https://' not in link_post:
                    if 'https/' not in link_post:
                        link_post = 'https://www.agileconnection.com' + link_post
                    else:
                        link_post.replace("https/", "https://")
            
            #Recebendo autor
            if search_index != 4:
                autor_post = post.select_one(selec['autor'])
                try:
                    autor_post = autor_post.select_one('a.username').text.strip() #Raise error????
                    if autor_post == None:
                        raise Exception
                except:
                    autor_post = autor_post.text.strip()   

            if autor_post == None:
                autor_post = ''

            #Recebendo data
            data_post = post.select_one(selec['date'])
            if data_post == None:
                data_post = ''
                data_filtro = True
            else:
                data_post, data_filtro = converterData(data_post.text, data_intervalo)
            
            if data_filtro == False:
                continue

            #Recebendo a descrição    
            descricao_post = post.select_one(selec['teaser']).select_one('p')
            if descricao_post == None:
                descricao_post = ''
            else:
                descricao_post = descricao_post.text.strip()
    

                #Salvando no dicionario do dataframe
            data['tipo'].append(tipo_post)
            data['titulo'].append(titulo_post)
            data['link'].append(link_post)
            data['autor'].append(autor_post)
            data['data'].append(data_post)
            data['descricao'].append(descricao_post)

            num_posts += 1
            if search_index != 4:
                if num_posts >= 10:
                    break
            else:
                if num_posts >= len(soup.select_one('div', {'id': 'content'}).find_all('tr')) - 14: #Sempre há 14 elementos do intrusos
                    break

            #Checando se existe uma próxima página
        '''num_pag += 1
        if num_pag >= lastPage:
            break'''
        
        try:
            pag = 'https://www.agileconnection.com' + soup.select_one('li.pager-next').find('a').get('href')
        except:
            page_exist = False
            print('Próxima página não encontrada.')
            break
        
            #Conectando com a próxima página
        try:
            html = requests.get(pag)
            soup = BeautifulSoup(html.text, 'html.parser')
        except:
            print(f'Erro ao conectar-se com {pag}')
            break
        