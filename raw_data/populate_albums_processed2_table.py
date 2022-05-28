#!/usr/bin/env python3

import sqlite3
import argparse

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

ANIMAL_LABELS = [
    'Mammal',
    'Terrestrial animal',
    'Working animal',
    'Carnivore',
    'Dog',
    'Fish',
    'Bride',
    'Dog breed',
    'Companion dog',
    'Horse',
    'Butterfly',
    'Big cats',
    'Wings',
    'Pack animal',
    'Cat',
]
ANIMAL_LABELS = list(map(lambda x: x.lower(), ANIMAL_LABELS))

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

FINE_ARTS_LABELS = [
    'art paint',
    'Modern art',
    'Visual arts',
    'Sculpture',
]
FINE_ARTS_LABELS = list(map(lambda x: x.lower(), FINE_ARTS_LABELS))

NATURE_LABELS = [
    'Sky',
    'Wood',
    'People in nature',
    'Tree',
    'Cloud',
    'Natural landscape',
    'Nature',
    'Grass',
    'Terrestrial plant',
    'Natural environment',
    'Petal',
    'Branch',
    'Flower',
    'Geological phenomenon',
    'Aqua',
    'Atmospheric phenomenon',
    'Vegetation',
    'Mountain',
    'Botany',
    'Grassland',
    'Leaf',
    'Moon',
    'Flowering plant',
    'Lake',
    'Star',
    'Natural material',
    'Underwater',
    'Sunset',
    'Mountainous landforms',
    'Beach',
    'Rose',
    'Full moon',
    'Water resources',
    'Wind wave',
    'Annual plant',
    'Ocean',
]
NATURE_LABELS = list(map(lambda x: x.lower(), NATURE_LABELS))

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

def prepare_tables(cur):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS album_processed (
            gid TEXT PRIMARY KEY,
            album_name TEXT NOT NULL,
            artist_name TEXT NOT NULL,
            release_yeat INTEGER NOT NULL,
            colors TEXT,
            faces TEXT,
            text_blocks TEXT,
            urban INTEGER NOT NULL,
            animal INTEGER NOT NULL,
            musical INTEGER NOT NULL,
            fine_arts INTEGER NOT NULL,
            nature INTEGER NOT NULL,
            geometric INTEGER NOT NULL,
            fashion INTEGER NOT NULL,
            drawing INTEGER NOT NULL,
            photography INTEGER NOT NULL,
            small_thumbnail TEXT NOT NULL,
            big_thumbnail TEXT NOT NULL,
            track_name TEXT NOT NULL,
            genre TEXT NOT NULL
        );
        '''
    )

def parse_args():
    args = argparse.ArgumentParser(description='Generate processed2 table')
    args.add_argument('-d', '--db', help='DB file', default='albums_no_imgs.sqlite')
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        data = {}
        cur = conn.cursor()
        prepare_tables(cur)
        cur.execute('''
            SELECT a.gid, a.name, a.artist, a.release_year, r.album_small_thumbnail_url, r.album_big_thumbnail_url, r.track_name, r.genres
            FROM album AS a
            LEFT JOIN raw_spotify AS r ON a.gid = r.gid
            WHERE r.track_name IS NOT NULL AND r.genres NOT LIKE ''
        ''')
        for album in cur.fetchall():
            gid, album_name, artist_name, release_year, small_thumb, big_thumb, track_name, genres = album
            data[gid] = {
                'album_name': album_name,
                'artist_name': artist_name,
                'release_year': release_year,
                'small_thumbnail': small_thumb,
                'big_thumbnail': big_thumb,
                'track_name': track_name,
                'genre': genres.split(',')[0].title(),
                'urban': False,
                'animal': False,
                'musical': False,
                'fine_arts': False,
                'nature': False,
                'geometric': False,
                'fashion': False,
                'drawing': False,
                'photography': False,
                'colors': None,
                'faces': None,
                'text_blocks': None
            }

        for gid, values in data.items():
            cur.execute('''
                SELECT l.description
                FROM raw_label AS l
                WHERE l.gid = ?
            ''', (gid, ))
            for label in cur.fetchall():
                label = label[0]
                if label.lower() in URBAN_LABLES:
                    values['urban'] = True
                if label.lower() in ANIMAL_LABELS:
                    values['animal'] = True
                if label.lower() in MUSICAL_LABELS:
                    values['musical'] = True
                if label.lower() in FINE_ARTS_LABELS:
                    values['fine_arts'] = True
                if label.lower() in NATURE_LABELS:
                    values['nature'] = True
                if label.lower() in GEOMETRIC_LABLES:
                    values['geometric'] = True
                if label.lower() in FASHION_LABELS:
                    values['fashion'] = True
                if label.lower() in DRAWING_LABELS:
                    values['drawing'] = True
                if label.lower() in PHOTOGRAPHY_LABELS:
                    values['photography'] = True
            
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
                # TODO: Normalize points with original height / width
                faces.append(','.join(list(map(lambda x: str(x), [x1, y1, x2, y2, x3, y3, x4, y4]))))
            if len(faces) > 0:
                values['faces'] = '|'.join(faces)

            cur.execute('''
                SELECT x1, y1, x2, y2, x3, y3, x4, y4
                FROM raw_text
                WHERE gid = ?
            ''', (gid, ))
            texts = []
            for text in cur.fetchall():
                x1, y1, x2, y2, x3, y3, x4, y4 = text
                # TODO: Normalize points with original height / width
                texts.append(','.join(list(map(lambda x: str(x), [x1, y1, x2, y2, x3, y3, x4, y4]))))
            if len(texts) > 0:
                values['text_blocks'] = '|'.join(texts)
            

        
        


if __name__ == '__main__':
    main()