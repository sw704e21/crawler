import csv
import sys


with open('subreddits.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([sys.argv[1]])
