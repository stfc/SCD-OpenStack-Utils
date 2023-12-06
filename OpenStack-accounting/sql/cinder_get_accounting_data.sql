/*
SPDX-License-Identifier: Apache-2.0
Copyright (c) 2023 United Kingdom Research and Innovation
*/

CREATE PROCEDURE `get_accounting_data`(IN starttime datetime, IN endtime datetime)
BEGIN
/*
   This procedure generates accounting data for cinder
*/
SELECT
    IFNULL(v.availability_zone, 'nova') AS AvailabilityZone,
    p.name AS Project,
    pp.name AS Department,
    COUNT(v.id) AS Volumes,
    "Volume" as CinderType,
    @VolumeSeconds:=SUM(IF(v.created_at <= starttime /* Captures Volumes which were created outside of the period deleted out of the period */
            AND (v.deleted_at >= endtime
            OR ISNULL(v.deleted_at)),
        TIMESTAMPDIFF(SECOND,
            starttime,
            endtime),
        IF(v.created_at <= starttime /* Captures Volumes which were created before the period and deleted during the period */
                AND v.deleted_at < endtime,
            TIMESTAMPDIFF(SECOND,
                starttime,
                v.deleted_at),
            IF(v.created_at > starttime /* Captures Volumes which were created during the period and deleted outside the period */
                    AND (v.deleted_at >= endtime
                    OR ISNULL(v.deleted_at)),
                TIMESTAMPDIFF(SECOND,
                    v.created_at,
                    endtime),
                TIMESTAMPDIFF(SECOND,
                    v.created_at,
                    v.deleted_at))))) AS Volume_Seconds, /* Generates a count of seconds Volumes were running */
    v.size AS Volume_GB
FROM
    cinder.volumes v
        JOIN
    keystone.project p ON v.project_id = p.id
        JOIN
    keystone.project pp ON p.parent_id = pp.id
WHERE
    v.created_at <= endtime
        AND (v.deleted_at >= starttime
        OR ISNULL(v.deleted_at))
GROUP BY v.availability_zone , v.size , p.name , pp.name;
END
