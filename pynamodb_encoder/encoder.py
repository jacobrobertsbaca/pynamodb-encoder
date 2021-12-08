from typing import Any

from pynamodb.attributes import (
    Attribute,
    AttributeContainer,
    DynamicMapAttribute,
    ListAttribute,
    MapAttribute,
)
from pynamodb.models import Model

from pynamodb_encoder.primitive_attribute_encoder import PrimitiveAttributeEncoder


class Encoder:
    def encode(self, instance: Model) -> dict[str, Any]:
        return self.encode_container(instance)

    def encode_container(self, container: AttributeContainer) -> dict[str, Any]:
        encoded = {}
        for name, attr in container.get_attributes().items():
            value = getattr(container, name)
            if value:
                encoded[name] = self.encode_attribute(attr, value)
        return encoded

    def encode_attribute(self, attr: Attribute, data: Any):
        if isinstance(attr, ListAttribute):
            return self.encode_list(attr, data)
        elif isinstance(attr, MapAttribute):
            return self.encode_map(attr, data)
        else:
            return PrimitiveAttributeEncoder.encode(attr, data)

    def encode_list(self, attr: ListAttribute, data: list) -> list:
        element_attr = (attr.element_type or Attribute)()
        return [self.encode_attribute(element_attr, value) for value in data]

    def encode_map(self, attr: MapAttribute, data: MapAttribute) -> dict:
        if type(attr) == MapAttribute:
            return {name: data[name] for name in data}
        elif isinstance(attr, DynamicMapAttribute):
            return self.encode_dynamic_map(attr, data)
        else:
            return self.encode_container(data)

    def encode_dynamic_map(self, attr: DynamicMapAttribute, data: MapAttribute) -> dict:
        encoded = {}
        attributes = attr.get_attributes()
        for name in data:
            value = getattr(data, name)
            if name in attributes:
                encoded[name] = self.encode_attribute(attributes[name], value)
            else:
                encoded[name] = value
        return encoded
