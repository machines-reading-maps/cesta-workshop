import csv
import json
import re

def read_csv(filename):
  with open(filename, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)

    data = []
        
    for row in reader:
      data.append(row)
    
    return data
  
def obscure_parse(input_str):
  # Define a regular expression pattern to match all double quotes
  # except when they appear before or after a square bracket
  first = r'(?<!\[)"(?!\])'
  
  # Use the re.sub() function to replace all matches with "@"
  output_str = re.sub(first, '@', input_str)

  # Next, replace all single quotes with double quotes, using
  # a regular expression pattern to match all single quotes before 
  # or after a square bracket, curly bracket, or colon
  second = r"'(?=[\[\]:{}])|(?<=[\[\]:{}])'"

  # Next, replace all single quotes with double quotes, using
  # a regular expression pattern to match all single quotes before 
  # or after a square bracket, curly bracket, or colon

  output_str = re.sub(second, '"', output_str)

  # Third, get rid of the various "Note" fields, because they re literally unescapable...
  # Define a regular expression pattern to match the contents of the "Note" field between the square brackets and curly brackets
  pattern = r'"Note": \[[^\]]*\][^\}]*\}'
  output_str = re.sub(pattern, r'"Note": []}', output_str)

  pattern = r'"Pub Note": \[[^\]]*\][^\}]*\}'
  output_str = re.sub(pattern, r'"Pub Note": []}', output_str)

  pattern = r'"Full Title": \[[^\]]*\][^\}]*\}'
  output_str = re.sub(pattern, r'"Pub Note": []}', output_str)
  
  pattern = r'"Short Title": \[[^\]]*\][^\}]*\}'
  output_str = re.sub(pattern, r'"Short Note": []}', output_str)

  # pattern = r'"Pub Title": \[[^\]]*\][^\}]*\}'
  # output_str = re.sub(pattern, r'"Pub Note": []}', output_str)

  pattern = r'"Reference": \[[^\]]*\][^\}]*\}'
  output_str = re.sub(pattern, r'"Reference": []}', output_str)

  pattern = r'"Pub Reference": \[[^\]]*\][^\}]*\}'
  output_str = re.sub(pattern, r'"Pub Reference": []}', output_str)

  output_str = output_str.replace("\\", '')
  output_str = output_str.replace("\\", '')

  as_list = json.loads(output_str)

  as_dict= {}

  for key_val in as_list:
    as_dict.update(key_val)

  return as_dict
