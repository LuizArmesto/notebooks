import requests
import json

from concurrent import futures

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
root_url = 'http://www.zapimoveis.com.br/aluguel/apartamentos/sp+sao-paulo/'
validate_search_url = 'http://www.zapimoveis.com.br/Busca/ValidarNecessidadeBusca/'
search_response_url = 'http://www.zapimoveis.com.br/Busca/RetornarBuscaAssincrona/'

filename_template = 'files/apartamentos_alugar_sao_paulo_pagina_{0:04d}.json'

pages = 1773

start = 1
end = pages

response = requests.get(root_url, headers=headers)


def load_page(page):
    data = {
        'tipoOferta': 1,
        'paginaAtual': (page - 1) or 1,
        'ordenacaoSelecionada': None,
        'pathName': '/aluguel/apartamentos/sp+sao-paulo/',
        'hashFragment' :'{{"precomaximo":"2147483647","parametrosautosuggest":[{{"Bairro":"","Zona":"","Cidade":"SAO PAULO","Agrupamento":"","Estado":"SP"}}],"pagina":"{page}","paginaOrigem":"ResultadoBusca"}}'.format(page=page)
    }
    response = requests.post(validate_search_url, data=data, headers=headers)
    response = requests.post(search_response_url, data=data, headers=headers)
    return response.content


def save_page(page):
    filename = filename_template.format(page)
    json_content = json.loads(load_page(page))
    results = json_content.get('Resultado', {}).get('Resultado', [])
    filtered = []
    for result in results:
        filtered.append({
            'valor': result.get('Valor'),
            'area': result.get('Area'),
            'quartos': result.get('QuantidadeQuartos'),
            'suites': result.get('QuantidadeSuites'),
            'vagas': result.get('QuantidadeVagas'),
            'bairro': result.get('Bairro'),
            'cidade': result.get('Cidade'),
            'id': result.get('CodigoOfertaZAP'),
            'tipo': result.get('Tipo'),
            'subtipo': result.get('SubTipo'),
        })
    content = json.dumps(filtered)
    with open(filename, 'w') as fp:
        fp.write(content)
    print 'Saving {}'.format(filename)


with futures.ThreadPoolExecutor(max_workers=5) as executor:
    future_to_id = dict((executor.submit(save_page, page), page) for page in xrange(start, end + 1))

    for future in futures.as_completed(future_to_id):
        id = future_to_id[future]
        if future.exception() is not None:
            print('{} generated an exception: {}'.format(id, future.exception()))
