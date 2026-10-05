import re
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


def _supabase_project_ref(endpoint: str) -> str:
    # endpoint looks like: https://krxoefmzrsvqzrxkgjoz.supabase.co/storage/v1/s3
    match = re.match(r"https://([^.]+)\.supabase\.co", endpoint)
    return match.group(1) if match else ""


class SupabaseMediaStorage(S3Boto3Storage):
    """
    Uploads still go through the normal S3-compatible protocol (handled by
    the parent class), but Supabase serves PUBLIC files through a different
    URL shape than the one used for upload/auth. This override makes the
    .url() Django/DRF actually show point at that public path instead.
    """
    def url(self, name, parameters=None, expire=None, http_method=None):
        ref = _supabase_project_ref(settings.AWS_S3_ENDPOINT_URL)
        return f"https://{ref}.supabase.co/storage/v1/object/public/{self.bucket_name}/{name}"
