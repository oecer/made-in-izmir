"""
Management command: sync_subscriptions

Finds TenantSubscriptions where expires_at < today and status == 'active',
marks them as 'expired', and syncs Tenant.show_company_profile accordingly.

Run daily via cron:
    python manage.py sync_subscriptions
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from subscriptions.models import TenantSubscription


class Command(BaseCommand):
    help = 'Marks expired subscriptions as expired and syncs tenant features.'

    def handle(self, *args, **options):
        today = timezone.now().date()

        expired_qs = TenantSubscription.objects.filter(
            status='active',
            expires_at__lt=today,
        ).select_related('tenant', 'plan')

        count = expired_qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No subscriptions to expire.'))
            return

        for sub in expired_qs:
            sub.status = 'expired'
            # save() will sync tenant.show_company_profile via the override
            sub.save()
            self.stdout.write(
                f'  Expired: {sub.tenant.company_name} (was: {sub.plan.name_tr})'
            )

        self.stdout.write(
            self.style.SUCCESS(f'Done. {count} subscription(s) marked as expired.')
        )
