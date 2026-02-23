import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class StrongPasswordValidator:
    """
    Requires at least:
      - 8 characters
      - 1 uppercase letter
      - 1 lowercase letter
      - 1 digit
      - 1 special character (!@#$%^&*…)
    """
    SPECIAL = r'[!@#$%^&*()_+\-=\[\]{};\'\\:"|,.<>/?`~]'

    def validate(self, password, user=None):
        errors = []
        if len(password) < 8:
            errors.append(
                ValidationError(
                    _('Şifre en az 8 karakter olmalıdır. / Password must be at least 8 characters.'),
                    code='password_too_short',
                )
            )
        if not re.search(r'[A-Z]', password):
            errors.append(
                ValidationError(
                    _('Şifre en az bir büyük harf içermelidir. / Password must contain at least one uppercase letter.'),
                    code='password_no_upper',
                )
            )
        if not re.search(r'[a-z]', password):
            errors.append(
                ValidationError(
                    _('Şifre en az bir küçük harf içermelidir. / Password must contain at least one lowercase letter.'),
                    code='password_no_lower',
                )
            )
        if not re.search(r'\d', password):
            errors.append(
                ValidationError(
                    _('Şifre en az bir rakam içermelidir. / Password must contain at least one digit.'),
                    code='password_no_digit',
                )
            )
        if not re.search(self.SPECIAL, password):
            errors.append(
                ValidationError(
                    _('Şifre en az bir özel karakter içermelidir (!@#$%^&* vb.). / Password must contain at least one special character (!@#$%^&* etc.).'),
                    code='password_no_special',
                )
            )
        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return _(
            'Şifreniz en az 8 karakter, bir büyük harf, bir küçük harf, bir rakam ve bir özel karakter içermelidir.'
        )
