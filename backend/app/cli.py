import asyncio
import sys
import argparse
from app.core.database import AsyncSessionLocal
from app.core.bootstrap import bootstrap_initial_organization_and_admin
from app.core.security import get_password_hash
from app.models.domain import User, Organization, OrganizationMember
from sqlalchemy import select

async def cmd_seed_admin(args):
    async with AsyncSessionLocal() as session:
        org, user = await bootstrap_initial_organization_and_admin(
            session=session,
            org_name=args.org_name or "Assessoria Revon",
            org_slug=args.org_slug or "revon",
            admin_name=args.admin_name or "Administrador",
            admin_email=args.admin_email or "admin@lhcrm.com",
            admin_password=args.admin_password
        )
        print(f"SUCCESS: Organization '{org.name}' and Admin '{user.email}' configured.")

async def cmd_create_org(args):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Organization).where(Organization.slug == args.slug))
        if res.scalar_one_or_none():
            print(f"ERROR: Organization with slug '{args.slug}' already exists.")
            return
        org = Organization(name=args.name, slug=args.slug, is_active=True)
        session.add(org)
        await session.commit()
        await session.refresh(org)
        print(f"SUCCESS: Created organization '{org.name}' (ID: {org.id}, Slug: {org.slug}).")

async def main():
    parser = argparse.ArgumentParser(description="LHCRM Administrative CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Seed Admin
    seed_parser = subparsers.add_parser("seed-admin", help="Seed initial organization and admin user")
    seed_parser.add_argument("--org-name", default="Assessoria Revon")
    seed_parser.add_argument("--org-slug", default="revon")
    seed_parser.add_argument("--admin-name", default="Administrador")
    seed_parser.add_argument("--admin-email", default="admin@lhcrm.com")
    seed_parser.add_argument("--admin-password", required=False, default=None)

    # Create Org
    org_parser = subparsers.add_parser("create-org", help="Create a new tenant organization")
    org_parser.add_argument("--name", required=True)
    org_parser.add_argument("--slug", required=True)

    args = parser.parse_args()
    if args.command == "seed-admin":
        await cmd_seed_admin(args)
    elif args.command == "create-org":
        await cmd_create_org(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
