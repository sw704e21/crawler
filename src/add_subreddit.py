import csv
import sys

if __name__ == '__main__':
    with open('subreddits.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([sys.argv[1]])
