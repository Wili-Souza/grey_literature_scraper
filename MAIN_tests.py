from bs4 import BeautifulSoup
import requests
import pandas as pd
from copy import deepcopy

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
        result[i] = result[i].replace('"waiting"', '').replace('waiting', '').replace('--', '').strip()
        result[i] = " ".join(result[i].split())
    
    return result

input_string = input('String: ')

result = tratamento_string(mark_operators(input_string))
result = clean_result(result)

print('\nResultado final: ', result)


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