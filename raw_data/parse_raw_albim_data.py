#!/usr/bin/env python3

import csv
import time
import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Raw Album Data Parser')
    args.add_argument('-i', '--infile', help='Input file', required=True)
    args.add_argument('-o', '--output', help='Output DB file', default='albums.sqlite')
    return args.parse_args()

def prepare_tables(conn):
    cur = conn.cursor()
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS album (
            gid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            artist TEXT NOT NULL,
            release_year INTEGER NOT NULL
        );
        '''
    )

def main():
    args = parse_args()
    albums = {}
    with open(args.infile, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        start = time.time()
        next_print = 50000
        # Skip header
        next(csv_reader)
        for row in csv_reader:
            gid, album, artist, release_year = row
            if gid not in albums:
                albums[gid] = {
                    'gid': gid,
                    'album': album,
                    'artist': [artist],
                    'release_year': release_year
                }
            else:
                if artist not in albums[gid]['artist']:
                    albums[gid]['artist'].append(artist)
            if len(albums) == next_print:
                print(f'Parsed {len(albums)} albums in {round(time.time() - start, 2)} seconds')
                next_print += 50000
    albums_unique = {}
    for gid, values in albums_unique.items():
        key = f'{values["album"]}__{values["artist"]}'
        if key not in albums_unique:
            albums_unique[key] = {
                'gid': gid,
                'album': values['album'],
                'artist': values['artist'],
                'release_year': values['release_year']
            }
        else:
            if values['release_year'] < albums_unique[key]['release_year']:
                albums_unique[key]['gid'] = values['gid']
                albums_unique[key]['release_year'] = values['release_year']
    with sqlite3.connect(args.output) as conn:
        prepare_tables(conn)
        cur = conn.cursor()
        for _, values in albums_unique.items():
            cur.execute(f'''
                INSERT INTO album (gid, name, artist, release_year)
                VALUES (?, ?, ?, ?);
            ''', (values['gid'], values['album'], ','.join(values['artist']), values['release_year']))
        conn.commit()
        print('Done')

if __name__ == '__main__':
    main()