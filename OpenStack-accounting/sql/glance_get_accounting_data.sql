CREATE PROCEDURE `get_accounting_data`(IN starttime datetime, IN endtime datetime)
BEGIN
SELECT
    p.name AS Project,
    pp.name AS Department,
    COUNT(g.id) AS Images,
    ip.value as GlanceType,
    if(il.value like "%rbd%", "RBD" ,if(il.value like "%swift%","OBJECT","UNKNONWN")) as StorageBackend,
    @VolumeSeconds:=SUM(IF(g.created_at <= starttime
            AND (g.deleted_at >= endtime
            OR ISNULL(g.deleted_at)),
        TIMESTAMPDIFF(SECOND,
            starttime,
            endtime),
        IF(g.created_at <= starttime
                AND g.deleted_at < endtime,
            TIMESTAMPDIFF(SECOND,
                starttime,
                g.deleted_at),
            IF(g.created_at > starttime
                    AND (g.deleted_at >= endtime
                    OR ISNULL(g.deleted_at)),
                TIMESTAMPDIFF(SECOND,
                    g.created_at,
                    endtime),
                TIMESTAMPDIFF(SECOND,
                    g.created_at,
                    g.deleted_at))))) AS Image_Seconds,
    g.size/(1024 * 1024 * 1024) AS Glance_GB
FROM
    glance.images g
    join
    glance.image_properties ip on g.id = ip.image_id and ip.name = "image_type"
    join
    glance.image_locations il on g.id = il.image_id
        JOIN
    keystone.project p ON g.owner = p.id
        JOIN
    keystone.project pp ON p.parent_id = pp.id
WHERE
    g.created_at <= endtime
        AND (g.deleted_at >= starttime
        OR g.deleted_at is null )
GROUP BY ip.value, g.size , p.name , pp.name,if(il.value like "%rbd%", "SIRIUS" ,if(il.value like "%swift%","ECHO","UNKNONWN"));
END
