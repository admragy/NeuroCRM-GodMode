#!/usr/bin/env python3
"""
Create Admin User Script
Usage: python scripts/create_admin.py
"""

import sys
import os
import asyncio
from getpass import getpass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db, engine
from app.core.security import get_password_hash, check_password_strength
from app.models.user import User
from app.models.organization import Organization, SubscriptionPlan, SubscriptionStatus


async def create_admin_user():
    """Create admin user interactively"""
    
    print("=" * 60)
    print("🔐 OmniCRM - Admin User Creation")
    print("=" * 60)
    print()
    
    # Collect information
    print("📧 Admin Email:")
    email = input("> ").strip()
    
    if not email or '@' not in email:
        print("❌ Invalid email address")
        return
    
    print("\n👤 Full Name:")
    full_name = input("> ").strip()
    
    print("\n🔒 Password:")
    password = getpass("> ")
    
    print("\n🔒 Confirm Password:")
    password_confirm = getpass("> ")
    
    if password != password_confirm:
        print("❌ Passwords do not match")
        return
    
    # Check password strength
    strength = check_password_strength(password)
    
    if not strength['is_strong']:
        print(f"\n⚠️  Password is {strength['strength']}")
        print("Suggestions:")
        for suggestion in strength['suggestions']:
            print(f"  - {suggestion}")
        
        print("\nContinue anyway? (y/N)")
        if input("> ").lower() != 'y':
            print("❌ Aborted")
            return
    
    # Organization details
    print("\n🏢 Organization Name:")
    org_name = input("> ").strip() or "Default Organization"
    
    print("\n🌐 Subdomain (e.g., mycompany):")
    subdomain = input("> ").strip().lower()
    
    if not subdomain:
        subdomain = org_name.lower().replace(' ', '-')[:63]
    
    # Create organization and user
    async for db in get_db():
        try:
            # Check if organization exists
            from sqlalchemy import select
            
            result = await db.execute(
                select(Organization).where(Organization.subdomain == subdomain)
            )
            organization = result.scalar_one_or_none()
            
            if organization:
                print(f"\n⚠️  Organization with subdomain '{subdomain}' already exists")
                print("Use this organization? (y/N)")
                if input("> ").lower() != 'y':
                    print("❌ Aborted")
                    return
            else:
                # Create organization
                organization = Organization(
                    name=org_name,
                    subdomain=subdomain,
                    slug=subdomain,
                    plan=SubscriptionPlan.ENTERPRISE,
                    subscription_status=SubscriptionStatus.ACTIVE,
                    owner_email=email,
                    is_active=True,
                    is_verified=True,
                    max_users=999,
                    max_customers=999999,
                    max_ai_requests_per_month=999999
                )
                db.add(organization)
                await db.flush()
                print(f"✅ Organization created: {org_name}")
            
            # Check if user exists
            result = await db.execute(
                select(User).where(User.email == email)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"\n❌ User with email '{email}' already exists")
                return
            
            # Create admin user
            hashed_password = get_password_hash(password)
            
            admin_user = User(
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                organization_id=organization.id,
                is_active=True,
                is_superuser=True,
                is_verified=True
            )
            
            db.add(admin_user)
            await db.commit()
            
            print("\n" + "=" * 60)
            print("✅ Admin user created successfully!")
            print("=" * 60)
            print(f"\n📧 Email: {email}")
            print(f"👤 Name: {full_name}")
            print(f"🏢 Organization: {org_name} ({subdomain})")
            print(f"🔑 Role: Superuser (Admin)")
            print(f"📦 Plan: Enterprise (Unlimited)")
            print(f"\n🌐 Login URL: http://localhost:{os.getenv('PORT', 5000)}/api/auth/login")
            print()
            
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Error creating admin user: {str(e)}")
            raise
        
        break  # Exit the async for loop


if __name__ == "__main__":
    asyncio.run(create_admin_user())
