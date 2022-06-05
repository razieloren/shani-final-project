import sqlite3

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    albums = {'error': None, 'albums': {}}
    try:
        with sqlite3.connect('albums.sqlite') as conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT gid, big_thumbnail
                FROM album_processed3
            ''')
            for gid, thumb in cur.fetchall():
                albums['albums'][gid] = thumb
            cur.close()
    except Exception as e:
        albums['error'] = str(e)
    return albums

# @app.get("/album/{gid}")
# async def album(gid: str):
#     albums = {'error': None, 'album': {'gid': gid}}
#     try:
#         with sqlite3.connect('albums.sqlite') as conn:
#             cur = conn.cursor()
#             cur.execute('''
#                 SELECT album_name, artist_name, release_year, 
#                 FROM album_processed3
#             ''')
#             for gid, thumb in cur.fetchall():
#                 albums['albums'][gid] = thumb
#             cur.close()
#     except Exception as e:
#         albums['error'] = str(e)
#     return albums