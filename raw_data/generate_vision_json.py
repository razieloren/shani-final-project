#!/usr/bin/env python3

import os
import zlib
import json
import sqlite3
import argparse
from google.cloud import vision_v1

os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS', 'musicscanner-349518-179fdfd94e23.json')

def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def get_cover_art(cur, gid):
    cur.execute('''
        SELECT cover_art
        FROM album
        WHERE gid = ?
    ''', (gid, ))
    compressed_blob = cur.fetchone()[0]
    return zlib.decompress(compressed_blob)

def get_all_gids(cur):
    cur.execute('''
        SELECT gid
        FROM album
    ''')
    return map(lambda x: x[0], cur.fetchall())   

def parse_args():
    args = argparse.ArgumentParser(description='Google Vision API Scraper')
    args.add_argument('-i', '--infile', help='Input DB file', required=True)
    args.add_argument('-o', '--output', help='Output JSON file', default='vision.json')
    return args.parse_args()

def main():
    args = parse_args()
    data = {}
    if os.path.exists(args.output):
        with open(args.output, 'r') as f:
            data = json.load(f)
    client = vision_v1.ImageAnnotatorClient()
    processed = 0
    with sqlite3.connect(args.infile) as conn:
        cur = conn.cursor()
        gids_list = list(filter(lambda x: x not in data, get_all_gids(cur)))
        gids_chunks = chunks(gids_list, 1)
        total_images = len(list(gids_list))
        for chunk in gids_chunks:
            requests = []
            temp_gids = []
            try:
                for gid in chunk:
                    temp_gids.append(gid)
                    content = get_cover_art(cur, gid)
                    image = vision_v1.types.Image(content=content)
                    requests.append({
                        'image': image,
                        'features': [
                            {"type_": vision_v1.Feature.Type.FACE_DETECTION},
                            {"type_": vision_v1.Feature.Type.IMAGE_PROPERTIES},
                            {"type_": vision_v1.Feature.Type.LABEL_DETECTION},
                            {"type_": vision_v1.Feature.Type.TEXT_DETECTION},
                        ]
                    })
                print(temp_gids)
                response = client.batch_annotate_images(requests=requests)
                for i, response in enumerate(response.responses):
                    serialized_proto_plus = vision_v1.AnnotateImageResponse.serialize(response)
                    desrialized = vision_v1.AnnotateImageResponse.deserialize(serialized_proto_plus)
                    response_json = vision_v1.AnnotateImageResponse.to_json(desrialized)
                    data[temp_gids[i]] = json.loads(response_json)
                processed += 1
                print(f'Processed {round((processed / total_images) * 100, 2)}%')
            except Exception as e:
                print(f'Exception: {e}, moving on')
    with open(args.output, 'w') as f:
        f.write(json.dumps(data))

if __name__ == '__main__':
    main()