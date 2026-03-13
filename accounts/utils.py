"""
Utility functions for the accounts app
"""
import uuid
import os


class tenant_gallery_photo_upload_to:
    """
    Serializable callable for TenantPhoto and TenantPhotoRequest ImageField upload_to.

    Both the pending request and the approved photo land in the same folder so
    the file is stored exactly once. No copy happens on approval — only the DB
    reference is transferred.

    Generates a standardized filename:
        tenant_gallery/{tenant_id}_gallery_{short_uuid}.jpg
    Example:
        tenant_gallery/15_gallery_a3f9b2c1.jpg

    Implemented as a class (not a closure) so Django's migration framework
    can serialize and deconstruct it correctly.
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower() or '.jpg'
        short_id = uuid.uuid4().hex[:8]

        # Works for both TenantPhoto (instance.tenant) and
        # TenantPhotoRequest (instance.tenant)
        tenant_id = None
        if hasattr(instance, 'tenant') and instance.tenant_id:
            tenant_id = instance.tenant_id

        prefix = str(tenant_id) if tenant_id else 'unknown'
        return f'tenant_gallery/{prefix}_gallery_{short_id}{ext}'

    def deconstruct(self):
        """Required for Django migration serialization."""
        return (
            'accounts.utils.tenant_gallery_photo_upload_to',
            [self.field_name],
            {},
        )

    def __eq__(self, other):
        return isinstance(other, tenant_gallery_photo_upload_to) and self.field_name == other.field_name

    def __hash__(self):
        return hash(self.field_name)


class tenant_logo_upload_to:
    """
    Serializable callable for TenantLogoRequest and Tenant logo ImageField upload_to.

    Both the pending logo request and the approved logo land in the same folder so
    the file is stored exactly once.

    Generates a standardized filename:
        tenant_logos/{tenant_id}_logo_{short_uuid}.jpg
    Example:
        tenant_logos/15_logo_a3f9b2c1.jpg

    Implemented as a class (not a closure) so Django's migration framework
    can serialize and deconstruct it correctly.
    """

    def __init__(self, field_name):
        self.field_name = field_name

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower() or '.jpg'
        short_id = uuid.uuid4().hex[:8]

        # Works for TenantLogoRequest (instance.tenant_id)
        # and Tenant itself (instance.pk)
        tenant_id = None
        if hasattr(instance, 'tenant') and instance.tenant_id:
            tenant_id = instance.tenant_id
        elif hasattr(instance, 'pk') and instance.pk:
            # Called on Tenant model directly
            tenant_id = instance.pk

        prefix = str(tenant_id) if tenant_id else 'unknown'
        return f'tenant_logos/{prefix}_logo_{short_id}{ext}'

    def deconstruct(self):
        """Required for Django migration serialization."""
        return (
            'accounts.utils.tenant_logo_upload_to',
            [self.field_name],
            {},
        )

    def __eq__(self, other):
        return isinstance(other, tenant_logo_upload_to) and self.field_name == other.field_name

    def __hash__(self):
        return hash(self.field_name)
