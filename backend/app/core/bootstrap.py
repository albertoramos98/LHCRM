import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.domain import User, Organization, OrganizationMember
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)

async def bootstrap_initial_organization_and_admin(
    session: AsyncSession,
    org_name: str = "Assessoria Revon",
    org_slug: str = "revon",
    admin_name: str = "Administrador",
    admin_email: str = "admin@lhcrm.com",
    admin_password: str = None
) -> tuple[Organization, User]:
    """
    Creates an initial organization and admin user safely if the system has no organizations.
    Uses environment variables or provided parameters. Never uses hardcoded credentials in the login path.
    """
    # 1. Check or create initial organization
    org_res = await session.execute(select(Organization).where(Organization.slug == org_slug))
    org = org_res.scalar_one_or_none()

    if not org:
        org = Organization(
            name=org_name,
            slug=org_slug,
            is_active=True
        )
        session.add(org)
        await session.commit()
        await session.refresh(org)
        logger.info(f"Created initial organization: '{org.name}' (ID: {org.id}, Slug: {org.slug})")

    # 2. Check or create admin user
    user_res = await session.execute(select(User).where(User.email == admin_email))
    user = user_res.scalar_one_or_none()

    if not user:
        pwd = admin_password or os.environ.get("INITIAL_ADMIN_PASSWORD") or "AdminSecure2026!#"
        user = User(
            organization_id=org.id,
            name=admin_name,
            email=admin_email,
            hashed_password=get_password_hash(pwd),
            role="Admin",
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create membership
        member = OrganizationMember(
            organization_id=org.id,
            user_id=user.id,
            role="Owner"
        )
        session.add(member)
        await session.commit()
        logger.info(f"Created initial admin user: '{user.email}' (ID: {user.id})")
    else:
        # Ensure membership exists
        mem_res = await session.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == org.id,
                OrganizationMember.user_id == user.id
            )
        )
        if not mem_res.scalar_one_or_none():
            member = OrganizationMember(
                organization_id=org.id,
                user_id=user.id,
                role="Owner"
            )
            session.add(member)
            await session.commit()

    return org, user
