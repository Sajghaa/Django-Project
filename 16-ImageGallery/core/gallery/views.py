from rest_framework.viewsets import ModelViewSet
from .models import Image
from .serializers import ImageSerializer

class ImageViewSet(ModelViewSet):
    queryset = Image.objects.all().order_by('-created_at')
    serializer_class = ImageSerializer
