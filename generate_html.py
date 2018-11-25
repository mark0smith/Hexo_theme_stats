import json
import os
import datetime
from jinja2 import Environment, FileSystemLoader

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, 'templates')
env = Environment( loader = FileSystemLoader(templates_dir) )
template = env.get_template('layout.html')

# get today
today = datetime.datetime.today().strftime('%Y-%m-%d')

with open('report/fork/{}.json'.format(today)) as f:
    fork_data = json.load(f)
with open('report/star/{}.json'.format(today)) as f:
    star_data = json.load(f)
with open('report/watch/{}.json'.format(today)) as f:
    watch_data = json.load(f)

filename = os.path.join(root,'docs', 'index.html')
def find(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result
                    

with open(filename, 'w') as fh:
    fh.write(template.render(
        today=today,
        fork_labels = list(find('name',{'x':fork_data})),
        fork_data = list(find('fork',{'x':fork_data})),
        star_labels = list(find('name',{'x':star_data})),
        star_data = list(find('star',{'x':star_data})),
        watch_labels = list(find('name',{'x':watch_data})),
        watch_data = list(find('watch',{'x':watch_data})),
    ))
