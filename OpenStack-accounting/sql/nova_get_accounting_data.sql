CREATE PROCEDURE `get_accounting_data`(IN starttime datetime, IN endtime datetime)
BEGIN
/*
   Generates accounting data from the Nova database on various resources used
   Some further comments below for the trickier bits
 */
SELECT
    IFNULL(i.availability_zone, 'nova') AS AvailabilityZone,
    p.name AS Project,
    pp.name AS Department,
    it.name AS Flavor,
    COUNT(i.uuid) as VMs,
    @VMSeconds:=SUM(IF(i.created_at <= starttime /* Captures VMs which were created outside of the period deleted out of the period */
            AND (i.deleted_at >= endtime
            OR ISNULL(i.deleted_at)),
        TIMESTAMPDIFF(SECOND,
            starttime,
            endtime),
        IF(i.created_at <= starttime /* Captures VMs which were created before the period and deleted during the period */
                AND i.deleted_at < endtime,
            TIMESTAMPDIFF(SECOND,
                starttime,
                i.deleted_at),
            IF(i.created_at > starttime /* Captures VMs which were created during the period and deleted outside the period */
                    AND (i.deleted_at >= endtime
                    OR ISNULL(i.deleted_at)),
                TIMESTAMPDIFF(SECOND,
                    i.created_at,
                    endtime),
                TIMESTAMPDIFF(SECOND,
                    i.created_at,
                    i.deleted_at))))) AS VM_Seconds, /* Generates a count of seconds VMs were running */
    it.memory_mb AS Memory_MB,
    it.vcpus AS VCPU,
    it.swap AS Swap,
    it.root_gb AS Root_GB,
    it.ephemeral_gb AS Ephemeral_GB,
    /* The below section extracts metadata to be used for accounting */
    IFNULL((SELECT
                    value
                FROM
                    nova_api.flavor_extra_specs es
                WHERE
                    flavor_id = it.id
                        AND es.key LIKE '%per_unit_cost%'
                        AND es.key LIKE CONCAT('%',
                            CAST(YEAR(DATE_SUB(endtime, INTERVAL 3 MONTH))
                                AS NCHAR),
                            '%')
                LIMIT 1),
            0) AS Per_Unit_Cost,
    IFNULL((SELECT
                    value
                FROM
                    nova_api.flavor_extra_specs es
                WHERE
                    flavor_id = it.id
                        AND es.key LIKE 'accounting:unit%'),
            'core') AS Charge_Unit,
    (SELECT
            IFNULL(value, 0)
        FROM
            nova_api.flavor_extra_specs es
        WHERE
            flavor_id = it.id
                AND es.key LIKE 'accounting:gpu_num%') AS GPU_Num
FROM
    nova.instances i
        JOIN
    nova_api.flavors it ON i.instance_type_id = it.id
        JOIN
    keystone.project p ON i.project_id = p.id
        JOIN
    keystone.project pp ON p.parent_id = pp.id
WHERE
    i.created_at <= endtime
        AND (i.deleted_at >= starttime
        OR ISNULL(i.deleted_at))
GROUP BY i.availability_zone , p.name , it.name , SUBSTRING(it.name,
    1,
    LOCATE('.', it.name))
    UNION
    SELECT
        IFNULL(i.availability_zone, 'nova') AS AvailabilityZone,
        p.name AS Project,
        pp.name AS Department,
        it.name AS Flavor,
        COUNT(i.uuid) as VMs,
        @VMSeconds:=SUM(IF(i.created_at <= starttime /* Captures VMs which were created outside of the period deleted out of the period */
                AND (i.deleted_at >= endtime
                OR ISNULL(i.deleted_at)),
            TIMESTAMPDIFF(SECOND,
                starttime,
                endtime),
            IF(i.created_at <= starttime /* Captures VMs which were created before the period and deleted during the period */
                    AND i.deleted_at < endtime,
                TIMESTAMPDIFF(SECOND,
                    starttime,
                    i.deleted_at),
                IF(i.created_at > starttime /* Captures VMs which were created during the period and deleted outside the period */
                        AND (i.deleted_at >= endtime
                        OR ISNULL(i.deleted_at)),
                    TIMESTAMPDIFF(SECOND,
                        i.created_at,
                        endtime),
                    TIMESTAMPDIFF(SECOND,
                        i.created_at,
                        i.deleted_at))))) AS VM_Seconds, /* Generates a count of seconds VMs were running */
        it.memory_mb AS Memory_MB,
        it.vcpus AS VCPU,
        it.swap AS Swap,
        it.root_gb AS Root_GB,
        it.ephemeral_gb AS Ephemeral_GB,
        /* The below section extracts metadata to be used for accounting */
        IFNULL((SELECT
                        value
                    FROM
                        nova_api.flavor_extra_specs es
                    WHERE
                        flavor_id = it.id
                            AND es.key LIKE '%per_unit_cost%'
                            AND es.key LIKE CONCAT('%',
                                CAST(YEAR(DATE_SUB(endtime, INTERVAL 3 MONTH))
                                    AS NCHAR),
                                '%')
                    LIMIT 1),
                0) AS Per_Unit_Cost,
        IFNULL((SELECT
                        value
                    FROM
                        nova_api.flavor_extra_specs es
                    WHERE
                        flavor_id = it.id
                            AND es.key LIKE 'accounting:unit%'),
                'core') AS Charge_Unit,
        (SELECT
                IFNULL(value, 0)
            FROM
                nova_api.flavor_extra_specs es
            WHERE
                flavor_id = it.id
                    AND es.key LIKE 'accounting:gpu_num%') AS GPU_Num
    FROM
        nova.shadow_instances i
            JOIN
        nova_api.flavors it ON i.instance_type_id = it.id
            JOIN
        keystone.project p ON i.project_id = p.id
            JOIN
        keystone.project pp ON p.parent_id = pp.id
    WHERE
        i.created_at <= endtime
            AND (i.deleted_at >= starttime
            OR ISNULL(i.deleted_at))
    GROUP BY i.availability_zone , p.name , it.name , SUBSTRING(it.name,
        1,
        LOCATE('.', it.name))
;
END
