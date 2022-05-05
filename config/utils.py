from dataclasses import dataclass


@dataclass
class VcapServices(object):

    services: dict

    @staticmethod
    def from_json(json_dict: dict):
        vcap_services = VcapServices(services=json_dict)
        return vcap_services

    def get_service_by_name(self, group_key: str, name: str) -> dict:
        service_group = self.services.get(group_key)
        if service_group:
            for service in service_group:
                if service.get("name") == name:
                    return service
            raise Exception("Service name '" + name + "' not found")
        raise Exception("Service group '" + group_key + "' not found")

    def get_service_credentials_by_name(self, group_key: str, name: str):
        service = self.get_service_by_name(group_key, name)
        return service.get("credentials")
