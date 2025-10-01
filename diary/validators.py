import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class AlphaNumericCombinationValidator:
    """
    パスワードは英字と数字をそれぞれ1文字以上含める
    """
    message = _("パスワードは英字と数字をそれぞれ1文字以上含めてください。")
    code = "password_no_alpha_numeric_combo"

    def validate(self, password, user=None):
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValidationError(self.message, code=self.code)

    def get_help_text(self):
        return self.message
