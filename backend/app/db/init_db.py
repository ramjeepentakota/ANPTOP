"""
ANPTOP Backend - Database Initialization
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import engine, async_session_factory
from app.models.user import User, UserRole


async def init_default_users(db: AsyncSession) -> None:
    """Initialize default admin user if not exists."""
    # Import here to avoid circular import
    from app.core.security import get_password_hash, generate_mfa_secret
    
    # Check if admin exists
    admin = await User.get_by_email(db, "admin@anptop.local")
    if admin:
        return
    
    # Create admin user
    admin = User(
        email="admin@anptop.local",
        username="admin",
        hashed_password=get_password_hash("ChangeMe123!"),
        full_name="System Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True,
        mfa_secret=generate_mfa_secret(),
    )
    db.add(admin)
    
    # Create default lead tester
    lead = User(
        email="lead@anptop.local",
        username="leadtester",
        hashed_password=get_password_hash("LeadTest123!"),
        full_name="Lead Tester",
        role=UserRole.LEAD,
        is_active=True,
        mfa_secret=generate_mfa_secret(),
    )
    db.add(lead)
    
    # Create default senior tester
    senior = User(
        email="senior@anptop.local",
        username=" seniortester",
        hashed_password=get_password_hash("SeniorTest123!"),
        full_name="Senior Tester",
        role=UserRole.SENIOR,
        is_active=True,
        mfa_secret=generate_mfa_secret(),
    )
    db.add(senior)
    
    # Create default analyst
    analyst = User(
        email="analyst@anptop.local",
        username="analyst",
        hashed_password=get_password_hash("Analyst123!"),
        full_name="Security Analyst",
        role=UserRole.ANALYST,
        is_active=True,
        mfa_secret=generate_mfa_secret(),
    )
    db.add(analyst)
    
    await db.commit()
    print("✅ Default users created")
    print("   - admin@anptop.local (password: ChangeMe123!)")
    print("   - lead@anptop.local (password: LeadTest123!)")
    print("   - senior@anptop.local (password: SeniorTest123!)")
    print("   - analyst@anptop.local (password: Analyst123!)")


async def init_db() -> None:
    """Initialize database with all tables and default data."""
    print("📦 Initializing ANPTOP Database...")
    
    # Create all tables
    from app.db.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database tables created")
    
    # Create default users
    async with async_session_factory() as db:
        await init_default_users(db)
    
    print("🎉 Database initialization complete")


if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
