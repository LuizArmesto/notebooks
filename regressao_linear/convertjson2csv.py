import json
import unicodecsv as csv

json_filename_template = 'files/apartamentos_alugar_sao_paulo_pagina_{0:04d}.json'
csv_filename = 'apartamentos_alugar_sao_paulo.csv'

pages = 1773

already_included = []

bairros = {}
last_bairro_id = 0

def get_bairro_id(bairro):
    global last_bairro_id
    bairro = bairro.lower()
    if bairro in bairros:
        return bairros[bairro]
    bairros[bairro] = last_bairro_id + 1
    last_bairro_id += 1
    return last_bairro_id


with open(csv_filename, 'w') as csv_fp:
    fieldnames = ['valor', 'area', 'quartos', 'suites', 'vagas', 'bairro_id', 'bairro', 'cidade', 'tipo', 'subtipo', 'id']
    csv_writer = csv.DictWriter(csv_fp, fieldnames=fieldnames, encoding='utf-8')
    csv_writer.writeheader()
    for page in xrange(1, pages + 1):
        json_filename = json_filename_template.format(page)
        with open(json_filename, 'r') as json_fp:
            json_content = json.loads(json_fp.read())
            for item in json_content:
                if item.get('id') not in already_included:
                    item['valor'] = item.get('valor', '').replace('R$ ', '').replace('.', '')
                    if item.get('valor') != 'Sob Consulta' and int(item.get('quartos')) <= 10 and int(item.get('valor')) <= 10000:
                        item['bairro_id'] = get_bairro_id(item.get('bairro'))
                        already_included.append(item.get('id'))
                        csv_writer.writerow(item)
