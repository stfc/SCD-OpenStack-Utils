from pynetboxquery.utils.device_dataclass import Device


# pylint: disable = R0903,C0115
class NetboxGetId:
    def __init__(self, api):
        self.netbox = api

    def get_id(self, device: Device, attr: str) -> Device:
        """
        This method queries Netbox for ID's of values.
        :param device: The device dataclass.
        :param attr: The attribute to query Netbox for.
        :return: Returns an updated copy of the device dataclass.
        """
        value = getattr(device, attr)
        netbox_id = ""
        if attr in ["status", "face", "airflow", "position", "name", "serial"]:
            return getattr(device, attr)
        match attr:
            case "tenant":
                netbox_id = self.netbox.tenancy.tenants.get(name=value).id
            case "device_role":
                netbox_id = self.netbox.dcim.device_roles.get(name=value).id
            case "manufacturer":
                netbox_id = self.netbox.dcim.manufacturers.get(name=value).id
            case "device_type":
                netbox_id = self.netbox.dcim.device_types.get(slug=value).id
            case "site":
                netbox_id = self.netbox.dcim.sites.get(name=value).id
            case "location":
                if isinstance(device.site, int):
                    site_slug = self.netbox.dcim.sites.get(id=device.site).slug
                else:
                    site_slug = device.site.replace(" ", "-").lower()
                netbox_id = self.netbox.dcim.locations.get(
                    name=value, site=site_slug
                ).id
            case "rack":
                netbox_id = self.netbox.dcim.racks.get(name=value).id
        return netbox_id
