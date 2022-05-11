-- This query JOINs all the relevant metadata per release.
-- There are duplicated lines: Either if the album had multiple releases, or the album was published in multiple countries.
-- Thus, this needs extra processing afterwards.
SELECT r.gid, rg.name AS album_name, a.name AS artist_name, rc.date_year AS release_year
FROM cover_art_archive.cover_art AS ca
LEFT JOIN musicbrainz.release AS r ON r.id = ca.release
LEFT JOIN musicbrainz.release_country AS rc ON r.id = rc.release
LEFT JOIN musicbrainz.release_group AS rg ON rg.id = r.release_group
LEFT JOIN musicbrainz.artist_credit_name AS acn ON acn.artist_credit = rg.artist_credit
LEFT JOIN musicbrainz.artist AS a ON a.id = acn.artist
LEFT JOIN musicbrainz.release_group_secondary_type_join AS rgstj ON rgstj.release_group = rg.id
WHERE rg.type = 1 AND rgstj.secondary_type IS NULL AND a.name NOT LIKE 'Various Artists' AND rc.date_year IS NOT NULL;
