import omniture
from datetime import datetime, date

from config import username, secret


def get_skus(report):

    skus = [sku[0] for sku in report.data['orders']]
    print(skus)


analytics = omniture.authenticate(username, secret)

suite = analytics.suites['np-extra']

dt_to = datetime.now()
dt_from = date(dt_to.year, dt_to.month, 1)


report = suite.report.range(dt_from.strftime('%Y/%m/%d'), dt_to.strftime('%Y/%m/%d')).ranked(metrics=['orders'], elements=['product'], top=100).sync()
get_skus(report)