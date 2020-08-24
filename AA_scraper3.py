from selenium import webdriver   ##Site dinamico -> Selenium
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from datetime import datetime

#  ---- Minhas funções e classes
from search import searchScrum
from exportar import exportar_df
from AA_scraper_mod.scraper import scrap

data = { # -> diciionário para data frame
    'tipo': [],
    'titulo': [],
    'link': [],
    'data': [],
    'descricao': [],
    'autor': []
}

def agileAlliance_scraper(types_received, lastPage, key_words):
    num_pag_scraped = 0
    finished = False

    # --------------- Conectando com o Selenium
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument("--headless")
    chromeOptions.add_argument('--disable-gpu')
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument("--disable-dev-shm-usage")
    chromeOptions.add_argument("--window-size=1920x1080")
    chromeOptions.add_argument("start-maximised")

    driver = webdriver.Chrome('chromedriver.exe', options=chromeOptions)

    #Conectando com a página usando o driver
    driver.get('https://www.agilealliance.org/resources')
    sleep(5) #Tempo de carregamento da página

    # Para filtragem de tipos da primeira página ->  ['tipo1', 'tipo1', ... ]
    # Para subpáginas com subtipos -> {'subpágina': ['Subtipo1', 'Subtipo2' ... ]}
    types_searched = [*types_received] 
    found = False

    for tp in types_searched:
        if isinstance(tp, dict):
            type_nav = driver.find_elements_by_class_name('aa-local-navigation__link')
            print('OPCOES ENCONTRADAS:   ', len(type_nav))

            for type_field in type_nav:
                    if type_field.text == list(tp.keys())[0]: #Pegando nome da key do primeiro elemento do dicionário (e unico)
                        driver.execute_script("arguments[0].click();", type_field) #Vai para a página do tipo requerido
                        found = True
                        break
            
            if not found:
                print('Página do tipo requerido não encontrada.')
            
            else:
                sleep(3) #carregando página

                if key_words != '':
                    search_field = driver.find_element_by_class_name('search-input__field') #Campo de pesquisa
                    search_field.send_keys(key_words) #Pesquisando 
                    sleep(3)

                type_label = driver.find_elements_by_class_name('aa-search-filters__checklist-item')
                
                for type_field in type_label:
                    if type_field.find_element_by_tag_name('span').text in tp[list(tp.keys())[0]]:
                        check_box_type = type_field.find_element_by_tag_name('input')
                        driver.execute_script("arguments[0].click();", check_box_type) #Ativa tipo requerido
                
                break

    if not found:
        if key_words != '':
            search_field = driver.find_element_by_class_name('search-input__field') #Campo de pesquisa
            search_field.send_keys(key_words) #Pesquisando 
            sleep(3)

        if len(types_searched) > 0:
            type_label = driver.find_elements_by_class_name('aa-search-filters__label')
            
            for type_field in type_label:
                if type_field.find_element_by_tag_name('span').text in types_searched:
                    check_box_type = type_field.find_element_by_tag_name('input')
                    driver.execute_script("arguments[0].click();", check_box_type) #Ativa tipo requerido

    sleep(3) #Tempo de carregamento da página

    try:
        pagination_div = driver.find_element_by_class_name('aa-search-pagination')
        test = driver.find_elements_by_class_name('aa-search-pagination__btn')[1]
    except:
        pagination_div = None

    # --------------- conexão BeautifulSoup através do driver
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    except:
        print('Erro ao conectar-se com o servidor')
        finished = True


    last_height = driver.execute_script("return document.body.scrollHeight")

    # ------- Carregando os posts
    if pagination_div is None:
        while not finished:
            num_pag_scraped += 1
            
            #intervalo de páginas
            if num_pag_scraped == lastPage:
                break

            print('---------- SCRAPED: ', num_pag_scraped)
                
            #Scroll down 
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight-1500);")
            #Espera carregar
            sleep(5)
            #Pega o novo comprimento da página
            new_height = driver.execute_script("return document.body.scrollHeight")

            seconds = 0
            while new_height == last_height: #Se for a mesma -> tenta novamente
                sleep(2)
                seconds += 2
                print(seconds)
                new_height = driver.execute_script("return document.body.scrollHeight")

                if seconds > 18: #Para pegar uma grande quantidade de páginas, alterar para 60, por causa da lentidão
                    finished = True
                    break

            last_height = new_height #Atualiza o último comprimento
        
        scrap(driver, data) #Faz o web-scraping

    else:
        while not finished and num_pag_scraped != lastPage:
            num_pag_scraped += 1
            scrap(driver, data) #Faz o web-scraping

            #Passando a página estática
            next_pag_btn = driver.find_elements_by_class_name('aa-search-pagination__btn')[1] #div do botão next
            if next_pag_btn.get_attribute('disabled'):
                finished = True
            else:
                next_pag = next_pag_btn.find_element_by_class_name('fa-angle-right')
                driver.execute_script("arguments[0].click();", next_pag)
                sleep(3)


    #Encerra o driver
    driver.quit()


    '''if len(data['titulo']) > 0: #se algum resultado for capturado

            # ---- Salvando resultado
        df = pd.DataFrame(data, columns = ['tipo', 'titulo', 'link', 'autor', 'data', 'descricao']) #-> criando dataframe

            # ---- Exportando para excel(xlsx) e/ou csv
        excel_file, csv_file = exportar_df(df, 'xlsx', 'csv', wb='AA')

    print('FIM DA EXECUÇÃO')'''

    return data
   