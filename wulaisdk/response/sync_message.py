from wulaisdk.response import BaseModel


class SyncMessage(BaseModel):
    msg_id: str

    def __init__(self, msg_id: str) -> None:
        self.msg_id = msg_id
