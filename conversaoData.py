from datetime import datetime

def converterData(data, date_interval):
    intervalo = date_interval.split('-')
    data = data.strip()
    
    try:
        data = datetime.strptime(data, '%B %d, %Y')
        data = data.strftime('%d/%m/%Y')

    except ValueError:
        items_data = data.split('/')
        for i in range(0, len(items_data)):
            if len(items_data[i]) == 1:
                items_data[i] = '0' + items_data[i]
                
        data = f'{items_data[1]}/{items_data[0]}/20{items_data[2]} '

    # Atualizando data do post formatada
    #data = datetime.strptime(data, '%m %d, %Y')
     
    if len(intervalo) > 2 or len(intervalo) < 1:
        print("Warning: Intervalo de data mal formatado, não será aplicado.")
        filtro = True
    else:
        try:
            if len(intervalo) == 2 and intervalo[1].strip() is not '':
                minimo = [int(x) for x in intervalo[0].strip().split('/')]
                maximo = [int(x) for x in intervalo[1].strip().split('/')]
                data_artigo = [int(x) for x in data.strip().split('/')]

                if (data_artigo[0] >= minimo[0] and data_artigo[1] >= minimo[1] and data_artigo[2] >= minimo[2]) \
                and (data_artigo[0] <= maximo[0] and data_artigo[1] <= maximo[1] and data_artigo[2] <= maximo[2]):
                    filtro = True
                else:
                    filtro = False

            if len(intervalo) == 1 or (len(intervalo) == 2 and intervalo[1].strip() == ''):
                minimo = [int(x) for x in intervalo[0].strip().split('/')]
                data_artigo = [int(x) for x in data.strip().split('/')]

                if (data_artigo[0] >= minimo[0] and data_artigo[1] >= minimo[1] and data_artigo[2] >= minimo[2]):
                    filtro = True
                else:
                    filtro = False
        except IndexError:
            print("Warning: Intervalo de data mal formatado, não será aplicado.")
            filtro = True

    return data, filtro

'''# --------------- Teste

novaData, booleano = converterData('May 12, 2020', "01/06/2020")
print(novaData, booleano)
print(type(novaData))'''