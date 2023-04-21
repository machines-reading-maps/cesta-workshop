import sys
sys.path.append('..')

import config
import json
import mrm_utils

# Load metadata CSV
print('Loading metadata CSV')
metadata = mrm_utils.read_csv(config.METADATA_CSV)

total = len(metadata)
print(f'Done ({str(total)} rows)')

data = []

for idx, row in enumerate(metadata):
  print(f'Processing ({idx}/{total})')

  record = {}

  # Also extract the more complex fields, hidden in the 'fieldValues' dump
  fields_str = row['fieldValues']

  fields = mrm_utils.obscure_parse(fields_str)

  # Helpers
  def f(name):
    return fields[name][0] if name in fields else None
  
  def split(str):
    return [f.strip(' \'"') for f in str.split(',')]

  def append(key, value):
    if (value):
      record[key] = value

  # Construct normalized record
  record['title'] = row['title']
  record['display_name'] = row['displayName']

  append('pub_title', f('Pub Title'))

  record['date'] = row['date']
  record['pub_date'] = row['pubdate']

  try:  
    record['date_normalized'] = int(float(row['date']))
  except:
    print('Could not parse date: ' + row['date'])

  try:  
    record['pub_date_normalized'] = int(float(row['pubdate']))
  except:
    print('Could not parse date: ' + row['pubdate'])

  record['creator'] = row['creator']

  append('pub_author', f('Publication Author'))
  append('pub_type', split(f('Pub Type')) if 'Pub Type' in fields else None)
  append('pub_location', f('Publisher Location') if 'Publisher Location' in fields else None)

  record['description'] = row['description']

  try:
    record['scale'] = int(float(row['scale']))
  except:
    print('Could not parse scale: ' + row['scale'])

  physical_size = json.loads(row['physical_size']) if row['physical_size'] else None
  if (physical_size):
    record['physical_size_cm'] = physical_size
    record['area'] = float(physical_size[0]) * float(physical_size[1])

  append('world_area', split(f('World Area')) if 'World Area' in fields else None)
  append('region', split(f('Region')) if 'Region' in fields else None)
  append('country', split(f('Country')) if 'Country' in fields else None)
  append('state_province', split(f('State/Province')) if 'State/Province' in fields else None)
  append('county', split(f('County')) if 'County' in fields else None)
  
  record['external_id'] = row['external_id'].strip(' \'"')
  record['list_no'] = row['list_no']
  record['image_manifest'] = row['image_url']
  record['presentation_manifest'] = row['iiifManifest']
  record['web_url'] = row['link_url']

  record['mapkurator_filename'] = f'{row["filename"]}.geojson'

  # Load GeoJSON and count no. of labels
  geojson_path = f'{config.GEOJSON_FOLDER}/{row["filename"]}.geojson'

  try:
    with open(geojson_path, 'r') as file:          
      fc = json.load(file)
      
      record['num_labels'] = len(fc['features'])

  except FileNotFoundError:
      print('Error loading file: ' + geojson_path) 

  data.append(record)

with open('output/map-metadata.json', 'w') as f:
  json.dump(data, f)

print('Done.')