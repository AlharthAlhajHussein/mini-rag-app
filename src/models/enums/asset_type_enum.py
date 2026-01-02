from enum import Enum


class AssetTypeEnum(Enum):
    
    FILE: str = "file"
    IMAGE: str = "image"
    VIDEO: str = "video"
    AUDIO: str = "audio"
    URL: str = "url"
    OTHER: str = "other"
    