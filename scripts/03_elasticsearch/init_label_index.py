import json
import requests
from itertools import islice
from geojson_utils import get_labels

BASE_URL = 'http://localhost:9200/'

LABEL_INDEX = 'rumsey-labels'

API_URL = BASE_URL + LABEL_INDEX

BULK_URL = API_URL + '/_bulk'

BATCH_SIZE = 10
  
"""
Delete index, if exists
"""
response = requests.delete(API_URL)

"""
Init index from JSON config
"""
with open('./mappings/mappings_labels.json') as f:
  data = json.load(f)
  response = requests.put(API_URL, json=data)

  if (response.status_code == 200):
    print('Map label index initialized successfully: ' + API_URL)
  else:
    print(response.text)

print("Indexing data...")

map_ctr = 0
label_ctr = 0
with open('../01_data_preparation/output/map-metadata.json') as f:
  records = enumerate(json.load(f))

  while True:
    next_batch = list(islice(records, BATCH_SIZE))

    if not next_batch:
      break

    payload = ''

    for idx, record in next_batch:
      map_ctr += 1

      filename = record['mapkurator_filename']

      # For each record, fetch all the labels from the GeoJSON
      # and add them as one ES document each
      labels = get_labels(filename)

      print(f'Reading file {filename} ({map_ctr} - {len(labels)} labels)')

      # Delete unnecessary metadata fields
      del record['description']

      if 'physical_size_cm' in record:
        del record['physical_size_cm']

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

      if 'area' in record:
        record['area_cm2'] = record['area'] 
        del record['area']

      if 'num_labels' in record:
        del record['num_labels']

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

      if 'world_area' in record:
        del record['world_area']

      if 'region' in record:
        del record['region']

      if 'country' in record:
        del record['country']

      if 'state_province' in record:
        del record['state_province']

      if 'county' in record:
        del record['county']

      del record['image_manifest']
      del record['presentation_manifest']

      for label in labels:
        label_ctr += 1
        
        props = label['properties']
        
        doc = {
          'geometry': label['geometry']
        }

        if 'text' in props:
          doc['text'] = props['text']
        
        if 'postocr_label' in props:
          doc['postocr_label'] = props['postocr_label']
        
        if 'score' in props:
          doc['score'] = props['score']

        doc.update(record)

        meta = json.dumps({
          'index': { '_index': LABEL_INDEX }
        })

        payload = f'{payload}{meta}\n{json.dumps(doc)}\n'

    print('Indexing...')
    headers = { 'Content-Type': 'application/x-ndjson' }
    response = requests.post(BULK_URL, data=payload, headers=headers)

    if response.status_code != 200:
      print(f'Error indexing data: {response.text}')
    else:
      print('Indexed ' + str(map_ctr) + ' maps (' + str(label_ctr) + ' labels)')

print(f'Successfully indexed {map_ctr} map sheet records ({label_ctr} labels)')