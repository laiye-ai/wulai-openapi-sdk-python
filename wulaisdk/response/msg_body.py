from wulaisdk.response import BaseModel


class Text(BaseModel):
    """
    文本消息
    """
    content: str

    def __init__(self, content: str) -> None:
        self.content = content


class Image(BaseModel):
    """
    图片消息
    """
    resource_url: str

    def __init__(self, resource_url: str) -> None:
        self.resource_url = resource_url


class Custom(BaseModel):
    """
    自定义消息
    """
    content: str

    def __init__(self, content: str) -> None:
        self.content = content


class Video(BaseModel):
    """
    视频消息
    """
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
    """
    文件消息
    """
    file_name: str
    resource_url: str

    def __init__(self, file_name: str, resource_url: str) -> None:
        self.file_name = file_name
        self.resource_url = resource_url


class Voice(BaseModel):
    """
    语音消息
    """
    resource_url: str
    type: str
    recognition: str

    def __init__(self, resource_url: str, type: str, recognition: str) -> None:
        self.resource_url = resource_url
        self.type = type
        self.recognition = recognition


class ShareLink(BaseModel):
    """
    卡片消息
    """
    description: str
    destination_url: str
    cover_url: str
    title: str

    def __init__(self, description: str, destination_url: str, cover_url: str, title: str) -> None:
        self.description = description
        self.destination_url = destination_url
        self.cover_url = cover_url
        self.title = title


class RichText(BaseModel):
    """
    图文消息
    """
    resource_url: str

    def __init__(self, resource_url: str) -> None:
        self.resource_url = resource_url


class Event(BaseModel):
    """
    事件消息
    """
    fields: dict
    event_type: str

    def __init__(self, fields: dict, event_type: str) -> None:
        self.fields = fields
        self.event_type = event_type


class MsgBody(BaseModel):
    """
    消息体格式
    """

    def __init__(self, **kwargs) -> None:
        if "text" in kwargs:
            self.text = Text.from_dict(kwargs.get("text"))
        elif "image" in kwargs:
            self.image = Image.from_dict(kwargs.get("image"))
        elif "custom" in kwargs:
            self.custom = Custom.from_dict(kwargs.get("custom"))
        elif "video" in kwargs:
            self.video = Video.from_dict(kwargs.get("video"))
        elif "file" in kwargs:
            self.file = File.from_dict(kwargs.get("file"))
        elif "voice" in kwargs:
            self.voice = Voice.from_dict(kwargs.get("voice"))
        elif "share_link" in kwargs:
            self.share_link = ShareLink.from_dict(kwargs.get("share_link"))
        elif "rich_text" in kwargs:
            self.rich_text = RichText.from_dict(kwargs.get("rich_text"))
        elif "event" in kwargs:
            self.event = Event.from_dict(kwargs.get("event"))
        else:
            for k, v in kwargs.items():
                setattr(self, k, v)
            # raise ValueError("err msg body value")
