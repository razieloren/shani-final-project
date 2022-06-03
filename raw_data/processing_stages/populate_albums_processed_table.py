#!/usr/bin/env python3

import io
from re import A
import zlib
import sqlite3
import argparse

from PIL import Image

URBAN_LABLES = [
    'Urban design',
    'City',
    'Signage',
    'Street light',
    'Street',
    'Car',
    'Asphalt',
    'Automotive exterior',
    'Road surface',
    'Skyscraper',
    'Monument',
    'Office supplies',
    'Architecture',
    'Naval architecture',
    'Building',
    'Mode of transport',
    'Interior design',
]
URBAN_LABLES = list(map(lambda x: x.lower(), URBAN_LABLES))

MUSICAL_LABELS = [
    'Music',
    'Musical instrument',
    'Musician',
    'Guitar accessory',
    'String instrument',
    'Musical instrument accessory',
    'String instrument accessory',
    'Music artist',
    'Plucked string instruments',
    'Microphone',
    'Band plays',
    'Drum',
    'Performance art',
    'Piano',
    'Music venue',
    'Jazz pianist',
]
MUSICAL_LABELS = list(map(lambda x: x.lower(), MUSICAL_LABELS))

GEOMETRIC_LABLES = [
    'Circle',
    'Triangle',
    'Square',
    'Fractal art',
]
GEOMETRIC_LABLES = list(map(lambda x: x.lower(), GEOMETRIC_LABLES))

FASHION_LABELS = [
    'Fashion design',
    'Street fashion',
    'Fashion',
    'Fashion accessory',
    'Sunglasses',
    'Fashion model',
    'Costume design',
]
FASHION_LABELS = list(map(lambda x: x.lower(), FASHION_LABELS))

DRAWING_LABELS = [
    'Illustration',
    'Visual arts',
    'Painting',
    'Drawing',
    'Cg artwork',
    'Cartoon',
    'Graffiti',
    'Art paint',
    'Line art',
    'Animated cartoon',
    'Ink',
    'Watercolor paint',
    'Sketch',
]
DRAWING_LABELS = list(map(lambda x: x.lower(), DRAWING_LABELS))

PHOTOGRAPHY_LABELS = [
    'Flash photography',
    'Photo caption',
    'Monochrome photography',
    'Photograph',
    'Snapshot',
    'Stock photography',
    'Action film',
    'Still life photography',
    'Macro photography',
]
PHOTOGRAPHY_LABELS = list(map(lambda x: x.lower(), PHOTOGRAPHY_LABELS))

cover_cache = {}
def get_cover_art_dimensions(cur, gid):
    global cover_cache
    if gid in cover_cache:
        return cover_cache[gid]
    cur.execute('''
        SELECT cover_art
        FROM album
        WHERE gid = ?
    ''', (gid, ))
    compressed_blob = cur.fetchone()[0]
    try:
        decomp = zlib.decompress(compressed_blob)
        image = Image.open(io.BytesIO(decomp))
    except Exception:
        print('Error in', gid)
        return None, None
    width, height = image.size
    cover_cache[gid] = (width, height)
    return width, height

def prepare_tables(cur):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS album_processed_final (
            gid TEXT PRIMARY KEY,
            album_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            release_year INTEGER NOT NULL,
            colors TEXT,
            faces TEXT,
            persons TEXT,
            text_blocks TEXT,
            urban INTEGER NOT NULL,
            musical INTEGER NOT NULL,
            geometric INTEGER NOT NULL,
            fashion INTEGER NOT NULL,
            drawing INTEGER NOT NULL,
            photography INTEGER NOT NULL,
            small_thumbnail TEXT NOT NULL,
            big_thumbnail TEXT NOT NULL,
            track_name TEXT NOT NULL,
            track_url TEXT NOT NULL,
            genre TEXT NOT NULL,
            face_ratio REAL NOT NULL,
            text_ratio REAL NOT NULL,
            persons_ratio REAL NOT NULL,
            youtube_link TEXT NOT NULL
        );
        '''
    )

def parse_args():
    args = argparse.ArgumentParser(description='Generate processed2 table')
    args.add_argument('-d', '--db', help='DB file', default='albums_no_imgs.sqlite')
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect('albums.sqlite') as conn2:
        cur2 = conn2.cursor()
        with sqlite3.connect(args.db) as conn:
            data = {}
            cur = conn.cursor()
            prepare_tables(cur)
            cur.execute('''
                SELECT a.gid, a.name, a.artist, a.release_year, r.album_small_thumbnail_url, r.album_big_thumbnail_url, r.track_name, r.track_spotify_url, r.genres, ap.face_ratio, ap.text_ratio, ry.link
                FROM album AS a
                LEFT JOIN raw_spotify AS r ON a.gid = r.gid
                LEFT JOIN album_processed AS ap ON a.gid = ap.gid
                LEFT JOIN raw_youtube AS ry ON a.gid = ry.gid
                WHERE r.track_name IS NOT NULL AND r.genres NOT LIKE '' AND ap.face_ratio IS NOT NULL AND ry.link IS NOT NULL
            ''')
            for album in cur.fetchall():
                gid, album_name, artist_name, release_year, small_thumb, big_thumb, track_name, track_spotify_url, genres, face_ratio, text_ratio, link = album
                width, height = get_cover_art_dimensions(cur2, gid)
                if width is None:
                    continue
                data[gid] = {
                    'album_name': album_name,
                    'artist_name': artist_name,
                    'release_year': release_year,
                    'small_thumbnail': small_thumb,
                    'big_thumbnail': big_thumb,
                    'track_name': track_name,
                    'track_url': track_spotify_url,
                    'youtube_link': link,
                    'genre': genres.split(',')[0].title(),
                    'urban': False,
                    'musical': False,
                    'geometric': False,
                    'fashion': False,
                    'drawing': False,
                    'photography': False,
                    'colors': None,
                    'faces': None,
                    'persons': None,
                    'text_blocks': None,
                    'face_ratio': face_ratio,
                    'text_ratio': text_ratio,
                    'width': width,
                    'height': height
                }
            i = 0
            filtered_albums = {}
            for gid, values in data.items():
                i += 1
                print(i)
                width, height = values['width'], values['height']
                cur.execute('''
                    SELECT l.description
                    FROM raw_label AS l
                    WHERE l.gid = ?
                ''', (gid, ))
                has_label = False
                for label in cur.fetchall():
                    label = label[0]
                    if label.lower() in URBAN_LABLES:
                        values['urban'] = True
                        has_label = True
                    if label.lower() in MUSICAL_LABELS:
                        values['musical'] = True
                        has_label = True
                    if label.lower() in GEOMETRIC_LABLES:
                        values['geometric'] = True
                        has_label = True
                    if label.lower() in FASHION_LABELS:
                        values['fashion'] = True
                        has_label = True
                    if label.lower() in DRAWING_LABELS:
                        values['drawing'] = True
                        has_label = True
                    if label.lower() in PHOTOGRAPHY_LABELS:
                        values['photography'] = True
                        has_label = True
                if not has_label:
                    print('Skipping', gid, 'because it has no lables')
                    continue
                
                cur.execute('''
                    SELECT red, green, blue, score, pixel_fraction
                    FROM raw_color
                    WHERE gid = ?
                ''', (gid, ))
                colors = []
                for color in cur.fetchall():
                    red, green, blue, score, fraction = color
                    if score < 0.01:
                        continue
                    colors.append(','.join(list(map(lambda x: str(x), [red, green, blue, fraction]))))
                if len(colors) == 0:
                    print('Skipping', gid, 'because it has no colors')
                    continue
                if len(colors) > 0:
                    values['colors'] = '|'.join(colors)
                
                cur.execute('''
                    SELECT x1, y1, x2, y2, x3, y3, x4, y4
                    FROM raw_face
                    WHERE gid = ?
                ''', (gid, ))
                faces = []
                for face in cur.fetchall():
                    x1, y1, x2, y2, x3, y3, x4, y4 = face
                    faces.append(','.join(list(map(lambda x: str(x), [x1 / width, y1 / height, x2 / width, 
                        y2 / height, x3 / width, y3 / height, x4 / width, y4 / height]))))
                if len(faces) > 0:
                    values['faces'] = '|'.join(faces)

                cur.execute('''
                    SELECT x1, y1, x2, y2, x3, y3, x4, y4
                    FROM raw_text_block
                    WHERE gid = ?
                ''', (gid, ))
                texts = []
                for text in cur.fetchall():
                    x1, y1, x2, y2, x3, y3, x4, y4 = text
                    texts.append(','.join(list(map(lambda x: str(x), [x1 / width, y1 / height, x2 / width, y2 / height, 
                        x3 / width, y3 / height, x4 / width, y4 / height]))))
                if len(texts) > 0:
                    values['text_blocks'] = '|'.join(texts)

                cur.execute('''
                    SELECT x1, y1, x2, y2, x3, y3, x4, y4
                    FROM raw_persons
                    WHERE gid = ?
                ''', (gid, ))
                persons = []
                perons_area = 0
                for person in cur.fetchall():
                    x1, y1, x2, y2, x3, y3, x4, y4 = person
                    persons.append(','.join(list(map(lambda x: str(x), [x1, y1, x2, y2, 
                        x3, y3, x4, y4]))))
                    one = abs(x2 - x1) * values['width']
                    two = abs(y3 - y2) * values['height']
                    perons_area += one * two
                persons_ratio = min(1, perons_area / (values['width'] * values['height']))
                if len(persons) > 0:
                    values['persons'] = '|'.join(persons)
                values['persons_ratio'] = persons_ratio
                filtered_albums[gid] = values

            for gid, values in filtered_albums.items():
                cur.execute('''
                    INSERT INTO album_processed_final (gid, album_name, artist_name, release_year, colors, 
                        faces, persons, text_blocks, urban, musical, geometric, fashion, drawing, 
                        photography, small_thumbnail, big_thumbnail, track_name, track_url, genre, face_ratio, text_ratio, persons_ratio, youtube_link)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (gid, values['album_name'], values['artist_name'], values['release_year'], values['colors'], 
                        values['faces'], values['persons'], values['text_blocks'], values['urban'], 
                        values['musical'], values['geometric'], values['fashion'], values['drawing'], 
                        values['photography'], values['small_thumbnail'],
                        values['big_thumbnail'], values['track_name'], values['track_url'], values['genre'], 
                        values['face_ratio'], values['text_ratio'], values['persons_ratio'], values['youtube_link']))
            

        
        


if __name__ == '__main__':
    main()