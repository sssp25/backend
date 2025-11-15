from rest_framework.exceptions import UnsupportedMediaType
from rest_framework.parsers import MultiPartParser

class MediaFileUploadParser(MultiPartParser):
    media_type = '*/*' # 비디오 형식만 받음 MIME 형식 찾아보셈

    ALLOWED_VIDEO_TYPES = [
        'video/mp4',
        'video/webm',
        'video/quicktime',
        'video/avi',  # avi
        'video/x-msvideo',  # avi
        'images/png',
        'images/jpeg',
    ]

    def parse(self, stream, media_type=None, parser_context=None):
        if media_type not in self.ALLOWED_VIDEO_TYPES:
            raise UnsupportedMediaType(
                media_type,
                detail=(
                    f"Unsupported video type: {media_type}. "
                    f"Allowed types are: {', '.join(self.ALLOWED_VIDEO_TYPES)}"
                )
            )

        return super().parse(stream, media_type, parser_context)