import csv
import sys


with open('subreddits.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([sys.argv[1]])
