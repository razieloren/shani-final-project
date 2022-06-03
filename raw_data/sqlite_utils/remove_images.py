#!/usr/bin/env python3

import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Deletes raw images from DB')
    args.add_argument('-i', '--infile', help='Input DB file', required=True)
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect(args.infile) as conn:
        cur = conn.cursor()
        cur.execute(f'''
            UPDATE album
            SET cover_art = 'a';
        ''')
        cur.execute(f'''
            vacuum;  
        ''')
        conn.commit()

if __name__ == '__main__':
    main()