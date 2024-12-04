from pydantic import BaseModel, Field
from typing import Optional

class ModelItem(BaseModel):
    """
    ModelItem represents a model in the asset management system.

    Attributes:
        model_name (str): The name of the model.
        model_number (str): The unique identifier for the model.
        model_id (Optional[int]): The unique ID of the model, which is optional.
    """
    model_name: str
    model_number: str
    model_id: Optional[int] = Field(None)