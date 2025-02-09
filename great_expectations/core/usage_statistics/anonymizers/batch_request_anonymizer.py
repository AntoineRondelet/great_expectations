import copy
from typing import Any, Dict, List, Optional, Set, Union

from great_expectations.core.batch import (
    BatchRequest,
    RuntimeBatchRequest,
    get_batch_request_from_acceptable_arguments,
)
from great_expectations.core.usage_statistics.anonymizers.anonymizer import Anonymizer
from great_expectations.util import deep_filter_properties_dict

from great_expectations.core.usage_statistics.anonymizers.types.base import (  # isort:skip
    GETTING_STARTED_DATASOURCE_NAME,
    GETTING_STARTED_EXPECTATION_SUITE_NAME,
    GETTING_STARTED_CHECKPOINT_NAME,
    BATCH_REQUEST_REQUIRED_TOP_LEVEL_KEYS,
    BATCH_REQUEST_OPTIONAL_TOP_LEVEL_KEYS,
    DATA_CONNECTOR_QUERY_KEYS,
    RUNTIME_PARAMETERS_KEYS,
    BATCH_SPEC_PASSTHROUGH_KEYS,
    BATCH_REQUEST_FLATTENED_KEYS,
)


class BatchRequestAnonymizer(Anonymizer):
    def __init__(self, salt=None):
        super().__init__(salt=salt)

        self._batch_request_required_top_level_properties = {}
        self._batch_request_optional_top_level_keys = []
        self._data_connector_query_keys = []
        self._runtime_parameters_keys = []
        self._batch_spec_passthrough_keys = []

    def anonymize_batch_request(self, *args, **kwargs) -> Dict[str, List[str]]:
        batch_request: Union[
            BatchRequest, RuntimeBatchRequest
        ] = get_batch_request_from_acceptable_arguments(*args, **kwargs)
        batch_request_dict: dict = batch_request.to_json_dict()
        anonymized_batch_request_dict: Optional[
            Union[str, dict]
        ] = self._anonymize_batch_request_properties(source=batch_request_dict)
        deep_filter_properties_dict(
            properties=anonymized_batch_request_dict,
            clean_falsy=True,
            inplace=True,
        )
        anonymized_batch_request_keys_dict: Dict[str, List[str]] = {
            "batch_request_required_top_level_properties": self._batch_request_required_top_level_properties,
            "batch_request_optional_top_level_keys": self._batch_request_optional_top_level_keys,
            "data_connector_query_keys": self._data_connector_query_keys,
            "runtime_parameters_keys": self._runtime_parameters_keys,
            "batch_spec_passthrough_keys": self._batch_spec_passthrough_keys,
        }
        self._build_anonymized_batch_request(source=anonymized_batch_request_dict)
        deep_filter_properties_dict(
            properties=anonymized_batch_request_keys_dict,
            clean_falsy=True,
            inplace=True,
        )
        return anonymized_batch_request_keys_dict

    def _anonymize_batch_request_properties(
        self, source: Optional[Any] = None
    ) -> Optional[Union[str, dict]]:
        if source is None:
            return None

        if isinstance(source, str) and source in BATCH_REQUEST_FLATTENED_KEYS:
            return source

        if isinstance(source, dict):
            source_copy: dict = copy.deepcopy(source)
            anonymized_keys: Set[str] = set()

            key: str
            value: Any
            for key, value in source.items():
                if key in BATCH_REQUEST_FLATTENED_KEYS:
                    if self._is_getting_started_keyword(value=value):
                        source_copy[key] = value
                    else:
                        source_copy[key] = self._anonymize_batch_request_properties(
                            source=value
                        )
                else:
                    anonymized_key: str = self.anonymize(key)
                    source_copy[
                        anonymized_key
                    ] = self._anonymize_batch_request_properties(source=value)
                    anonymized_keys.add(key)

            for key in anonymized_keys:
                source_copy.pop(key)

            return source_copy

        return self.anonymize(str(source))

    def _build_anonymized_batch_request(self, source: Optional[Any] = None):
        if isinstance(source, dict):
            key: str
            value: Any
            for key, value in source.items():
                if key in BATCH_REQUEST_REQUIRED_TOP_LEVEL_KEYS:
                    self._batch_request_required_top_level_properties[
                        f"anonymized_{key}"
                    ] = value
                elif key in BATCH_REQUEST_OPTIONAL_TOP_LEVEL_KEYS:
                    self._batch_request_optional_top_level_keys.append(key)
                elif key in DATA_CONNECTOR_QUERY_KEYS:
                    self._data_connector_query_keys.append(key)
                elif key in RUNTIME_PARAMETERS_KEYS:
                    self._runtime_parameters_keys.append(key)
                elif key in BATCH_SPEC_PASSTHROUGH_KEYS:
                    self._batch_spec_passthrough_keys.append(key)
                else:
                    pass

                self._build_anonymized_batch_request(source=value)

    @staticmethod
    def _is_getting_started_keyword(value: str):
        return value in [
            GETTING_STARTED_DATASOURCE_NAME,
            GETTING_STARTED_EXPECTATION_SUITE_NAME,
            GETTING_STARTED_CHECKPOINT_NAME,
        ]
