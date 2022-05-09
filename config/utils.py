import json
from dataclasses import dataclass


@dataclass
class VcapServices(object):

    services: dict

    @staticmethod
    def from_env_json(json_string: str):
        json_dict = dict(json.loads(json_string))
        vcap_services = VcapServices(services=json_dict)
        return vcap_services

    def get_service_by_name(self, group_key: str, name: str) -> dict:
        service_group = self.services.get(group_key)
        if service_group:
            for service in service_group:
                if service.get("name") == name:
                    return service
            raise Exception(f"Service name '{name}' not found")
        raise Exception(f"Service group '{group_key}' not found")

    def get_service_credentials_value(
        self, group_key: str, name: str, key: str
    ):
        service = self.get_service_by_name(group_key, name)
        return service.get("credentials").get(key)
