/*
SPDX-License-Identifier: Apache-2.0
Copyright (c) 2023 United Kingdom Research and Innovation
*/

CREATE PROCEDURE `get_accounting_data`(IN starttime datetime, IN endtime datetime)
BEGIN
/*
   This procedure generates accounting data for manila
*/
SELECT
    p.name AS Project,
    pp.name AS Department,
    maz.name AS Availability_zone,
    st.name AS Share_type,
    COUNT(m.id) AS Shares,
    "Share" as ManilaType,
    @ShareSeconds:=SUM(IF(m.created_at <= starttime  /* Captures Shares which were created outside of the period deleted out of the period */
            AND (m.deleted_at >= endtime
            OR ISNULL(m.deleted_at)),
        TIMESTAMPDIFF(SECOND,
            starttime,
            endtime),
        IF(m.created_at <= starttime /* Captures Shares which were created before the period and deleted during the period */
                AND m.deleted_at < endtime,
            TIMESTAMPDIFF(SECOND,
                starttime,
                m.deleted_at),
            IF(m.created_at > starttime /* Captures Shares which were created during the period and deleted outside the period */
                    AND (m.deleted_at >= endtime
                    OR ISNULL(m.deleted_at)),
                TIMESTAMPDIFF(SECOND,
                    m.created_at,
                    endtime),
                TIMESTAMPDIFF(SECOND,
                    m.created_at,
                    m.deleted_at))))) AS Share_Seconds, /* Generates a count of seconds Shares were running */
    m.size AS Share_GB
FROM
    manila.shares m
        JOIN
    manila.share_instances si ON m.id = si.share_id
        JOIN
    manila.share_types st ON si.share_type_id = st.id
        JOIN
    manila.availability_zones maz ON maz.id = si.availability_zone_id
        JOIN
    keystone.project p ON m.project_id = p.id
        JOIN
    keystone.project pp ON p.parent_id = pp.id
WHERE
    m.created_at <= endtime
        AND (m.deleted_at >= starttime
        OR ISNULL(m.deleted_at))
GROUP BY m.size , p.name , pp.name , maz.name , st.name;
END
