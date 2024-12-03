import json
import redis
from typing import Any, Union

from gq_webhooks_backend.utils.metrics import cache_get_total, cache_hits_total


class ElastiCacheUtility:
    def __init__(self, config: dict, env: str = "dev",
                 service: str = "project_name"): # TODO: change the service default value to project_name
        self.expiry_time = config.get("default_expiry_time")
        self.env = env
        self.service = service
        self.cluster_endpoint = config.get('cluster_endpoint')
        self.port = config.get('port')
        self.client = redis.StrictRedis(host=self.cluster_endpoint, port=self.port, decode_responses=True)

    def construct_key(self, unique_method_identifier: str, unique_identifier_key: str) -> str:
        return f"_GQ_{self.env}_{self.service}_{unique_method_identifier}_{unique_identifier_key}_".upper()

    def set(self, unique_method_identifier: str, unique_identifier_key: str, value: Any,
            expiry_time: int = None) -> bool:
        try:
            if not expiry_time:
                expiry_time = self.expiry_time
            key = self.construct_key(unique_method_identifier, unique_identifier_key)
            value_str = json.dumps(value)
            self.client.set(key, value_str)
            self.client.expire(key, expiry_time)
            return True
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get(self, unique_method_identifier: str, unique_identifier_key: str) -> Union[None, Any]:
        try:
            key = self.construct_key(unique_method_identifier, unique_identifier_key)
            cache_get_total.labels(backend="redis").inc()  # Increment total cache gets
            value_str = self.client.get(key)
            if value_str is not None:
                cache_hits_total.labels(backend="redis").inc()  # Increment cache hits
            return json.loads(value_str) if value_str else None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None

    def delete(self, unique_method_identifier: str, unique_identifier_key: str) -> bool:
        try:
            key = self.construct_key(unique_method_identifier, unique_identifier_key)
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False