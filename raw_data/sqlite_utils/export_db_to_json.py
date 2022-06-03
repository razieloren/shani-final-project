#!/usr/bin/env python3

import json
import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Export DB to JSON')
    args.add_argument('-d', '--db', help='DB file', default='albums_no_imgs.sqlite')
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        cur = conn.cursor()
        cur.execute(f'''
            SELECT *
            FROM album_processed3
        ''')
        data = {}
        for album in cur.fetchall():
            data[album[0]] = {
                'album_name': album[1],
                'artist_name': album[2],
                'release_year': album[3],
                'colors': None if album[4] is None else [list(map(float, e.split(','))) for e in album[4].split('|')],
                'faces': None if album[5] is None else [list(map(float, e.split(','))) for e in album[5].split('|')],
                'pesrons': None if album[6] is None else [list(map(float, e.split(','))) for e in album[6].split('|')],
                'text_blocks': None if album[7] is None else [list(map(float, e.split(','))) for e in album[7].split('|')],
                'urban': album[8],
                'musical': album[9],
                'geometric': album[10],
                'fashion': album[11],
                'drawing': album[12],
                'photography': album[13],
                'small_thumbnail': album[14],
                'big_thumbnail': album[15],
                'track_name': album[16],
                'genre': album[18],
                'face_ratio': album[19],
                'text_ratio': album[20],
                'persons_ratio': album[21],
                'youtube_link': album[22]
            }
        with open('db_dump.json', 'w') as f:
            json.dump(data, f)

if __name__ == '__main__':
    main()