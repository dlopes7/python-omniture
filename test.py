import requests
import omniture
import sys
import json
from datetime import datetime, date

from config import username, secret


def get_skus(skus):

    skus = {sku[0]: sku[2] for sku in skus}
    return skus


def get_precos(skus):
    dict_skus = get_skus(skus)
    url = 'http://preco.api-extra.com.br/v1/skus/Precovenda?IdsSku={skus}'.format(skus=','.join(dict_skus.keys()))
    r = requests.get(url)
    precos = r.json()

    for preco in precos['PrecoSkus']:
        print (preco['PrecoVenda']['IdSku'], dict_skus[str(preco['PrecoVenda']['IdSku'])], preco['PrecoVenda']['Preco'], sep='\t')


def discovery(skus):
    dict_data = {'data': []}
    [dict_data['data'].append({'{#SKU}': sku}) for sku in get_skus(skus).keys()]
    print(dict_data)


if __name__ == '__main__':

    try:
        bandeira = sys.argv[1]
        funcao = sys.argv[2]
    except:
        bandeira = 'np-extra'
        funcao = 'discovery'


    analytics = omniture.authenticate(username, secret)
    suite = analytics.suites[bandeira]

    dt_to = datetime.now()
    dt_from = date(dt_to.year, dt_to.month, 1)

    report = suite.report.range(dt_from.strftime('%Y/%m/%d'),
                                dt_to.strftime('%Y/%m/%d')).ranked(metrics=['orders'],
                                                                   elements=['product'],
                                                                   top=200).sync()

    if funcao == 'discovery':
         discovery(report.data['orders'])
    elif funcao == 'metricas':
        get_precos(report.data['orders'])



