import configparser

config = configparser.ConfigParser()
config.read('config.ini')


print(config['Git']['url'])
print(config['Git'].getint('project_id'))
