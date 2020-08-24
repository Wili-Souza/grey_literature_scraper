from datetime import datetime

def converterData(data):

    data = data.strip()

    '''if 'January' in data:
        data = data.replace('January', '01')
    elif 'February' in data:
        data = data.replace('February', '02')
    elif 'March' in data:
        data = data.replace('March', '03')
    elif 'April' in data:
        data = data.replace('April', '04')
    elif 'May' in data:
        data = data.replace('May', '05')
    elif 'June' in data:
        data = data.replace('June', '06')
    elif 'July' in data:
        data = data.replace('July', '07')
    elif 'August' in data:
        data = data.replace('August', '08')
    elif 'September' in data:
        data = data.replace('September', '09')
    elif 'October' in data:
        data = data.replace('October', '10')
    elif 'November' in data:
        data = data.replace('November', '11')
    elif 'December' in data:
        data = data.replace('December', '12')'''
    
    try:
        data = datetime.strptime(data, '%B %d, %Y')
        data = data.strftime('%d/%m/%Y')

    except ValueError:
        items_data = data.split('/')
        for i in range(0, len(items_data)):
            if len(items_data[i]) == 1:
                items_data[i] = '0' + items_data[i]
                
        data = f'{items_data[1]}/{items_data[0]}/20{items_data[2]} '

    #data = datetime.strptime(data, '%m %d, %Y')

    
    return data

''' # --------------- Teste

novaData = converterData('May 12, 2020')
print(novaData)
print(type(novaData))'''