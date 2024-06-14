import requests
from bs4 import BeautifulSoup
from time import sleep
import csv
import json

cookies = {
    'COSYSSessao': '',
}

response = requests.get(
    'https://isdb.cosys.co.mz/esura_isdb_v2/view/estudante/estudante_notas_exame.php',
    cookies=cookies,
)


print("Extraindo Anos letivos do sistema")
soup = BeautifulSoup(response.content, "html.parser")

select = soup.find(id='anolectivo')
options = select.find_all('option')

values = [option['value'] for option in options]


notas = {}

for ano_lectivo in values:
    print("Extraindo notas do Ano Lectivo: ", ano_lectivo)
    data = {
        'anolectivo': ano_lectivo,
    }

    response = requests.post(
        'https://isdb.cosys.co.mz/esura_isdb_v2/view/estudante/estudante_notas_exame.php',
        cookies=cookies,
        data=data,
    )

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', id='tabela')
    rows = table.find_all('tr')[1:] 
    
    for row in rows:
        cols = row.find_all('td')
        disciplina = cols[0].text.strip()
        semestre = cols[1].text.strip()
        media_final = cols[8].text.strip()
        
        if media_final:
            media_final = float(media_final)
            if media_final >= 10:
                if semestre not in notas: notas[semestre] = []
                
                notas[semestre].append((disciplina, media_final))    
    sleep(1)
    
semestres_ordenados = sorted(notas.keys(), key=int)


print("Gravando  notas num csv....")

with open('declaracao_notas.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    for semestre in semestres_ordenados:
        writer.writerow([f'{semestre}˚ Semestre'])
        writer.writerow(['Disciplina/Módulo', 'Media Final'])
        for item in notas[semestre]:
            writer.writerow([item[0], item[1]])
        writer.writerow([]) 

print("Gravando notas num arquivo JSON....")

with open('declaracao_notas.json', mode='w') as file:
    json.dump(notas, file, ensure_ascii=False, indent=4)
print("Done")