import json
import seaborn as sns
import matplotlib.pyplot as plt

discarded = 0

with open('../01_data_preparation/output/map-metadata.json') as f:
  data = json.load(f)

  x = []
  y = []

  for obj in data:
    if 'date_normalized' in obj and 'num_labels' in obj:
      # if obj['num_labels'] < 20000:
        x.append(obj['date_normalized'])
        y.append(obj['num_labels'])

    elif 'date_normalized' in obj:
      print('Discarding record without labels count')
      discarded += 1

    else:
      print('Discarding record with date: ' + obj['date'])
      discarded += 1
    
  print('Total discarded: ' + str(discarded) + ' of ' + str(len(data)))

  sns.regplot(
    x=x, 
    y=y, 
    ci=None, 
    scatter_kws={ 's':1 },
    line_kws={'color': 'red', 'label': 'Trend'})
  
  plt.yscale('log')
  plt.legend()
  plt.show()



