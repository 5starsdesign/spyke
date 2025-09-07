import csv
import sys

from django.core.management.base import BaseCommand

from newsletter.models import Signup


class Command(BaseCommand):
    help = "Exporteer newsletter signups naar CSV (stdout of pad)."

    def add_arguments(self, parser):
        parser.add_argument("--out", help="Pad naar CSV-bestand (default: stdout)")

    def handle(self, *args, **opts):
        qs = Signup.objects.all().order_by("-created_at")
        fields = ["created_at", "email", "ip", "user_agent"]
        if opts.get("out"):
            f = open(opts["out"], "w", newline="", encoding="utf-8")
        else:
            f = sys.stdout
        w = csv.writer(f)
        w.writerow(fields)
        for s in qs:
            w.writerow(
                [s.created_at.isoformat(), s.email, s.ip or "", s.user_agent or ""]
            )
        if opts.get("out"):
            f.close()
            self.stdout.write(self.style.SUCCESS(f"CSV geschreven: {opts['out']}"))
