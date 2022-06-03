#!/usr/bin/env python3

import math
import sqlite3
import argparse

from operator import itemgetter

BIGGEST_COLOR_DISTANCE = math.sqrt(math.pow(255, 2) + math.pow(255, 2) + math.pow(255, 2))

def parse_args():
    args = argparse.ArgumentParser(description='Export DB to JSON')
    args.add_argument('-d', '--db', help='DB file', default='albums_no_imgs.sqlite')
    return args.parse_args()

# Color distance, dom color distance, person ratio distance

def feature_3d_distance(p1, p2, normalize_to=255):
    x1, y1, z1 = list(map(lambda x: x / normalize_to, p1))
    x2, y2, z2 = list(map(lambda x: x / normalize_to, p2))
    return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2) + math.pow(z2 - z1, 2))

def feature_1d_distance(p1, p2):
    return abs(p2 - p1)

def feature_color_distance(colors1, colors2):
    r1, g1, b1 = 0, 0, 0
    for c in colors1:
        r1 += c[0] * c[-1]
        g1 += c[1] * c[-1]
        b1 += c[2] * c[-1]
    r2, g2, b2 = 0, 0, 0
    for c in colors2:
        r2 += c[0] * c[-1]
        g2 += c[1] * c[-1]
        b2 += c[2] * c[-1]
    return feature_3d_distance((r1, g1, b1), (r2, g2, b2)) / BIGGEST_COLOR_DISTANCE

def feature_dominant_color(colors1, colors2):
    return feature_1d_distance(colors1[0][-1], colors2[0][-1])

def feature_lables_distance(a1, a2):
    num_different = 0
    if a1.urban != a2.urban:
        num_different += 1
    if a1.musical != a2.musical:
        num_different += 1
    if a1.geometric != a2.geometric:
        num_different += 1
    if a1.fashion != a2.fashion:
        num_different += 1
    if a1.drawing != a2.drawing:
        num_different += 1
    if a1.photography != a2.photography:
        num_different += 1
    return num_different / 6

def feature_objects_distance(a1, a2):
    m = max(len(a1.faces) + len(a1.persons), len(a2.faces) + len(a2.persons))
    if m == 0:
        return 0
    return feature_1d_distance(len(a1.faces) + len(a1.persons), len(a2.faces) + len(a2.persons)) / m

def feature_text_blocks_distance(a1, a2):
    m = max(len(a1.text_blocks), len(a2.text_blocks))
    if m == 0:
        return 0
    return feature_1d_distance(len(a1.text_blocks), len(a2.text_blocks)) / m

def calc_neighbour_score(a1, a2):
    # Function, normalize (to 0-1 range), weight
    scores = [
        (feature_color_distance(a1.colors, a2.colors), 288, 6),
        (feature_dominant_color(a1.colors, a2.colors), 1, 5),
        (feature_1d_distance(a1.text_ratio, a2.text_ratio), 1, 3),
        (feature_1d_distance(a1.persons_ratio, a2.persons_ratio), 1, 3),
        (feature_lables_distance(a1, a2), 1, 1),
        (feature_objects_distance(a1, a2), 1, 4),
        (feature_text_blocks_distance(a1, a2), 1, 3),
    ]
    total = 0
    total_weight = sum([e[2] for e in scores])
    for score, _, w in scores:
        total += (score * (w / total_weight))
    return total

class Album(object):
    def __init__(self, gid, colors, faces, persons, text_blocks, urban, musical, geometric, fashion, drawing, photography, face_ratio, text_ratio, persons_ratio):
        self.gid = gid
        self.colors = [] if colors is None else [list(map(float, e.split(','))) for e in colors.split('|')]
        self.faces = [] if faces is None else [list(map(float, e.split(','))) for e in faces.split('|')]
        self.persons = [] if persons is None else [list(map(float, e.split(','))) for e in persons.split('|')]
        self.text_blocks = [] if text_blocks is None else [list(map(float, e.split(','))) for e in text_blocks.split('|')]
        self.urban = urban
        self.musical = musical
        self.geometric = geometric
        self.fashion = fashion
        self.drawing = drawing
        self.photography = photography
        self.face_ratio = face_ratio
        self.text_ratio = text_ratio
        self.persons_ratio = persons_ratio
        self.ns = []

def main():
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        cur = conn.cursor()
        cur.execute(f'''
            SELECT gid, colors, faces, persons, text_blocks, urban, musical, geometric, fashion, drawing, photography, face_ratio, text_ratio, persons_ratio
            FROM album_processed3
        ''')
        albums = []
        for album in cur.fetchall():
            gid, colors, faces, persons, text_blocks, urban, musical, geometric, fashion, drawing, photography, face_ratio, text_ratio, persons_ratio = album
            albums.append(Album(gid, colors, faces, persons, text_blocks, urban, musical, geometric, fashion, drawing, photography, face_ratio, text_ratio, persons_ratio))
        neighbours = {}
        for j, album1 in enumerate(albums[:600]):
            print(j)
            neighbours[album1.gid] = []
            for album2 in albums[:600]:
                if album1.gid != album2.gid:
                    score = calc_neighbour_score(album1, album2)
                    if len(neighbours[album1.gid]) == 0:
                        neighbours[album1.gid].append((album2.gid, score))
                    else:
                        for i, element in enumerate(neighbours[album1.gid]):
                            if score < element[1]:
                                neighbours[album1.gid].insert(i, (album2.gid, score))
                                break
                        if len(neighbours[album1.gid]) > 10:
                            neighbours[album1.gid].pop()

        for album, nei in neighbours.items():
            print(album)
            for n in nei:
                print('\t', n)
            

if __name__ == '__main__':
    main()