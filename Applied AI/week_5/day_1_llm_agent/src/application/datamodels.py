from pydantic import BaseModel,Field

class ChatPayload(BaseModel):
    query:str=Field("hello")
    userId:str=Field("xbnksis")
    
    class config:
        json_schema_extra = {
            "example":{
                "query":"what is the weather like in tokyo",
                "userId":"xbnksis"
            }
        }


class ChatResponse(BaseModel):
    response:str
    status_code:int=Field(200)
    
    class config:
        json_schema_extra = {
            "example":{
                "response":"it is 12F in degrees",
                "userId":"xbnksis"
            }
        }