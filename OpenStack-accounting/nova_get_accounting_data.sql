CREATE PROCEDURE `get_accounting_data`(IN starttime datetime, IN endtime datetime)
BEGIN
SELECT
    IFNULL(i.availability_zone,'nova') as AvailabilityZone,
    p.name as Project,
    pp.name as Department,
    #i.power_state as Power_State,
        it.name as Flavor,
    count(i.uuid)  as VMs,
    @VMSeconds:=SUM(IF(i.created_at <= starttime
            AND (i.deleted_at >= endtime
            OR ISNULL(i.deleted_at)),
        TIMESTAMPDIFF(SECOND,
            starttime,
            endtime),
        IF(i.created_at <= starttime
                AND i.deleted_at < endtime,
            TIMESTAMPDIFF(SECOND,
                starttime,
                i.deleted_at),
            IF(i.created_at > starttime
                    AND (i.deleted_at >= endtime
                    OR ISNULL(i.deleted_at)),
                TIMESTAMPDIFF(SECOND,
                    i.created_at,
                    endtime),
                TIMESTAMPDIFF(SECOND,
                    i.created_at,
                    i.deleted_at))))) AS VM_Seconds,
    #"x"+CAST(SUM(it.memory_mb * @VMSeconds)   AS CHAR(100))+"z" AS Memory_MB_Seconds,
    'something' AS testingstuff,
     it.memory_mb   AS Memory_MB,
     it.vcpus   AS VCPU,
     it.swap   AS Swap,
     it.root_gb   AS Root_GB,
     it.ephemeral_gb AS Ephemeral_GB,
     ifnull((select value from nova_api.flavor_extra_specs es where flavor_id = it.id and es.key like '%per_unit_cost%' and es.key like CONCAT('%',cast(YEAR(endtime) as NCHAR),'%')),0) as Per_Unit_Cost,
     ifnull((select value from nova_api.flavor_extra_specs es where flavor_id = it.id and es.key like 'accounting:unit%' ), "core") as Charge_Unit,
     (select IFNULL(value,0) from nova_api.flavor_extra_specs es where flavor_id = it.id and es.key like '%gpu_num%' ) as GPU_Num
FROM
    nova.instances i
        JOIN
    nova_api.flavors it ON i.instance_type_id = it.id
        JOIN
    keystone.project p ON i.project_id = p.id
    join
	keystone.project pp on p.parent_id = pp.id
WHERE
    i.created_at <= endtime
        AND (i.deleted_at >= starttime
        OR ISNULL(i.deleted_at))
GROUP BY i.availability_zone , p.name , it.name,SUBSTRING(it.name,1,LOCATE('.',it.name))
;
END
