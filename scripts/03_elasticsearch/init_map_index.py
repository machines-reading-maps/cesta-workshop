import json
import requests
from itertools import islice
from geojson_utils import get_map_text

BASE_URL = 'http://localhost:9200/'

MAP_INDEX = 'rumsey-maps'

API_URL = BASE_URL + MAP_INDEX

BULK_URL = API_URL + '/_bulk'

INCLUDE_MAP_TEXT = True

BATCH_SIZE = 250
  
"""
Delete index, if exists
"""
response = requests.delete(API_URL)

"""
Init index from JSON config
"""
with open('./mappings/mappings_maps.json') as f:
  data = json.load(f)
  response = requests.put(API_URL, json=data)

  if (response.status_code == 200):
    print('Map sheet index initialized successfully: ' + API_URL)
  else:
    print(response.text)

print("Indexing data...")

ctr = 0
with open('../01_data_preparation/output/map-metadata.json') as f:
  records = enumerate(json.load(f))

  while True:
    next_batch = list(islice(records, BATCH_SIZE))

    if not next_batch:
      break

    payload = ''

    for idx, record in next_batch:
      ctr += 1

      date = record['date_normalized'] if 'date_normalized' in record else None
      pub_date = record['pub_date_normalized'] if 'pub_date_normalized' in record else None

      if date != None:
        record['date_text'] = record['date']
        record['date'] = str(date)
        del record['date_normalized']

      if pub_date != None:
        record['pub_date_text'] = record['pub_date']
        record['pub_date'] = str(pub_date)
        del record['pub_date_normalized']

      if date != None or pub_date != None:
        record['date_or_pub_date'] = date if date != None else pub_date
  
      try:
        w_cm = record['physical_size_cm'][0]
        h_cm = record['physical_size_cm'][1]

        record['width_cm'] = w_cm
        record['height_cm'] = h_cm
        record['area_cm2'] = w_cm * h_cm

        del record['physical_size_cm']
        del record['area']
      except:
        pass

      related_places = []

      if 'world_area' in record:
        related_places += record['world_area']

      if 'region' in record:
        related_places += record['region']
      
      if 'country' in record:
        related_places += record['country']

      if 'state_province' in record:
        related_places += record['state_province']

      if 'county' in record:
        related_places += record['county']

      if (len(related_places) > 0):
        # Remove duplicates
        record['related_place'] = list(dict.fromkeys(related_places))

      if 'num_labels' not in record:
        record['num_labels'] = 0

      if INCLUDE_MAP_TEXT:
        filename = record['mapkurator_filename']

        print(f'Reading file {filename} ({str(ctr)})')

        # For each record, fetch all the labels from the GeoJSON and
        # add them as an extra map_text text field
        record['map_text'] = get_map_text(filename)

      meta = json.dumps({
        'index': { '_index': MAP_INDEX }
      })
    
      payload = f'{payload}{meta}\n{json.dumps(record)}\n'
      
    headers = { 'Content-Type': 'application/x-ndjson' }
    response = requests.post(BULK_URL, data=payload, headers=headers)

    if response.status_code != 200:
      print(f'Error indexing data: {response.text}')
    else:
      print('Indexed ' + str(ctr))

print(f'Successfully indexed {ctr} map sheet records')