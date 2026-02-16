from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify

from apps.tenant.models import Tenant, Domain


class Command(BaseCommand):
    help = "Create a tenant and its primary domain."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True, help="Tenant display name")
        parser.add_argument("--schema", required=False, help="Schema name (defaults to slugified name)")
        parser.add_argument("--domain", required=True, help="Primary domain or subdomain")
        parser.add_argument("--paid-until", required=False, help="YYYY-MM-DD")
        parser.add_argument(
            "--on-trial",
            required=False,
            default="true",
            help="true or false (default: true)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        name = options["name"].strip()
        schema_name = options.get("schema") or slugify(name).replace("-", "")
        domain_name = options["domain"].strip().lower()
        paid_until = options.get("paid_until")
        on_trial = options.get("on_trial", "true").lower() == "true"

        if not schema_name:
            raise CommandError("Schema name could not be derived. Provide --schema.")

        if Tenant.objects.filter(schema_name=schema_name).exists():
            raise CommandError(f"Tenant with schema '{schema_name}' already exists.")

        if Domain.objects.filter(domain=domain_name).exists():
            raise CommandError(f"Domain '{domain_name}' is already in use.")

        tenant = Tenant(
            name=name,
            schema_name=schema_name,
            paid_until=paid_until,
            on_trial=on_trial,
        )
        tenant.save()

        Domain.objects.create(
            domain=domain_name,
            tenant=tenant,
            is_primary=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created tenant '{name}' with schema '{schema_name}' and domain '{domain_name}'."
            )
        )
