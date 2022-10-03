from pydantic import BaseModel

class ConnectionSchema(BaseModel):
  sid: str