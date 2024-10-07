from django.db import models
from utils.abstracts import AbstractTimestampModel, AbstractUUIDModel
from utils.storage import AWSStorage


class Media(AbstractUUIDModel, AbstractTimestampModel):
    url = models.URLField()
    utag = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "media"
        verbose_name = "Media"
        verbose_name_plural = "Media"

    def __str__(self):
        return self.url

    @property
    def bucket_name(self):
        return self.url.split("/")[3]

    @property
    def key(self):
        return "/".join(self.url.split("/")[4:])

    @property
    def signed_url(self):
        _url = AWSStorage.get_signed_url(self.bucket_name, self.key)
        return _url

    def signed_url_with_expiration(self, expiration=3600):
        _url = AWSStorage.get_signed_url(self.bucket_name, self.key, expiration=expiration)
        return _url
