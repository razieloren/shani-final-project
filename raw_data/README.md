# raw_data

- On a Linux machine, setup MusicBrainz server according to this link: https://github.com/metabrainz/musicbrainz-server/blob/master/INSTALL.md
	- Make sure you use Postgres version 12
- Using `psql`, export the raw album data with `collect_raw_data.sql`
	- Example command: `psql -U musicbrainz -d musicbrainz_db -f ./collect_raw_data.sql -h /var/run/postgresql -p 5433 -t --csv > [OUTPUT_PATH]`
	- The default password is `musicbrainz`
	- This takes a lot of time
