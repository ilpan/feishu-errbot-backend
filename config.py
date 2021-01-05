import logging

BACKEND = 'Feishu'

BOT_EXTRA_BACKEND_DIR = r'<path/to/feishu-errbot-backend>'
BOT_DATA_DIR = r'<path/to/your/errbot/data/directory>'
BOT_EXTRA_PLUGIN_DIR = r'<path/to/your/errbot/plugin/directory>'

BOT_LOG_FILE = r'<path/to/your/errbot/logfile.log>'
BOT_LOG_LEVEL = logging.INFO

BOT_IDENTITY = {
    "app_id": "xxx",
    "app_secret": "xxx",
    "verification_token": "xxx",
    "encrypt_key": None,
    "host": "0.0.0.0",
    "port": 8888
}

BOT_ADMINS = ('ou_xxx',)