import sys
sys.path.append('..')

import config
import json
import pyproj
from shapely.geometry import shape

epsg_3857 = pyproj.CRS('EPSG:3857')
epsg_4326 = pyproj.CRS('EPSG:4326') # WGS 84

transformer = pyproj.Transformer.from_crs(epsg_3857, epsg_4326)

def get_map_text(filename):
  filepath = config.GEOJSON_FOLDER + '/' + filename

  try:
    with open(filepath) as f:
      fc = json.load(f)
        
      labels = [str(f['properties']['text']) for f in fc['features']]

      # Handle broken mapKurator serialization
      return ' '.join(labels)
  except FileNotFoundError:
    print('Not found - skipping')
    return None
  
def get_labels(filename, centroid_only = True):
  filepath = config.GEOJSON_FOLDER + '/' + filename

  try:
    with open(filepath) as f:
      fc = json.load(f)

      features = fc['features']

      for feature in features:
        if 'geometry' in feature and feature['geometry'] != None and feature['geometry']['type'] == 'Polygon':
          # mapKurator features are NOT in WGS 84 :-(
          coordinates = feature['geometry']['coordinates'][0]
          feature['geometry']['coordinates'][0] = [ transformer.transform(c[0], c[1]) for c in coordinates ]

          if centroid_only:
            geom = shape(feature['geometry'])
            cent = geom.centroid

            feature['geometry'] = {
              'type': 'Point',
              'coordinates': [ cent.y, cent.x ]
            }

      return features

  except FileNotFoundError:
    print('Not found - skipping')
    return []