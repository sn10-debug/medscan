from utils.storage import AWSStorage


def save_image(image, path="images/"):
    from core.models import Media

    storage = AWSStorage()
    s3_response = storage.write(path=path, file=image)
    url = "https://s3.ap-south-1.amazonaws.com/{}/{}".format(storage.bucket_name, s3_response.key)
    utag = s3_response.e_tag.replace('"', "")

    media, _ = Media.objects.update_or_create(
        utag=utag,
        defaults={"url": url},
    )

    return media
