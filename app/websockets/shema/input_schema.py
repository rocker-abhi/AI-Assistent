from datetime import datetime
from pydantic import BaseModel, Field

class MessageContent(BaseModel):
    text: str

class InputMessageSchema(BaseModel):
    type: str = Field(..., description="The general type of the event, e.g. 'message'")
    message_type: str = Field(..., description="The specific message type, e.g. 'text'")
    message_id: str
    content: MessageContent
    timestamp: datetime
