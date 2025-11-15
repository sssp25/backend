import os

from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from actor.models import Actor
from .models import Media
from .serializers import MediaSerializer
from .utils import gen_id

ALLOWED_VIDEO_TYPES = [
    'video/mp4',
    'video/webm',
    'video/quicktime',
    'video/avi',
    'video/x-msvideo',
]

ALLOWED_IMAGE_TYPES = [
    'image/png',
    'image/jpeg',
    'image/jpg',
    'image/gif',
    'image/webp',
]

# Create your views here.
@api_view(["GET"])
def get_trending_videos(request):
    rs = Media.objects.filter(is_video=True, oneweekvideostatics__isnull=False).order_by('-oneweekvideostatics__points') # 한 주의 비디오 상위 랭킹 집합(포인트로 나열); 비디오 정보 집합

    # rs = vq.intersection(q)
    #rs = vq.union(q) # 합집합
    paginator = Paginator(rs, 20) # 나눠서 가져오기 (페이지당 20개의 영상)
    page_number = request.GET.get("page") # 파라미터에서 'page' 쿼리 가져오기 (페이지 번호)
    page = paginator.get_page(page_number) # 가져온 페이지 번호에 해당되는 부분 가져오기

    serializer = MediaSerializer(page, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def search_media(request, mtype):
    q = request.GET.get('q')
    if not q: return Response(status=status.HTTP_400_BAD_REQUEST)

    order = request.GET.get("orderBy") # 무엇으로 정렬할 것 인지
    if not order: order = "views"

    ov = order if not order.startswith("-") else order[1:] # 정렬 요소 앞에 -가 붙으면 역정렬
    if not (ov == "views" or ov == "likes" or ov == "comments"): return Response(status=status.HTTP_400_BAD_REQUEST) # 만약에 지정된 정렬 요소가 아니라면 400 오류

    media = Media.objects.filter(is_video=(mtype=="video"), title__icontains=q).order_by(order) # q는 검색문
    paginator = Paginator(media, 440)  # 나눠서 가져오기 (페이지당 20개의 영상)
    page_number = request.GET.get("page")  # 파라미터에서 'page' 쿼리 가져오기 (페이지 번호)
    page = paginator.get_page(page_number)  # 가져온 페이지 번호에 해당되는 부분 가져오기

    serializer = MediaSerializer(page, many=True)
    return Response(serializer.data)


@api_view(["PUT"])
@parser_classes([MultiPartParser])
def upload_media(request, format=None):
    if not request.user.is_authenticated: 
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    if "file" not in request.FILES:
        return Response(
            {"detail": "No file provided"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file_obj = request.FILES["file"]
    
    is_video = file_obj.content_type in ALLOWED_VIDEO_TYPES
    is_image = file_obj.content_type in ALLOWED_IMAGE_TYPES
    
    if not is_video and not is_image:
        return Response(
            {"detail": f"Unsupported media type: {file_obj.content_type}"},
            status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )

    id = gen_id(16)
    ftype = 'video' if is_video else 'image'
    ext = file_obj.content_type.split('/')[-1]
    
    upload_path = './upload/{}/{}'.format(ftype, id)
    os.makedirs(upload_path, exist_ok=True)
    
    destination = open('{}/original.{}'.format(upload_path, ext), 'wb+')
    
    for chunk in file_obj.chunks():
        destination.write(chunk)
    
    destination.close()

    media = Media()
    media.id = id
    media.title = file_obj.name
    try:
        media.actor = Actor.objects.get(id=request.user.id)
    except Actor.DoesNotExist:
        pass
    media.is_video = is_video
    media.save()

    serializer = MediaSerializer(media, many=False)
    return Response(serializer.data)

@api_view(["PUT"])
@parser_classes([MultiPartParser])
def upload_video(request, format=None):
    return upload_media(request, format)

class VideoView(APIView):
    def get(self, request, vid):
        video = get_object_or_404(Media, pk=vid, is_media=True)
        serializer = MediaSerializer(video)
        return Response(serializer.data)

    def patch(self, request, vid):
        if not self.request.user.is_authenticated: return Response(status=status.HTTP_401_UNAUTHORIZED) # 유저가 로그인 되어있지 않다면 401 오류

        v = Media.objects.get(pk=vid, is_media=True)
        if v.actor.id != self.request.user.id: return Response(status=status.HTTP_404_NOT_FOUND) # 유저가 다른 사람의 영상을 수정하려고 할 때

        serializer = MediaSerializer(v, data=request.data) # 입력 값 역직렬화
        if serializer.is_valid(): # 유효한지 확인
            serializer.save() # 저장
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PhotoView(APIView):
    def get(self, request, iid):
        img = get_object_or_404(Media, pk=iid, is_media=False)
        serializer = MediaSerializer(img)
        return Response(serializer.data)

    def patch(self, request, iid):
        if not self.request.user.is_authenticated: return Response(status=status.HTTP_401_UNAUTHORIZED) # 유저가 로그인 되어있지 않다면 401 오류

        v = Media.objects.get(pk=iid, is_media=False)
        if v.actor.id != self.request.user.id: return Response(status=status.HTTP_404_NOT_FOUND) # 유저가 다른 사람의 이미지를 수정하려고 할 때

        serializer = MediaSerializer(v, data=request.data) # 입력 값 역직렬화
        if serializer.is_valid(): # 유효한지 확인
            serializer.save() # 저장
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)