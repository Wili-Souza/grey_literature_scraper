from bs4 import BeautifulSoup
import requests
import pandas as pd
from copy import deepcopy
from time import sleep

#--- Meus imports
from scrum_scraper import scrum_scraper as scrum
from AA_scraper3 import agileAlliance_scraper as agileAlliance
from AC_scraper import agileConnection_scraper as agileConnection
from exportar import exportar_df

scraped_data = { # -> diciionário para data frame 
    'tipo': [],
    'titulo': [],
    'link': [],
    'data': [],
    'descricao': [],
    'autor': []
}

def tratamento_string(string_atual, opened=False, closed=False, continuing=False, list_all_searches = []):
    print('chamou a função')
    idx = 0
    this_string = ''

    if string_atual[idx] != '(':
        for i in range(0, len(string_atual)):
            if string_atual[i] == '(':
                opened, opened_idx = True, i
                break
            if string_atual[i] == ')':
                closed, closed_idx = True, i
                break

            this_string += string_atual[i]
        
        string_atual = string_atual[i:]

        while '*AND' in this_string:
            print('entrando no while do AND')
            print(this_string)
            if this_string.strip().find('*AND') == 0:
                print('CONTINUING')
                continuing = True

            # ooo or uhuhu and ijijij
            and_idx = this_string.find('*AND')
            print('index primeiro AND', and_idx)
            
            #tratando o que há antes do and 
            if '*OR' in this_string[:and_idx]:
                aux_string = this_string[:and_idx].split('*OR')

                for i in range(0, len(aux_string) - 1):
                    if aux_string[i].strip() != '':
                        list_all_searches.append('"{} --"' .format(aux_string[i].strip()))
            
                list_all_searches.append('"{}" ' .format(aux_string[-1].strip()))
                idx_waiting = len(list_all_searches) - 1

                print(list_all_searches)

                #A parte antes do and já foi tratada:
                this_string = this_string[and_idx:]
                and_idx = 0 #novo and_idx
            else:
                if not continuing:
                    list_all_searches.append('"{}" ' .format(this_string[:and_idx].strip()))
                    idx_waiting = len(list_all_searches) - 1

            #Tratando o que há depois do and
            aux_string = this_string[and_idx+4:].strip()
            if '*OR' in aux_string or '*AND' in aux_string:
                print('Há um OR ou um AND')
                or_idx = aux_string.find('*OR')
                and_idx = aux_string.find('*AND')
                idx_op = or_idx if (or_idx < and_idx and or_idx > -1) or and_idx < 0 else and_idx
                print(aux_string, idx_op)

                #tirar aspas
                if continuing:
                    try:
                        list_all_searches[idx_waiting] = list_all_searches[idx_waiting] + ' '
                    except: #Caso da função recursiva com combinações
                        for i in range(0, len(list_all_searches)):
                            if 'waiting' in list_all_searches[i]:
                                list_all_searches[i] = list_all_searches[i] + ' '

                try:
                    list_all_searches[idx_waiting] += '"{}"' .format(aux_string[:idx_op].strip())
                except:
                    for i in range(0, len(list_all_searches)):
                            if 'waiting' in list_all_searches[i]:
                                list_all_searches[i] += '"{}"' .format(aux_string[:idx_op].strip())
                print(list_all_searches)
            else:
                idx_op = None
                print('Entrou, continuing --> ', continuing)
                if continuing:
                    try:
                        list_all_searches[idx_waiting] = list_all_searches[idx_waiting][:-1] + ' '
                        list_all_searches[idx_waiting] += '{}"' .format(aux_string.strip())

                    except: #Caso da função recursiva com combinações
                        for i in range(0, len(list_all_searches)):
                            if 'waiting' in list_all_searches[i]:
                                if aux_string.strip() != '':
                                    list_all_searches[i] = list_all_searches[i] + ' "' + aux_string.strip() + '"'
                
                else:
                    try:
                        if aux_string.strip() != '':
                            list_all_searches[idx_waiting] += '"{}"' .format(aux_string.strip())

                    except: #Caso da função recursiva com combinações - need testing
                        for i in range(0, len(list_all_searches)):
                            if 'waiting' in list_all_searches[i]:
                                list_all_searches[i] = list_all_searches[i][:-1] + ' ' + aux_string.strip()


                print(list_all_searches)
            
            if idx_op:
                this_string = aux_string[idx_op:].strip()
                print('--->>>', aux_string[idx_op:].strip())
            else:
                break

        if '*OR' in this_string:
            print('~~~ ', string_atual)
            if '*AND' in string_atual[0:4].strip():
                    for item in this_string.split('*OR'):
                        if item.strip() != '':
                            list_all_searches.append('"{}" waiting"' .format(item.strip()) )

            else:
                for item in this_string.split('*OR'):
                    if item.strip() != '':
                        list_all_searches.append('"{}"' .format(item.strip()) )
        
        if opened and not closed:
            print('Heyyyy 00000000')
            if '*AND' in this_string[-5:]:
                continuing = True

            if continuing:
                for k in range(len(list_all_searches) - 1, -1, -1):
                    print(list_all_searches[k], k)
                    if '--' in list_all_searches[k]:
                        break
                    else:
                        list_all_searches[k] = list_all_searches[k].replace('waiting','') +'waiting'
                
            
            print(list_all_searches)

            list_all_searches = tratamento_string(
                string_atual, 
                opened=True, 
                continuing=continuing,
                list_all_searches=list_all_searches
                )

        print('retornando ---->>' , list_all_searches)
        return list_all_searches
    
    else:
        for i in range(0, len(string_atual)):
            if string_atual[i] == '(':
                if i != 0:
                    opened, opened_idx = True, i
                    break
                else:
                    continue

            if string_atual[i] == ')':
                closed, closed_idx = True, i
                break
        
            this_string += string_atual[i]
        
        string_atual = string_atual[i+1:]

        if continuing:
            new_items = []
            print('recursivando C --->', this_string)
            if '*OR' in this_string.strip() or '*AND' in this_string.strip():
                parenthesis = tratamento_string(this_string, list_all_searches=list_all_searches) ##
            else:
                parenthesis = [*list_all_searches, f'"{this_string}"']

            print(parenthesis)

            print('ANtes d for recursivando C -->', list_all_searches)
            for i in range(0, len(list_all_searches)):
                if '--' in list_all_searches[i]:
                    new_items.append(list_all_searches[i].replace(' --', ''))
                
                elif 'waiting' in list_all_searches[i]:
                    print(list_all_searches[i])

                    for j in range(i, len(parenthesis)):
                        if 'waiting' not in parenthesis[j]:
                            new_items.append(f'{list_all_searches[i]} {parenthesis[j]}')
            
            list_all_searches = new_items
            print(list_all_searches)

            if string_atual.strip() != '':
                if '*AND' not in string_atual[0:5].strip():
                    for i in range(0, len(list_all_searches)):
                        list_all_searches[i] = list_all_searches[i].replace('waiting', '')
                
                print(string_atual, list_all_searches)

                list_all_searches = tratamento_string(
                    string_atual,  
                    list_all_searches=list_all_searches
                    )

        else:
            print('(???) recursivando --->', this_string)
            if '*OR' in this_string.strip() or '*AND' in this_string.strip():
                aux = [*list_all_searches] #estava pegando o endereço na memória
                parenthesis = tratamento_string(this_string, list_all_searches=list_all_searches)

                parenthesis = list(set(parenthesis).difference(aux))
                list_all_searches = list(set(list_all_searches).difference(parenthesis))
            else:
                parenthesis = [f'"{this_string}"']

            print('valores--', parenthesis, list_all_searches)

            for i in range(0, len(parenthesis)):
                print('rodando for', parenthesis[i])
                list_all_searches.append(f'{parenthesis[i][:-1]} waiting"')
            
            print('Depois do for', list_all_searches)

            if string_atual.strip() != '':
                if '*AND' not in string_atual[0:5].strip():
                    for i in range(0, len(list_all_searches)):
                        list_all_searches[i] = list_all_searches[i].replace('waiting', '')
                
                print(string_atual)
                list_all_searches = tratamento_string(
                    string_atual,  
                    list_all_searches=list_all_searches
                    )

    return list_all_searches 


def mark_operators(input_string):
    quotes_counter = 0
    waiting_other = False
    for i in range(0, len(input_string)):
        if input_string[i] == '"':
            waiting_other = False
            quotes_counter += 1
        
        if quotes_counter % 2 == 0 and not waiting_other:
            if input_string[i+2:i+4] == 'OR' or input_string[i+2:i+5] == 'AND':
                input_string = input_string[:i+2] + "*" + input_string[i+2:]
                i = i+4
                waiting_other = True

            elif input_string[i+3:i+5] == 'OR' or input_string[i+3:i+6] == 'AND': 
                input_string = input_string[:i+3] + "*" + input_string[i+3:]
                i = i + 5
                waiting_other = True

    return input_string.replace('"', '')

def clean_result(result):
    for i in range(0, len(result)):
        result[i] = result[i].replace('"waiting"', '').replace(' "waiting', '"').replace('waiting', '').replace('--', '').strip()

        result[i] = " ".join(result[i].split())
    
    return result

def get_key_words(result):
    #Pegando palavras chaves individuais
    key_words = []
    for item in result:
        key_words += [x.strip() for x in item.split('"') if x.strip() != '']

    return list(set(key_words))

def eliminate_duplicates(data):
    #Eliminando repetições de posts em data
    idx_duplicates = [i for i in range(0, len(data['titulo'])) if data['titulo'][i] in data['titulo'][i+1:]]
    for i in range(len(data['titulo']) - 1, -1, -1):
        if i in idx_duplicates:
            for key in data:
                del data[key][i]

    print(len(data['tipo']), len(data['titulo']), len(data['link']), \
            len(data['data']), len(data['descricao']))

def search_filter(data, AC=False):
    #---------  Fazendo scraping com base nas combinações encontradas
    for j in range(len(data['titulo']) -1, -1, -1): 
        print(j)
        validated = False
        content = ''

        #Pegando conteudo do post
        try:
            html = requests.get(data['link'][j])
            soup = BeautifulSoup(html.text, 'html.parser')
        except:
            print('Erro ao conectar-se com página do conteúdo, tentando novamente...')
            print('Link: {}' .format(data['link'][j]))
            break
            

        if AC:
            div_of_parag = soup.select_one('div.field-item.even')
            div_of_summary = soup.select_one('div.summary')
            if div_of_summary == None:
                div_of_summary = soup.select_one('div.field.field-name-body')

            if div_of_parag is not None:
                paragraphs = div_of_parag.find_all('p')
            if div_of_summary is not None:
                paragraphs += div_of_summary.find_all('p')

            if paragraphs is not None:
                for p in paragraphs:
                    content += p.text
        else:
            paragraphs = soup.find_all('p')

            if paragraphs is not None:
                for p in paragraphs:
                    content += p.text
        
        #Checando se o post possui alguma das combinações requeridas
        for item in result:
            valid_post = True
            item_elements = [x.strip() for x in item.split('"') if x.strip() != '']

            for i in range(0, len(item_elements)):
                if item_elements[i].lower() not in data['titulo'][j].lower() and \
                    item_elements[i].lower() not in content.lower():
                    valid_post = False
                    break

            if valid_post:
                validated = True
                break
        
        if not validated:
            for key in data:
                del data[key][j]

    print(len(data['tipo']), len(data['titulo']), len(data['link']), len(data['data']), \
            len(data['descricao']))

    return data

def search_on_scrum(result):
    key_words = get_key_words(result)
    scraped_data_scrum = deepcopy(scraped_data)

    #Pesquisando os resultados das palavras chaves individuais
    for key_word in key_words:
        if len(key_word.split()) >= 2:
            temp_dict = scrum(f'"{key_word}"', '', '', 0, 999, intervalo_data)

        else:
            temp_dict = scrum(key_word, '', '', 0, 999, intervalo_data)

        for key in scraped_data_scrum:
            if key == 'autor':
                scraped_data_scrum[key] = ['' for x in range(0, len(scraped_data_scrum['titulo']))]
                continue
            scraped_data_scrum[key] += temp_dict[key]

    print(len(scraped_data_scrum['tipo']), len(scraped_data_scrum['titulo']), len(scraped_data_scrum['link']), 
            len(scraped_data_scrum['data']), len(scraped_data_scrum['descricao']))

    eliminate_duplicates(scraped_data_scrum)

    scraped_data_scrum = search_filter(scraped_data_scrum)

    print('FIM DA EXECUÇÃO NO SCRUM ...')

    return scraped_data_scrum

def search_on_AA(result):
    key_words = get_key_words(result)
    scraped_data_AA = deepcopy(scraped_data)

    #Pesquisando os resultados das palavras chaves individuais
    for key_word in key_words:
        if len(key_word.split()) >= 2:
            temp_dict = agileAlliance([], 999, f'"{key_word}"', intervalo_data)
        else:
            temp_dict = agileAlliance([], 999, key_word, intervalo_data)

        for key in scraped_data_AA:
            scraped_data_AA[key] += temp_dict[key]

    print(len(scraped_data_AA['tipo']), len(scraped_data_AA['titulo']), len(scraped_data_AA['link']), 
            len(scraped_data_AA['data']), len(scraped_data_AA['descricao']), len(scraped_data_AA['autor']))

    eliminate_duplicates(scraped_data_AA)

    scraped_data_AA = search_filter(scraped_data_AA)

    print('FIM DA EXECUÇÃO NO AGILE ALLIANCE ...')

    return scraped_data_AA

def search_on_AC(result):
    key_words = get_key_words(result)
    scraped_data_AC = deepcopy(scraped_data)
    firstPages = [0, 0, 0, 0, 0]
    lastPages = [999, 999, 999, 999, 999]

    #Pesquisando os resultados das palavras chaves individuais
    for key_word in key_words:
        if len(key_word.split()) >= 2:
            temp_dict = agileConnection(f'"{key_word}"', f'"{key_word}"', f'"{key_word}"', f'"{key_word}"', \
                                        f'"{key_word}"', firstPages, lastPages, intervalo_data)
        else:
            temp_dict = agileConnection(key_word, key_word, key_word, key_word, key_word, firstPages, \
                                        lastPages, intervalo_data)

        for key in scraped_data_AC:
            scraped_data_AC[key] += temp_dict[key]

    print(len(scraped_data_AC['tipo']), len(scraped_data_AC['titulo']), len(scraped_data_AC['link']), 
            len(scraped_data_AC['data']), len(scraped_data_AC['descricao']), len(scraped_data_AC['autor']))

    eliminate_duplicates(scraped_data_AC)

    scraped_data_AC = search_filter(scraped_data_AC)

    print('FIM DA EXECUÇÃO NO AGILE CONNECTION ...')

    return scraped_data_AC

input_string = input('String: ')
intervalo_data = input('Intervalo de data (ex.: 1/12/2001-12/12/2012): ')

result = tratamento_string(mark_operators(input_string))
result = clean_result(result)

print('\nResultado final: ', result)


# --- Chamando funções de busca
scraped_data_AC = search_on_AC(result=result)
scraped_data_scrum = search_on_scrum(result=result)
scraped_data_AA = search_on_AA(result=result)


# --- Unindo resultados em um único dicionário
for key in scraped_data:
    scraped_data[key] += scraped_data_scrum[key] + scraped_data_AA[key] + scraped_data_AC[key]
    #scraped_data[key] += scraped_data_AA[key]

print(len(scraped_data['titulo']))
if len(scraped_data['titulo']) > 0: #se algum resultado for capturado

        # ---- Salvando resultado
    df = pd.DataFrame(scraped_data, columns = ['tipo', 'titulo', 'link', 'autor', 'data', 'descricao']) #-> criando dataframe

        # ---- Exportando para excel(xlsx) e/ou csv
    exportar_df(df, 'xlsx', 'csv', wb='AA')

print('FIM DA EXECUÇÃO')

# teste -->  ("Paper" OR "Sheet") AND ("Agile learning" OR "Machines")

''' Testados ------------------------------------
    "A" AND ("B" OR "C") AND "D" -> ['"A B D"', '"A C D"']
    "A" AND ("B" OR "C") OR "D" -> ['"A B"', '"A C"', '"D"']
    "A" AND ("B" OR "C") AND ("D") -> ['"A B D"', '"A C D"']
    "A" AND ("B" OR "C") AND "D" AND "F" -> ['"A B D F"', '"A C D F"']
    "A" AND ("B" OR "C") AND "D" OR "F" -> ['"A B D"', '"A C D"', '"F"']
    "A" OR "B" AND ("C" OR "D") -> ['"A"', '"B C"', '"B D"']
    "A" AND ("B" OR "C") AND ("D" AND "E") -> ['"A B D E"', '"A C D E"']
    "A" AND "B" OR "C" AND "D" -> ['"A B"', '"C D"']
    "A" AND ("B" OR "C") AND ("D" OR "E") AND "G" -> ['"A B D G"', '"A B E G"', '"A C D G"', '"A C E G"']
    "A" AND ("B" OR "C" OR "D") -> ['"A B"', '"A C"', '"A D"']

    "A" AND ("B" OR "C") OR ("D" OR "E") AND "G" -> ['"A C"', '"A B"', '"E G"', '"D G"']
    ("A") AND ("B" OR "C") AND ("D" OR "E") AND "G" -> ['"A B D G"', '"A B E G"', '"A C D G"', '"A C E G"']
    ("A" AND "B" OR "C") OR ("D" OR "E") AND "G" -> ['"C "', '"A B "', '"D G"', '"E G"']
'''