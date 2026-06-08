from source.expansion import Namespace
from .request import Html

__all__ = ["Video"]


class Video:
    VIDEO_LINK = (
        "video",
        "consumer",
        "originVideoKey",
    )
    STREAM_LINKS = (
        "video.media.stream.h264[0].masterUrl",
        "video.media.stream.h265[0].masterUrl",
        "video.media.stream.h266[0].masterUrl",
        "video.media.stream.av1[0].masterUrl",
        "media.stream.h264[0].masterUrl",
        "media.stream.h265[0].masterUrl",
        "media.stream.h266[0].masterUrl",
        "media.stream.av1[0].masterUrl",
    )

    @classmethod
    def get_video_link(cls, data: Namespace) -> list:
        if links := cls.__get_stream_links(data):
            return links
        if t := data.safe_extract(".".join(cls.VIDEO_LINK)):
            return [Html.format_url(f"https://sns-video-bd.xhscdn.com/{t}")]
        return []

    @classmethod
    def __get_stream_links(cls, data: Namespace) -> list:
        urls = []
        for path in cls.STREAM_LINKS:
            if url := data.safe_extract(path):
                urls.append(Html.format_url(url))
        return list(dict.fromkeys(i for i in urls if i))
