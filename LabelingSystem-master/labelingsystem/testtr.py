import csv
from io import TextIOWrapper

reader = csv.reader(open('/home/sara/Documents/PhD Courses/Thesis/LabelingSystem-master/labelingsystem/sample_survey.csv', newline=''), delimiter='|')
#reader = csv.reader(TextIOWrapper('sample_survey1.csv'), delimiter='|', skipinitialspace=True)
print (reader)
labels = next(reader)
for row in labels:
  print(row)
