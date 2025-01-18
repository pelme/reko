import subprocess
import tempfile
from collections.abc import Sequence
from shutil import which
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage


class EmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        for message in email_messages:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as f:
                f.write(message.message().as_bytes())

            subprocess.run(["open" if which("open") else "xdg-open", f.name])

            print(f"\033[94m>>>\033[0m Email was sent to {', '.join(message.recipients())}")

        return len(email_messages)
