import omniture
from datetime import datetime, date

from config import username, secret


analytics = omniture.authenticate(username, secret)

suite = analytics.suites['np-extra']

dt_to = datetime.now()
dt_from = date(dt_to.year, dt_to.month, 1)

print(dt_to, dt_from)

report = suite.report.range(dt_from.strftime('%Y/%m/%d'), dt_to.strftime('%Y/%m/%d')).ranked(metrics=['orders'], elements=['product']).sync()
print (report.data['orders'])