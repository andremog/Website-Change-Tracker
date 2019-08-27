import json
import requests
import hashlib
import re
from time import sleep, localtime, strftime
from plyer import notification
from os.path import exists, isfile

regular = {}

with open('config.json', 'r', encoding='utf-8') as config:
  configuration = json.load(config)
  (update_interval, website_list) = (configuration['update_interval'], configuration['website_list'])

# Generate hashes and RegExps
with open('config.json', 'w', encoding='utf-8') as config:
  for page in website_list:
    if 'hash' not in page:
      page['hash'] = hashlib.sha1(page['url'].encode('utf-8')).hexdigest()
    regular[page['hash']] = []
    for ignore in page['ignore']:
      regular[page['hash']].append(re.compile(ignore))

  configuration = {'update_interval': update_interval, 'website_list': website_list}
  json.dump(configuration, config)

notification.notify('Tracking started', 'Tracking changes on ' + str(len(website_list)) + ' websites.')
print(strftime('%X', localtime()), end=' - ')
print('Started tracking changes on ' + str(len(website_list)) + ' websites.')

while True:
  try:
    for page in website_list:
      web_content = requests.get(page['url']).content.decode('utf-8')

      for ignore in regular[page['hash']]:
        web_content = ignore.sub('', web_content)

      filepath = './website_data/' + page['hash'] + '.html'
      if not (exists(filepath) and isfile(filepath)):
        with open(filepath, 'w', encoding='utf-8') as file:
          file.write(web_content)
      else:
        changed = False
        with open(filepath, 'r', encoding='utf-8') as file:
          previous_content = file.read()
          # for i in range(max([len(previous_content), len(web_content)])):
          #   if i >= len(previous_content):
          #     print(i, web_content[i])
          #   elif i >= len(web_content):
          #     print(i, previous_content[i])
          #   elif (previous_content[i] != web_content[i]):
          #     print(i, previous_content[i], web_content[i])
          if previous_content != web_content:
            changed = True
            notification.notify('Change detected', 'Change detected on website ' + page['name'] + ' (' + page['url'] + ')')
            print(strftime('%X', localtime()), end=' - ')
            print('A change was detected on website ' + page['name'] + ' (' + page['url'] + ')')

        if changed:
          with open(filepath, 'w', encoding='utf-8') as file:
            file.write(web_content)
    sleep(update_interval)
  except Exception as excpt:
    print(strftime('%X', localtime()), end=' - ')
    print('An exception has occurred: ', end='')
    print(excpt)
