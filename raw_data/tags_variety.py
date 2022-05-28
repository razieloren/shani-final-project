#!/usr/bin/env python3

import csv
import json
import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Final Processed Albums Table')
    args.add_argument('-d', '--db', help='Output DB file', default='albums.sqlite')
    return args.parse_args()

def try_add(labels, new_one):
    if new_one not in labels:
        labels[new_one] = 1
    else:
        labels[new_one] += 1

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        # cur = conn.cursor()
        # cur.execute('''
        #     SELECT first_label, second_label, third_label
        #     FROM album_processed
        # ''')
        # labels = cur.fetchall()
        # label_dist = {}
        # for label1, label2, label3 in labels:
        #     try_add(label_dist, label1)
        #     try_add(label_dist, label2)
        #     try_add(label_dist, label3)
        label_dist = {}
        with open('vision.json', 'r') as f:
            data = json.load(f)
        for gid, attrs in data.items():
            for annot in attrs['labelAnnotations']:
                try_add(label_dist, annot['description'])
        
        with open('labels_all.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Label', 'Amount'])
            for label, amount in label_dist.items():
                writer.writerow([label, amount])


if __name__ == '__main__':
    main()