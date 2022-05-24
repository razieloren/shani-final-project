#!/usr/bin/env python3

import csv
import zlib
import string
import sqlite3
import psycopg2
import argparse
import requests

ALLOWED_TAGS = [
    'acid breaks',
    'acid house',
    'acid jazz',
    'acid rock',
    'acid techno',
    'acid trance',
    'acoustic blues',
    'acoustic rock',
    'alternative country',
    'alternative dance',
    'alternative folk',
    'alternative hip hop',
    'alternative metal',
    'alternative pop',
    'alternative punk',
    'alternative rock',
    'ambient',
    'ambient dub',
    'ambient house',
    'ambient pop',
    'ambient techno',
    'ambient trance',
    'black metal',
    'blues',
    'blues rock',
    'classic blues',
    'classic country',
    'classic jazz',
    'classic rock',
    'classical',
    'country',
    'country blues',
    'country boogie',
    'country folk',
    'country pop',
    'country rap',
    'country rock',
    'country soul',
    'dance',
    'dance-pop',
    'dance-punk',
    'dance-rock',
    'death metal',
    'disco',
    'dubstep',
    'electric blues',
    'electro',
    'electro house',
    'emo',
    'folk',
    'folk metal',
    'folk pop',
    'folk punk',
    'folk rock',
    'funk',
    'fusion',
    'gothic',
    'hip hop',
    'indie',
    'indie folk',
    'indie pop',
    'indie rock',
    'industrial',
    'instrumental',
    'j-pop',
    'jazz',
    'jazz blues',
    'jazz fusion',
    'jazz rap',
    'jazz rock',
    'jazz-funk',
    'k-pop',
    'latin',
    'metal',
    'musical',
    'opera',
    'pop',
    'pop metal',
    'pop punk',
    'pop rap',
    'pop rock',
    'pop soul',
    'progressive',
    'progressive bluegrass',
    'progressive breaks',
    'progressive country',
    'progressive electronic',
    'progressive folk',
    'progressive house',
    'progressive metal',
    'progressive pop',
    'progressive rock',
    'progressive trance',
    'punk',
    'r&b',
    'rap metal',
    'rap rock',
    'rock',
    'rock and roll',
    'salsa',
    'samba',
    'soul',
    'soul blues',
    'soul jazz',
    'techno',
]

def get_cover_art(gid):
    res = requests.get(f'https://coverartarchive.org/release/{gid}')
    try:
        images = res.json()['images']
        front_images = {}
        for image in images:
            if image['front'] and 'Front' in image['types']:
                front_images[image['edit']] = image['image']
        if len(front_images) == 0:
            return images[0]['image']
        return front_images[min(front_images.keys())]
    except Exception as e:
        print(f'Could not fetch cover art for {gid}: {e}')

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
            release_year INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            rating_count INTERGER NOT NULL,
            genres TEXT NOT NULL,
            cover_art BLOB NOT NULL
        );
        '''
    )

def main():
    albums = {}
    args = parse_args()
    with open(args.infile, 'r') as csv_file:
        for row in csv.reader(csv_file):
            rg_id, gid, album, artist, release_year, rating, rating_count = row
            should_skip = False
            for c in artist + album:
                if c not in string.printable:
                    should_skip = True
                    break
            if should_skip:
                continue
            if gid not in albums:
                albums[gid] = {
                    'rg_id': rg_id,
                    'gid': gid,
                    'album': album,
                    'artist': [artist],
                    'release_year': release_year,
                    'rating': int(rating),
                    'rating_count': int(rating_count)
                }
            else:
                if artist not in albums[gid]['artist']:
                    albums[gid]['artist'].append(artist)
    albums_unique = {}
    for gid, values in albums.items():
        key = f'{values["album"]}__{values["artist"]}'
        if key not in albums_unique:
            albums_unique[key] = {
                'rg_id': rg_id,
                'gid': gid,
                'album': values['album'],
                'artist': values['artist'],
                'release_year': values['release_year'],
                'rating': values['rating'],
                'rating_count': values['rating_count']
            }
        else:
            if values['release_year'] < albums_unique[key]['release_year']:
                albums_unique[key]['rg_id'] = values['rg_id']
                albums_unique[key]['gid'] = values['gid']
                albums_unique[key]['release_year'] = values['release_year']
    print('Total unique albums:', len(albums_unique))
    with psycopg2.connect("dbname='musicbrainz_db' user='musicbrainz' password='musicbrainz' host='localhost' port=5433") as conn:
        for album in albums_unique.values():
            cur = conn.cursor()
            cur.execute(f'''
                SELECT t.name
                FROM musicbrainz.release_group_tag AS rt
                LEFT JOIN musicbrainz.tag AS t ON rt.tag = t.id
                WHERE rt.release_group = {album["rg_id"]}
            ''')
            album['genres'] = ','.join([x[0] for x in cur.fetchall() if x[0] in ALLOWED_TAGS])

    with sqlite3.connect(args.output) as conn:
        prepare_tables(conn)
        cur = conn.cursor()
        i = 0
        for _, values in albums_unique.items():
            try:
                i += 1
                cover_art_link = get_cover_art(values['gid'])
                cover_art_bytes = requests.get(cover_art_link).content
                cover_art_compressed = zlib.compress(cover_art_bytes)
                print(f'Cover art {values["gid"]} size: {len(cover_art_bytes)} -> {len(cover_art_compressed)}')
                cur.execute(f'''
                    INSERT INTO album (gid, name, artist, release_year, rating, rating_count, genres, cover_art)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                ''', (values['gid'], values['album'], ','.join(values['artist']), values['release_year'], values['rating'], values['rating_count'], values['genres'], cover_art_compressed))
                conn.commit()
                print(round((i / len(albums_unique)) * 100, 2), '%')
            except Exception as e:
                print(f'Error while commiting {values["gid"]}: {e}, skipping')
        print('Done')

if __name__ == '__main__':
    main()