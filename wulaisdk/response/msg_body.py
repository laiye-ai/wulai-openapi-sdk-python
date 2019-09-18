from wulaisdk.response import BaseModel


class Text(BaseModel):
    content: str

    def __init__(self, content: str) -> None:
        self.content = content


class Image(BaseModel):
    resource_url: str

    def __init__(self, resource_url: str) -> None:
        self.resource_url = resource_url


class Custom(BaseModel):
    content: str

    def __init__(self, content: str) -> None:
        self.content = content


class Video(BaseModel):
    resource_url: str
    thumb: str
    description: str
    title: str

    def __init__(self, resource_url: str, thumb: str, description: str, title: str) -> None:
        self.resource_url = resource_url
        self.thumb = thumb
        self.description = description
        self.title = title


class File(BaseModel):
    file_name: str
    resource_url: str

    def __init__(self, file_name: str, resource_url: str) -> None:
        self.file_name = file_name
        self.resource_url = resource_url


class Voice(BaseModel):
    # todo: type
    resource_url: str
    type: str
    recognition: str

    def __init__(self, resource_url: str, type: str, recognition: str) -> None:
        self.resource_url = resource_url
        self.type = type
        self.recognition = recognition


class ShareLink(BaseModel):
    description: str
    destination_url: str
    cover_url: str
    title: str

    def __init__(self, description: str, destination_url: str, cover_url: str, title: str) -> None:
        self.description = description
        self.destination_url = destination_url
        self.cover_url = cover_url
        self.title = title
#
#
# class MsgBody:
#     text: Text
#
#     def __init__(self, text: Text) -> None:
#         self.text = Text(**text)
#
#
# class MsgBody:
#     msg_body: dict
#
#     def __init__(self, msg_body: dict) -> None:
#         if "text" in msg_body:
#             self.text = Text(**msg_body)
#         elif "image" in msg_body:
#             self.text = Image(**msg_body)
#         elif "custom" in msg_body:
#             self.text = Custom(**msg_body)
#         elif "video" in msg_body:
#             self.text = Video(**msg_body)
#         elif "file" in msg_body:
#             self.text = File(**msg_body)
#         elif "voice" in msg_body:
#             self.text = Voice(**msg_body)
#         elif "share_link" in msg_body:
#             self.text = ShareLink(**msg_body)
#         else:
#             raise ValueError("err msg body value")


class MsgBody(BaseModel):
    msg_body: dict

    def __init__(self, **kwargs) -> None:
        if "text" in kwargs:
            self.text = Text(**kwargs.get("text"))
        elif "image" in kwargs:
            self.image = Image(**kwargs.get("image"))
        elif "custom" in kwargs:
            self.custom = Custom(**kwargs.get("custom"))
        elif "video" in kwargs:
            self.video = Video(**kwargs.get("video"))
        elif "file" in kwargs:
            self.file = File(**kwargs.get("file"))
        elif "voice" in kwargs:
            self.voice = Voice(**kwargs.get("voice"))
        elif "share_link" in kwargs:
            self.share_link = ShareLink(**kwargs.get("share_link"))
        else:
            raise ValueError("err msg body value")
