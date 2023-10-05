CREATE PROCEDURE `get_accounting_data`(IN starttime datetime, IN endtime datetime)
BEGIN
/*
   Generates accounting data from the Nova database on various resources used
   A temporary table is set up to run incremental checks to try and establish concurrency stats - This is dropped at the end of the proc
   Some further comments below for the trickier bits
 */
create table if not exists thecount_concurrency_stats (
start_time datetime,
end_time datetime,
project_id varchar(255),
flavor_id int ,
concVMs int,
concVCPUs int,
concMem int,
concSwap int,
concRoot int,
concEph int
);
set @looptime = starttime;
while @looptime < endtime do /* loop which iterates through intervals within the time period to get approximate concurrency */
set @loopend = DATE_ADD(@looptime, INTERVAL 10 MINUTE);
insert into thecount_concurrency_stats
SELECT
    @looptime AS start_time,
    @loopend AS end_time,
    i.project_id AS project_id,
    i.instance_type_id AS flavor_id,
    COUNT(uuid) AS concVMs,
    SUM(it.vcpus) AS concVCPUs,
    SUM(it.memory_mb) AS concMem,
    SUM(it.swap) AS concSwap,
    SUM(it.root_gb) AS concRoot,
    SUM(it.ephemeral_gb) AS concEph

FROM
    nova.instances i
        JOIN
    nova_api.flavors it ON i.instance_type_id = it.id
WHERE
    i.created_at <= @loopend
        AND (i.deleted_at >= @looptime
        OR ISNULL(i.deleted_at))
GROUP BY instance_type_id , i.project_id ;
set @looptime = @loopend;
end while;
SELECT
    IFNULL(i.availability_zone, 'nova') AS AvailabilityZone,
    p.name AS Project,
    pp.name AS Department,
    it.name AS Flavor,
    MAX(ts.concVMs) AS VMs,
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
    'something' AS testingstuff,
    it.memory_mb AS Memory_MB,
    it.vcpus AS VCPU,
    it.swap AS Swap,
    it.root_gb AS Root_GB,
    it.ephemeral_gb AS Ephemeral_GB,
    MAX(ts.concMem) AS Max_Conc_Memory_MB,
    MAX(ts.concVCPUs) AS Max_Conc_VCPU,
    MAX(ts.concSwap) AS Max_Conc_Swap,
    MAX(ts.concRoot) AS Max_Conc_Root_GB,
    MAX(ts.concEph) AS Max_Conc_Ephemeral_GB,
    MIN(ts.concMem) AS Min_Conc_Memory_MB,
    MIN(ts.concVCPUs) AS Min_Conc_VCPU,
    MIN(ts.concSwap) AS Min_Conc_Swap,
    MIN(ts.concRoot) AS Min_Conc_Root_GB,
    MIN(ts.concEph) AS Min_Conc_Ephemeral_GB,
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
    thecount_concurrency_stats ts ON i.instance_type_id = ts.flavor_id
        AND i.project_id = ts.project_id
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
drop table thecount_concurrency_stats;
END
