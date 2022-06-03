import logging

MIN_PORT_NUMBER = 1024
MAX_PORT_NUMBER = 65535

ANON_ACCOUNT_NAME = 'anonymous'

DEFAULT_LISTEN_ADDRESS = ''
DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 1
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
RESPONDEFAULT_IP_ADDRESSSE = 'respondefault_ip_addressse'

STATUS_OK = 200
STATUS_BAD_REQUEST = 400

LOGGING_LEVEL = logging.DEBUG

EXIT_CLIENT_CHAR = '^'

ACCEPTABLE_CLIENT_MODES: tuple = ('listen', 'send')
