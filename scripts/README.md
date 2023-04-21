# Preparing and Using Map and Label Data

This folder contains utilities for preparing and using map & label data from the Machines Reading 
Maps x [Rumsey Maps](https://www.davidrumsey.com/) collaboration for your own analyses. 

The source data that this repository relies on was compiled by the US team of the [Machines Reading
Maps](https://machines-reading-maps.github.io/) project, and consists of two datasets:

1. `luna_omo_metadata_56628_20220724.csv`: a CSV file of metadata properties for each map sheet, harvested 
   from davidrumsey.com and Old Maps Online.
2. A folder of GeoJSON files, one per map sheet, containing features for each predicted map label, with label shape 
   (in map image pixel coordinates and geo-coordinates), predicted label and post-OCR correction.

The dataset covers approximately 56.000 map sheets with a total of approx. 90 million labels (for Version 2 of the data). 

## 0. Prerequisites

- Create a copy of the file `config.py.example` and configure the paths to your data (metadata CSV and
  folder of mapKurator GeoJSON files) accordingly.
- Make sure you have [Docker](https://www.docker.com/) installed on your system if you want to 
  use the ElasticSearch indices (see Step 3).

## 1. Preparing the Data

The folder `01_data_preparation` contains helper scripts for creating simplified derivative data, based on the 
original source CSV and GeoJSON data.

This is useful if you want to be able to query multi-value metadata fields that were difficult to parse in `luna_omo_metadata_56628_20220724.csv`.

#### `data_per_sheet.py` 

Generates a JSON file with the following modifications and additions to the source CSV:

- Only the following fields from the CSV file are included (order according to the original order in the CSV):
  __creator__, __date__, __description__, __external id__, __image url__, __link url__, __physical size__, 
  __pub date__, __scale__, __title__, __filename__, __display name__, __iiifManifest__, __list no__.

- The following CSV fields were not incorporated into the JSON file (order according to CSV): __bounds__, 
  __catalog url__, __collection id__, __contributor__, __created__, __dpi__, __georeference changed__, 
  __georeference is finished__, __id__, __is reviewed__, __publisher__, __reviewed__, __viewer url__, 
  __media type__, __relayButtonUrl__, __relayButtonTitle__, __fieldValues__, __relatedFieldValues__, 
  __urlSize4__, __urlSize2__, __urlSize3__, __urlSize0__, __urlSize1__, __affine transformation__,
  __changed__, __created georeference__, __cutline__, __gcps__, __transformation method__, __map id__,
  __image no__.

- Some additional metadata properties that were not included in the CSV as separate columns were extracted 
  from the __fieldValues__ field: __publication title__, __publication author__, __publication type__, 
  __publisher location__, __world area__, __region__, __country__, __state/province__, __county__.

- Various changes were made to the fields, for reasons of easier use or better readability:
  - Two fields __date normalized__ and __pub date normalized__ were added, which represent copies of the 
    original date/pub date string fields, parse to integer/date values.
  - The original string __scale__ field was parsed to an integer value.
  - The original string __physical size__ field was parsed, width and height were converted to separate float values.
  - An additional __area__ field (physical width x physical height) was added for convenience.
  - __image url__ was renamed to __image manifest__.
  - __iiifManifest__ was renamed to __presentation manifest__.
  - __link_url__ was renamed to __web url__.
  - __filename__ was renamed to __mapkurator filename__, and the `.geojson` extension was appended to the filename.

- The script reads the mapKurator GeoJSON file for each map (if available), counts the number of labels in the GeoJSON,
  and records the nubmer of labels in an additional __num labels__ field.

The script stores the result file as `01_data_preparation/output/map-metadata.json`.

#### `compact_metadata.py`

Takes the `map-metadata-json` file as input and produces a more compact representation (<50MB), with only essential fields.
The following changes are made to the input file:

- The __pub title__ field is truncated to only the first 100 characters of the title.
- The following fields are removed: __display name__, __description__, __presentation_manifest__.
- The field __image manifest__ is made more compact by removing the `https://images.iiifhosting.com/iiif/` base URL prefix
  as well as the `/info.json` suffix (which are always the same), leaving only the identifier.
- The field __web url__ is made more compact by removing the `http://www.davidrumsey.com/luna/servlet/detail/` base URL
  prefix.
- An additional "meta-category" is added to the record as __pub_type_grouped__. The meta-category is assigne according
  to [this mapping table](https://github.com/machines-reading-maps/rumsey_mrm_data_analysis/blob/main/scripts/01_data_preparation/compact_metadata.py#L4-L64).

The script writes two result files: a JSON version (`01_data_preparation/output/map-metadata-compact.json`), and
a flattened CSV version (`01_data_preparation/output/map-metadata-compact.csv`). In the CSV version, content of
multi-value fields is concatenated into a single CSV cell using `|` (pipe) as a separating character.

In addition, the CSV version includes an extra field `related place`, which concatenates __all__ distinct values from the
fields __world area__, __region__, __country__, __state province__, __county__.

## 2. Example Visualizations (Python)

For illustration purposes, the folder `02_python_visualizations` contains a script that
generates a scatterplot of the number of labels per map sheet over time.

- Make sure the file `scripts/01_data_preparation/output/map-metadata.json` exists.
- Run `python scatterplot_labels_over_time.py`

## 3. Building ElasticSearch Indices

The folder `03_elasticsearch` contains:

- A Docker configuration file for bootstrapping an installation of [ElasticSearch](https://www.elastic.co/)
  and [Kibana](https://www.elastic.co/kibana), behind an NGINX web proxy.
- ElasticSearch schema mappings for a __map metadata__ and a __label data__ index.
- Python utility scripts to initialize the indices from the map metadata file prepared in Step 1, and the 
  GeoJSON files produced by mapKurator

__To launch ElasticSearch and Kibana:__

- Run `docker compose up`
- ElasticSearch is available on <http://localhost:9200>
- Kibana is available on <http://localhost>

__To build the map metadata index:__

- Make sure the file `scripts/01_data_preparation/output/map-metadata.json` exists.
- Make sure the GeoJSON files from mapKurator are available on a folder on your machine, 
  and the path to the folder is correctly configured in your `config.py` file.
- Run `python init_map_index.py`.
- The indexing will read __all the labels for each map__ from the mapKurator GeoJSON files, 
  and include them as one full-text search field. (This may take a while - be prepared for
  several hours of indexing!)

Alternatively, you can choose to exclude the full-text map label field from the index, by changing 
the `INCLUDE_MAP_TEXT` variable to `False` in the Python script. This will make the index much
smaller, and significantly reduce the indexing time. However, it also means you loose the ability
to do full-text searches of the map content. 

__To build the label index:__

- Make sure the file `scripts/01_data_preparation/output/map-metadata.json` exists.
- Make sure the GeoJSON files from mapKurator are available on a folder on your machine, 
  and the path to the folder is correctly configured in your `config.py` file.
- Run `python init_map_index.py`.

The indexing script will index each label as an individual index record, along with its
geographical location (point centroid coordinate). Be aware that the indexing process will 
take __very long__, up to several days for the full dataset!

