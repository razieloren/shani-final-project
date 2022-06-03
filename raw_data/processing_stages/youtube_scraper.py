#!/usr/bin/env python3

import sqlite3
import argparse
from youtubesearchpython import VideosSearch

def parse_args():
    args = argparse.ArgumentParser(description='Final Processed Albums Table')
    args.add_argument('-d', '--db', help='Output DB file', default='albums_no_imgs.sqlite')
    return args.parse_args()

def prepare_tables(cur):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS raw_youtube (
            gid TEXT PRIMARY KEY,
            link TEXT NOT NULL
        );
        '''
    )

def get_all_gids(cur):
    cur.execute('''
        SELECT a.gid, a.artist, r.track_name
        from album AS a
        LEFT JOIN raw_spotify AS r ON a.gid = r.gid
        WHERE r.track_name IS NOT NULL
    ''')
    return cur.fetchall()

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        cur = conn.cursor()
        prepare_tables(cur)
        conn.commit()
        print('Getting all songs')
        for gid, artist, track in get_all_gids(cur):
            try:
                print('Trying', artist, track)
                videosSearch = VideosSearch(f'{artist} {track}', limit=1)
                link = videosSearch.result()['result'][0]['link']
                cur.execute('''
                    INSERT INTO raw_youtube (gid, link) VALUES (?, ?)
                ''', (gid, link))
                conn.commit()
            except Exception as e:
                print('Skipping', artist, track, e)


if __name__ == '__main__':
    main()