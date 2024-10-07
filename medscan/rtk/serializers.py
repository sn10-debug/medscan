from rest_framework import serializers
from PIL import Image


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()

class ReferenceImageUploadSerializer(serializers.Serializer):
    image1 = serializers.ImageField(source='image_1')
    image2 = serializers.ImageField(source='image_2')
    class Meta:
        
        # Add the Model of the Reference Image

        # model = ProcessedImage
        fields = ['image_1', 'image_2']

    def validate(self, data):
        image1 = data.get('original_image_1')
        image2 = data.get('original_image_2')

        # Check if both files are provided
        if not image1 or not image2:
            raise serializers.ValidationError("Both images must be provided.")

        # Check if the uploaded files are valid images
        for image in [image1, image2]:
            try:
                img = Image.open(image)
                img.verify()  # Verify that this is an actual image
            except Exception as e:
                raise serializers.ValidationError(f"Invalid image file: {e}")

        return data