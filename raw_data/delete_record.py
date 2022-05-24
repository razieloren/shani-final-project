#!/usr/bin/env python3

import sqlite3
import argparse

def parse_args():
    args = argparse.ArgumentParser(description='Delete Record')
    args.add_argument('-i', '--infile', help='Input DB file', required=True)
    args.add_argument('-g', '--gid', help='GID to delete', required=True)
    return args.parse_args()

def main():
    args = parse_args()
    with sqlite3.connect(args.infile) as conn:
        cur = conn.cursor()
        cur.execute('''
            DELETE FROM album
            WHERE gid = ?
        ''', (args.gid,))
        conn.commit()

if __name__ == '__main__':
    main()