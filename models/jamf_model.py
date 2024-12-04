from pydantic import BaseModel
from typing import Optional


class JamfItem(BaseModel):
    """
    ModelItem represents a model in the asset management system.

    Attributes:
        model_name (str): The name of the model.
        model_number (str): The unique identifier for the model.
        model_id (Optional[int]): The unique ID of the model, which is optional.
    """
    name: str
    serial_number: str
    model_identifier: str
    assigned_user: Optional[str] = None
    model_name: str