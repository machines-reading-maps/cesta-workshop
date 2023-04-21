import csv
import json

META_TYPE = {
  'National Atlas':	'atlas',
  'Case Map': 'sheet',
  'Separate Map': 'sheet',
  'World Atlas': 'atlas',
  'Exploration Book': 'book',
  'Book Map': 'book',
  'City Atlas': 'atlas',
  'Regional Atlas': 'atlas',
  'Geography Book': 'book',
  'Globe Gores': 'globe',
  'Broadside': 'other',
  'Guide Book': 'book',
  'Wall Map': 'sheet',
  'Military Atlas': 'atlas',
  'School Atlas': 'atlas',
  'Pocket Map': 'sheet',
  'Gov\'t Report Book': 'book',
  'Chart Map': 'sheet',
  'Manuscript Map': 'sheet',
  'Chart Atlas': 'atlas',
  'Classical Atlas': 'atlas',
  'Ephemera': 'other',
  'Letter': 'other',
  'Historical Atlas': 'atlas',
  'Timeline': 'other',
  'Geologic Atlas': 'atlas',
  'Game': 'other',
  'Celestial Atlas': 'atlas',
  'Survey Book': 'book',
  'State Atlas': 'atlas',
  'Physical Atlas': 'atlas',
  'Geology Book': 'book',
  'Statistical Atlas': 'atlas',
  'Survey Map': 'sheet',
  'Real Estate Map': 'sheet',
  'Aerial Photography': 'photograph',
  'Puzzle': 'other',
  'Timetable Map': 'sheet',
  'County Atlas': 'atlas',
  'Gazetteer Book': 'book',
  'Advertisement': 'other',
  'Atlas Map': 'atlas',
  'Section Title Page': 'other',
  'Magazine': 'other',
  'Newspaper Map': 'sheet',
  'Fabric Map': 'other',
  'Newspaper': 'other',
  'Pamphlet': 'book',
  'Religious Atlas': 'atlas',
  'Mining Atlas': 'atlas',
  'View': 'sheet',
  'Commercial Reference Book': 'book',
  'Aerial Photograph': 'photograph',
  'Coat of Arms': 'other',
  'Game Map': 'other',
  'Pianta della Cita di Napoli. Rapporto 1:5000.': 'sheet',
  'Thematic Atlas': 'atlas',
  'Puzzle Map': 'other',
  'Manuscript Book': 'book'
}

with open('./output/map-metadata.json') as file:
  records = json.load(file)

  for record in records:
    if 'pub_title' in record:
      record['pub_title'] = record['pub_title'][:100]

    if 'pub_type' in record:
      record['pub_type_grouped'] = list(dict.fromkeys([META_TYPE[t] for t in record['pub_type']]))

    del record['display_name']
    
    del record['description']

    record['image_manifest'] = record['image_manifest'].replace('https://images.iiifhosting.com/iiif/', '').replace('/info.json', '')
    
    del record['presentation_manifest']
    
    record['web_url'] = record['web_url'].replace('http://www.davidrumsey.com/luna/servlet/detail/', '')

  with open('./output/map-metadata-compact.json', 'w') as out:
      json.dump(records, out)

  for record in records:
    if 'pub_type' in record:
      record['pub_type'] = '|'.join(record['pub_type'])

    if 'pub_type_grouped' in record:
      record['pub_type_grouped'] = '|'.join(record['pub_type_grouped'])

    related_place = []

    if 'world_area' in record:
      related_place += record['world_area']
      record['world_area'] = '|'.join(record['world_area'])

    if 'region' in record:
      related_place += record['region']
      record['region'] = '|'.join(record['region'])

    if 'country' in record:
      related_place += record['country']
      record['country'] = '|'.join(record['country'])

    if 'state_province' in record:
      related_place += record['state_province']
      record['state_province'] = '|'.join(record['state_province'])

    if 'county' in record:
      related_place += record['county']
      record['county'] = '|'.join(record['county'])

    record['related_place'] = '|'.join(related_place)

    if 'physical_size_cm' in record:
      record['w'] = record['physical_size_cm'][0]
      record['h'] = record['physical_size_cm'][1]
      del record['physical_size_cm']

  keys = [
    'title',
    'pub_title',
    'date',
    'pub_date',
    'date_normalized',
    'pub_date_normalized',  
    'creator',
    'pub_author',
    'pub_type',
    'pub_type_grouped',
    'pub_location',
    'scale',
    'w',
    'h',
    'area',
    'world_area',
    'region',
    'country',
    'state_province',
    'county',
    'related_place',
    'external_id',
    'list_no',
    'image_manifest',
    'web_url',
    'mapkurator_filename',
    'num_labels'
  ]

  with open('./output/map-metadata-compact.csv', 'w') as out:
    writer = csv.DictWriter(out, keys)
    writer.writeheader()
    writer.writerows(records)

