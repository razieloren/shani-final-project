#!/usr/bin/env python3

import io
import zlib
import sqlite3
import argparse

from PIL import Image

def parse_args():
    args = argparse.ArgumentParser(description='Final Processed Albums Table')
    args.add_argument('-d', '--db', help='Output DB file', default='albums.sqlite')
    return args.parse_args()

def prepare_tables(cur):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS album_processed (
            gid TEXT PRIMARY KEY,
            cover_area INTEGER NOT NULL,
            red INTEGER,
            green INTEGER,
            blue INTEGER,
            face_ratio REAL,
            is_joy INTEGER,
            is_sorrow INTEGER,
            is_anger INTEGER,
            is_surprised INTEGER,
            is_blurred INTEGER,
            first_label TEXT,
            second_label TEXT,
            third_label TEXT,
            text_ratio REAL
        );
        '''
    )

def get_all_gids(cur):
    cur.execute('''
        SELECT gid
        FROM album
    ''')
    return map(lambda x: x[0], cur.fetchall())

def get_cover_art(cur, gid):
    cur.execute('''
        SELECT cover_art
        FROM album
        WHERE gid = ?
    ''', (gid, ))
    compressed_blob = cur.fetchone()[0]
    return zlib.decompress(compressed_blob)

def get_colors(cur, gid):
    cur.execute('''
        SELECT red, green, blue, score
        FROM raw_color
        WHERE gid = ?
    ''', (gid, ))
    return cur.fetchall()

def get_faces(cur, gid):
    cur.execute('''
        SELECT x1, y1, x2, y2, x3, y3, x4, y4, joy, sorrow, anger, surprised, blurred
        FROM raw_face
        WHERE gid = ?
    ''', (gid, ))
    return cur.fetchall()

def get_labels(cur, gid):
    cur.execute('''
        SELECT description
        FROM raw_label
        WHERE gid = ?
        ORDER BY score DESC
    ''', (gid, ))
    return map(lambda x: x[0], cur.fetchall())

def get_text(cur, gid):
    cur.execute('''
        SELECT x1, y1, x2, y2, x3, y3, x4, y4
        FROM raw_text_block
        WHERE gid = ?
    ''', (gid, ))
    return cur.fetchall()

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        cur = conn.cursor()
        prepare_tables(cur)
        conn.commit()
        for gid in get_all_gids(cur):
            cover_art = get_cover_art(cur, gid)
            try:
                image = Image.open(io.BytesIO(cover_art))
            except Exception:
                print('Error in', gid)
                continue
            width, height = image.size
            image_area = width * height

            best_color_score = 0
            red, green, blue = None, None, None
            for color in get_colors(cur, gid):
                score = color[-1]
                if score > best_color_score:
                    red, green, blue = color[0], color[1], color[2]

            face_area = 0
            is_joy, is_sorrow, is_anger, is_surprised, is_blurred = False, False, False, False, False
            for face in get_faces(cur, gid):
                x1, y1, x2, y2, x3, y3, x4, y4, joy, sorrow, anger, surprised, blurred = face
                if joy >= 4:
                    is_joy = True
                if sorrow >= 4:
                    is_sorrow = True
                if anger >= 4:
                    is_anger = True
                if surprised >= 4:
                    is_surprised = True
                if blurred >= 4:
                    is_blurred = True
                one = abs(x2 - x1)
                two = abs(y3 - y2)
                face_area += one * two
            face_ratio = min(1, face_area / image_area)

            labels = []
            for label in get_labels(cur, gid):
                if len(labels) == 3:
                    break
                labels.append(label)
            while len(labels) < 3:
                labels.append(None)

            text_area = 0
            for text in get_text(cur, gid):
                x1, y1, x2, y2, x3, y3, x4, y4 = text
                one = abs(x2 - x1)
                two = abs(y3 - y2)
                text_area += one * two
            text_ratio = min(1, text_area / image_area)
            '''
                        gid TEXT PRIMARY KEY,
            cover_area INTEGER NOT NULL,
            red INTEGER,
            green INTEGER,
            blue INTEGER,
            face_ratio REAL,
            is_joy INTEGER,
            is_sorrow INTEGER,
            is_anger INTEGER,
            is_surprised INTEGER,
            is_blurred INTEGER,
            first_label TEXT,
            second_label TEXT,
            third_label TEXT,
            text_ratio REAL'''
            cur.execute('''
                INSERT INTO album_processed (gid, cover_area, red, green, blue, face_ratio, is_joy, is_sorrow, is_anger, is_surprised, is_blurred, first_label, second_label, third_label, text_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (gid, image_area, red, green, blue, face_ratio, is_joy, is_sorrow, is_anger, 
                is_surprised, is_blurred, labels[0], labels[1], labels[2], text_ratio))
        conn.commit()


if __name__ == '__main__':
    main()