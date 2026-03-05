from django.db import migrations


# Models moved from main → new app labels
_MOVES = [
    ('accounts', 'signuprequest'),
    ('accounts', 'signuprequesthistory'),
    ('accounts', 'consenttext'),
    ('accounts', 'membershipconsent'),
    ('accounts', 'tenant'),
    ('accounts', 'userprofile'),
    ('accounts', 'profileeditrequest'),
    ('catalog', 'sector'),
    ('catalog', 'producttag'),
    ('catalog', 'productrequest'),
    ('catalog', 'product'),
    ('expos', 'expo'),
    ('expos', 'exposignup'),
]


def fix_content_types(apps, schema_editor):
    """
    post_migrate auto-created new-app CT rows + permissions after accounts/catalog/expos
    0001_initial ran.  The old 'main.*' CT rows are the originals whose PKs are
    referenced by existing admin_log / permission data.

    Strategy per model:
      1. Delete the duplicate permissions tied to the new CT (old CT already has them).
      2. Re-point any admin LogEntry rows from new CT → old CT (safety measure).
      3. Delete the new CT row.
      4. Rename old CT's app_label to the new app.

    If no old CT exists (brand-new DB with no prior data) the new CT is already correct.
    """
    from django.contrib.contenttypes.models import ContentType
    from django.contrib.auth.models import Permission
    try:
        from django.contrib.admin.models import LogEntry
        has_logentry = True
    except ImportError:
        has_logentry = False

    for new_app, model in _MOVES:
        old_ct = ContentType.objects.filter(app_label='main', model=model).first()
        new_ct = ContentType.objects.filter(app_label=new_app, model=model).first()

        if old_ct and new_ct:
            # old_ct already has the correct permissions; delete duplicates on new_ct
            Permission.objects.filter(content_type=new_ct).delete()
            if has_logentry:
                LogEntry.objects.filter(content_type=new_ct).update(content_type=old_ct)
            new_ct.delete()
            old_ct.app_label = new_app
            old_ct.save()
        elif old_ct and not new_ct:
            old_ct.app_label = new_app
            old_ct.save()
        # Only new_ct (brand-new DB): already correct, nothing to do


class Migration(migrations.Migration):
    """
    State-only migration: removes all models from main's migration state
    that have been relocated to accounts/, catalog/, and expos/.
    No database operations are performed – tables remain untouched.
    """

    dependencies = [
        ('main', '0017_alter_tenant_owner'),
        ('accounts', '0001_initial'),
        ('catalog', '0001_initial'),
        ('expos', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # expos (child of expo/product)
                migrations.DeleteModel(name='ExpoSignup'),
                migrations.DeleteModel(name='Expo'),
                # catalog (product children first)
                migrations.DeleteModel(name='ProductRequest'),
                migrations.DeleteModel(name='Product'),
                migrations.DeleteModel(name='ProductTag'),
                migrations.DeleteModel(name='Sector'),
                # accounts (dependents first)
                migrations.DeleteModel(name='SignupRequestHistory'),
                migrations.DeleteModel(name='MembershipConsent'),
                migrations.DeleteModel(name='ProfileEditRequest'),
                migrations.DeleteModel(name='UserProfile'),
                migrations.DeleteModel(name='Tenant'),
                migrations.DeleteModel(name='ConsentText'),
                migrations.DeleteModel(name='SignupRequest'),
            ],
            database_operations=[],
        ),
        # Fix content types: post_migrate auto-created new-app content type rows
        # (and permissions) after accounts/catalog/expos 0001_initial ran.
        # Strategy: for each moved model, point all existing FK references
        # (auth_permission, django_admin_log) to the OLD main content type row,
        # then delete the new-app row, then rename the old row's app_label.
        # This preserves PKs so all historical references stay intact.
        migrations.RunPython(fix_content_types, reverse_code=migrations.RunPython.noop),
    ]
