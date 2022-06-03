#!/usr/bin/env python3

import json
import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Google Vision JSON Parser')
    args.add_argument('-i', '--infile', help='Input JSON file', required=True)
    args.add_argument('-o', '--output', help='Output DB file', default='albums.sqlite')
    return args.parse_args()

def prepare_tables(cur):
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS raw_face (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT NOT NULL,
            x1 INTEGER NOT NULL,
            y1 INTEGER NOT NULL,
            x2 INTEGER NOT NULL,
            y2 INTEGER NOT NULL,
            x3 INTEGER NOT NULL,
            y3 INTEGER NOT NULL,
            x4 INTEGER NOT NULL,
            y4 INTEGER NOT NULL,
            joy INTEGER NOT NULL,
            sorrow INTEGER NOT NULL,
            anger INTEGER NOT NULL,
            surprised INTEGER NOT NULL,
            blurred INTEGER NOT NULL
        );
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS raw_label (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT NOT NULL,
            description TEXT NOT NULL,
            score REAL NOT NULL,
            topicality REAL NOT NULL
        );
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS raw_color (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT NOT NULL,
            red REAL NOT NULL,
            green REAL NOT NULL,
            blue REAL NOT NULL,
            score REAL NOT NULL,
            pixel_fraction REAL NOT NULL
        );
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS raw_text_block (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT NOT NULL,
            x1 INTEGER NOT NULL,
            y1 INTEGER NOT NULL,
            x2 INTEGER NOT NULL,
            y2 INTEGER NOT NULL,
            x3 INTEGER NOT NULL,
            y3 INTEGER NOT NULL,
            x4 INTEGER NOT NULL,
            y4 INTEGER NOT NULL,
            text TEXT NOT NULL
        );
        '''
    )
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS raw_persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gid TEXT NOT NULL,
            x1 INTEGER NOT NULL,
            y1 INTEGER NOT NULL,
            x2 INTEGER NOT NULL,
            y2 INTEGER NOT NULL,
            x3 INTEGER NOT NULL,
            y3 INTEGER NOT NULL,
            x4 INTEGER NOT NULL,
            y4 INTEGER NOT NULL
        );
        '''
    )
    

def main():
    args = parse_args()
    with open(args.infile, 'r') as f:
        data = json.load(f)
    with sqlite3.connect(args.output) as conn:
        cur = conn.cursor()
        prepare_tables(cur)
        conn.commit()
        amount = 0
        for gid, attrs in data.items():
            amount += 1
            # for annot in attrs['faceAnnotations']:
            #     p = annot['fdBoundingPoly']['vertices']
            #     cur.execute('''
            #         INSERT INTO raw_face (gid, x1, y1, x2, y2, x3, y3, x4, y4, joy, sorrow, anger, surprised, blurred)
            #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            #     ''', (gid, p[0]['x'], p[0]['y'], p[1]['x'], p[1]['y'], p[2]['x'], p[2]['y'], p[3]['x'], p[3]['y'], 
            #         annot['joyLikelihood'], annot['sorrowLikelihood'], annot['angerLikelihood'], annot['surpriseLikelihood'],
            #         annot['blurredLikelihood']))
            # for annot in attrs['labelAnnotations']:
            #     cur.execute('''
            #         INSERT INTO raw_label (gid, description, score, topicality)
            #         VALUES (?, ?, ?, ?)
            #     ''', (gid, annot['description'], annot['score'], annot['topicality']))
            # if 'imagePropertiesAnnotation' in attrs:
            #     for annot in attrs['imagePropertiesAnnotation']['dominantColors']['colors']:
            #         cur.execute('''
            #             INSERT INTO raw_color (gid, red, green, blue, score, pixel_fraction)
            #             VALUES (?, ?, ?, ?, ?, ?)
            #         ''', (gid, annot['color']['red'], annot['color']['green'], annot['color']['blue'], 
            #                 annot['score'], annot['pixelFraction']))
            if 'fullTextAnnotation' in attrs:
                for page in attrs['fullTextAnnotation']['pages']:
                    for block in page['blocks']:
                        for paragrpah in block['paragraphs']:
                            text = ''
                            p = paragrpah['boundingBox']['vertices']
                            for word in paragrpah['words']:
                                for symbol in word['symbols']:
                                    text += symbol['text']
                            cur.execute('''
                                INSERT INTO raw_text_block (gid, x1, y1, x2, y2, x3, y3, x4, y4, text)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (gid, p[0]['x'], p[0]['y'], p[1]['x'], p[1]['y'], p[2]['x'], p[2]['y'], p[3]['x'], p[3]['y'], text))
            # if 'localizedObjectAnnotations' in attrs:
            #     for obj in attrs['localizedObjectAnnotations']:
            #         if str(obj['name']) == 'Person':
            #             p = obj['boundingPoly']['normalizedVertices']
            #             cur.execute('''
            #                 INSERT INTO raw_persons (gid, x1, y1, x2, y2, x3, y3, x4, y4)
            #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            #             ''', (gid, p[0]['x'], p[0]['y'], p[1]['x'], p[1]['y'], p[2]['x'], p[2]['y'], p[3]['x'], p[3]['y']))
            conn.commit()
            print(f'{round((amount / len(data)) * 100, 2)}%')

if __name__ == '__main__':
    main()