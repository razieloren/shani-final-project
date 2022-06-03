#!/usr/bin/env python3

import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Delete Record')
    args.add_argument('-i', '--infile', help='Input DB file', required=True)
    args.add_argument('-t', '--table', help='Table to drop', required=True)
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect(args.infile) as conn:
        cur = conn.cursor()
        cur.execute(f'''
            DROP TABLE {args.table}
        ''')
        conn.commit()

if __name__ == '__main__':
    main()