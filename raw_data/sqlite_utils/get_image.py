#!/usr/bin/env python3

import zlib
import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Export image from albums DB')
    args.add_argument('-g', '--gid', help='GID to export image', required=True)
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect('albums.sqlite') as conn:
        cur = conn.cursor()
        cur.execute('''SELECT cover_art FROM album WHERE gid = ?''', (args.gid, ))
        cover_art = cur.fetchall()[0][0]
        with open('./dump.jpg', 'wb') as f:
            f.write(zlib.decompress(cover_art))

if __name__ == '__main__':
    main()