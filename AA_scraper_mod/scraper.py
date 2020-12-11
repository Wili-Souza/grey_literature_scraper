from bs4 import BeautifulSoup
from AA_scraper_mod.postType import findType
from conversaoData import converterData

def scrap(driver, data, date_interval):
    #Atualiza o soup com o novo html (contento todos os posts carregados)
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except:
        print('Erro ao conectar-se com a nova página.')
        return -1

    # ---------- Scraping dos posts do Agile Alliance carregados
    posts = soup.select_one('ul.aa-search__results').find_all('li', 'wrap') #Pegando todos os posts
    print(len(posts))

    for post in posts:

            #Recebemos o tipo
        tipo_post, _type = findType(post)

            #Recebemos o título
        titulo_post = post.select_one('span.aa-result-card__name-content')
        if titulo_post == None:
            titulo_post = ''
        else:
            titulo_post = titulo_post.text.strip()
        #print(titulo_post)

        #Recebendo o href (faz uso do type, extraido em postType.py)
        try:
            href = post.select_one(f'a.aa-result-card.aa-result-card--{_type}').get('href')
            link_post = str(href)
        except AttributeError:
            link_post = ''

        try:
            autor_post = post.select_one('p.aa-result-card__meta').select_one('span')
            autor_post = autor_post.text.strip()
        except AttributeError:
            autor_post = ''
            

        #Recebendo data
        data_post = post.select_one('time.aa-result-card__created')
        if data_post == None:
            data_post = ''
            data_filtro = True
        else:
            data_post, data_filtro = converterData(data_post.text, date_interval)
            '''data_post = datetime.strptime(data_post.text, '%-m/%-d/%-y')
            data_post = data_post.strftime('%d/%m/%Y')'''

        if data_filtro == False:
            continue

        #Recebendo a descrição    
        descricao_post = post.select_one('span.aa-result-card__description-content')
        if descricao_post == None:
            descricao_post = ''
        else:
            descricao_post = descricao_post.text.strip()

            #Salvando no dicionario do dataframe
        data['tipo'].append(tipo_post)
        data['titulo'].append(titulo_post)
        data['link'].append(link_post)
        data['autor'].append(autor_post),
        data['data'].append(data_post)
        data['descricao'].append(descricao_post)
