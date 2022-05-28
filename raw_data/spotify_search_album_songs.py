#!/usr/bin/env python3

import time
import random
import sqlite3
import requests
import argparse
import urllib.parse

SPOTIFY_ACCESS_TOKEN = 'BQCCaGnnV-wb2exPaP87QTMw2KWA4izygx7Ms6s_kHxTFlsi34caA2057gj-nOJ3pmtkLXn2Lm8EAjrNbgE'

def parse_args():
    args = argparse.ArgumentParser(description='Final Processed Albums Table')
    args.add_argument('-d', '--db', help='Output DB file', default='albums.sqlite')
    return args.parse_args()

def prepare_tables(cur):
    cur.execute(
        '''
            CREATE TABLE IF NOT EXISTS raw_spotify (
            gid TEXT PRIMARY KEY,
            album_id TEXT NOT NULL,
            album_release_date TEXT NOT NULL,
            album_spotify_url TEXT NOT NULL,
            album_small_thumbnail_url TEXT NOT NULL,
            small_thumbnail_size INTEGER NOT NULL,
            album_big_thumbnail_url TEXT NOT NULL,
            big_thumbnail_size INTEGER NOT NULL,
            track_id TEXT NOT NULL,
            track_spotify_url TEXT NOT NULL,
            track_name TEXT NOT NULL,
            genres TEXT NOT NULL
        );
        '''
    )

def get_all_albums(cur):
    cur.execute('''
        SELECT gid, name, artist
        FROM album
    ''')
    return cur.fetchall()

def get_old_gids(cur):
    cur.execute('''
        SELECT gid
        FROM raw_spotify
    ''')
    return list(map(lambda x: x[0], cur.fetchall()))

def find_smallest_image(images):
    im = images[0]
    for image in images:
        if image['height'] < im['height']:
            im = image
    return im['url'], im['height']

def find_biggest_image(images):
    im = images[0]
    for image in images:
        if image['height'] > im['height']:
            im = image
    return im['url'], im['height']

def api_album(artist, album):
    ar = urllib.parse.quote(artist)
    al = urllib.parse.quote(album)
    r = requests.get(f'https://api.spotify.com/v1/search?type=album&q=artist:{ar}+album:{al}',
        headers={
            'Authorization': f'Bearer {SPOTIFY_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        })
    assert r.status_code == 200, r.status_code
    return r.json()['albums']['items'][0]

def api_album_tracks(album_id):
    r = requests.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks',
        headers={
            'Authorization': f'Bearer {SPOTIFY_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        })
    assert r.status_code == 200, r.status_code
    return r.json()

def api_artist(artist_id):
    r = requests.get(f'https://api.spotify.com/v1/artists/{artist_id}',
        headers={
            'Authorization': f'Bearer {SPOTIFY_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        })
    assert r.status_code == 200, r.status_code
    return r.json()    

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        cur = conn.cursor()
        prepare_tables(cur)
        conn.commit()
        raw_albums = get_all_albums(cur)
        old_gids = get_old_gids(cur)
        needed_albums = list(filter(lambda x: x[0] not in old_gids, raw_albums))
        total = len(needed_albums)
        amount = 0
        for gid, album_name, artist_name in needed_albums:
            try:
                amount += 1
                if gid in old_gids:
                    continue
                album = api_album(artist_name, album_name)
                smallest_thumbnail, smallest_size = find_smallest_image(album['images'])
                biggest_thumbnail, biggest_size = find_biggest_image(album['images'])
                album_id = album['id']
                release_date = album['release_date']
                album_spotify_url = album['external_urls']['spotify']
                track = random.choice(api_album_tracks(album_id)['items'])
                track_id = track['id']
                track_spotify_url = track['external_urls']['spotify']
                track_name = track['name']
                artist_id = track['artists'][0]['id']
                genres = api_artist(artist_id)['genres']
                cur.execute('''
                    INSERT INTO raw_spotify (gid, album_id, album_release_date, album_spotify_url, album_small_thumbnail_url, small_thumbnail_size, album_big_thumbnail_url, big_thumbnail_size, track_id, track_spotify_url, track_name, genres)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (gid, album_id, release_date, album_spotify_url, smallest_thumbnail, smallest_size, biggest_thumbnail, biggest_size,
                    track_id, track_spotify_url, track_name, ','.join(genres)))
                conn.commit()
                time.sleep(0.2)
            except Exception as e:
                print(gid, artist_name, album_name, e)
                # import traceback
                # traceback.print_exc()
            print(f'{round((amount / total) * 100, 2)}%')

if __name__ == '__main__':
    main()