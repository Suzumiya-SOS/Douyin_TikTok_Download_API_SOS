from pydantic import BaseModel


# API基础请求模型 / Base Request Model
class BaseRequestModel(BaseModel):
    """
    Base Request Model for Douyin APP API
    """
    iid: int = 7318518857994389254
    device_id: int = 7318517321748022790
    channel: str = "wandoujia"
    aid: str = "1128"
    app_name: str = "aweme"
    version_code: str = "250401"
    version_name: str = "25.4.1"
    device_platform: str = "android"
    device_type: str = "SM-G9500"
    os_version: str = "9"
    residence: str = "CN"
    app_language: str = "zh"
    language: str = "zh"
    region: str = "CN"


# Feed视频详情请求模型 / Feed Video Detail Request Model
class FeedVideoDetail(BaseRequestModel):
    """
    Feed Video Detail Request Model
    """
    aweme_id: str


# 视频详情请求模型 / Video Detail Request Model
class VideoDetail(BaseRequestModel):
    """
    Video Detail Request Model (aweme/v1/aweme/detail/)
    """
    aweme_id: str
