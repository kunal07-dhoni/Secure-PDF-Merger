"""
Script to create an admin/superuser from command line.
Usage: python -m scripts.create_superuser
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session_factory, init_db
from app.models.user import User
from app.utils.security import hash_password


async def create_superuser():
    await init_db()

    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    full_name = input("Full Name (optional): ").strip() or None

    async with async_session_factory() as session:
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.commit()
        print(f"\n✅ Superuser '{username}' created successfully!")
        print(f"   ID: {user.id}")
        print(f"   Email: {email}")


if __name__ == "__main__":
    asyncio.run(create_superuser())