import omniture
import sys
import os
from pprint import pprint
import hashlib
import base64

from config import username, secret


analytics = omniture.authenticate(username, secret)

print (analytics.suites)



