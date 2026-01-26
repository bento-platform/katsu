from typing import Type, Set
from pydantic import BaseModel

class PydanticJSONBMixin:
    """
    Mixin for models that store some Pydantic fields in a JSONB column.
    
    Requires:
        - COLUMN_FIELDS: set of field names stored as actual columns
        - JSONB_FIELD: name of the JSONField (default: 'other_data')
        - SCHEMA_CLASS: the Pydantic model class
    """
    COLUMN_FIELDS: Set[str] = set()
    JSONB_FIELD: str = 'other_data'
    SCHEMA_CLASS: Type[BaseModel] | None = None
    
    @classmethod
    def from_schema(cls, schema: BaseModel, **extra_column_kwargs):
        data = schema.model_dump(exclude_unset=True)
        
        column_data = {
            k: v for k, v in data.items() 
            if k in cls.COLUMN_FIELDS and k != 'id'
        }
        column_data.update(extra_column_kwargs)
        
        jsonb_data = {
            k: v for k, v in data.items() 
            if k not in cls.COLUMN_FIELDS
        }
        
        instance = cls(**column_data)
        setattr(instance, cls.JSONB_FIELD, jsonb_data)
        return instance
    
    def to_schema(self) -> BaseModel:
        data = {
            field: getattr(self, field) 
            for field in self.COLUMN_FIELDS 
            if hasattr(self, field)
        }
        data.update(getattr(self, self.JSONB_FIELD, {}))

        if self.SCHEMA_CLASS is None:
            raise NotImplementedError(f"{self.__class__.__name__} must define SCHEMA_CLASS")
        
        return self.SCHEMA_CLASS(**data)