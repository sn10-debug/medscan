from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import cv2
import numpy as np
from .serializers import ImageUploadSerializer, ReferenceImageUploadSerializer
from .yolo_call import findIntensity

class ImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']

            buffered_image=image.file

            # Read the image using OpenCV
            np_img = np.frombuffer(image.read(), np.uint8)
            img_cv2 = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            findIntensity(buffered_image, img_cv2)

            # Return the image data as a response (for demonstration)
            # You can return other data if needed, like image dimensions, etc.
            return Response({"message": "Image received and converted."})
        else:
            return Response(serializer.errors, status=400)
        


class ReferenceImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        serializer = ReferenceImageUploadSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']

            buffered_image=image.file

            # Read the image using OpenCV
            np_img = np.frombuffer(image.read(), np.uint8)
            img_cv2 = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            result=findIntensity(buffered_image, img_cv2)

            # Return the image data as a response (for demonstration)
            # You can return other data if needed, like image dimensions, etc.
            return Response({"message": "Image received and converted."})
        else:
            return Response(serializer.errors, status=400)
