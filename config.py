import os 

settings = {
    'TOKEN': '',
    'NAME BOT': 'TurboBot',
    'ID': 792121708634439691,
    'PREFIX': '$'
}

settings['TOKEN'] = os.environ.get('BOT_TOKEN')