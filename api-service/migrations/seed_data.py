"""
Seed data script for development environment.

Creates:
- Development user (dev@noosphere.local)
- Classification prompt v1
- Sample items across all categories

Idempotent: Safe to run multiple times.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal  # noqa: E402
from app.models.item import Item, ItemState  # noqa: E402
from app.models.prompt import Prompt  # noqa: E402
from app.models.user import User  # noqa: E402


def seed_database(session=None) -> None:
    """
    Seed database with development data.

    Args:
        session: Optional SQLAlchemy session to use. If None, creates a new session.
    """
    if session is None:
        session = SessionLocal()
        should_close = True
    else:
        should_close = False

    try:
        # 1. Create dev user (if not exists)
        user = session.query(User).filter(User.email == "dev@noosphere.local").first()
        if not user:
            user = User(email="dev@noosphere.local")
            session.add(user)
            session.flush()  # Get user.id for foreign keys
            print("✓ Created dev user: dev@noosphere.local")
        else:
            print("○ Dev user already exists")

        # 2. Create classification prompt v1 (if not exists)
        prompt = (
            session.query(Prompt)
            .filter(Prompt.name == "classify_item", Prompt.version == "v1")
            .first()
        )
        if not prompt:
            prompt = Prompt(
                name="classify_item",
                version="v1",
                content="""You are a knowledge management assistant. Classify items into categories:
- Admin: Administrative tasks, settings, configuration
- Ideas: Concepts, brainstorms, future possibilities
- People: Contacts, relationships, networks
- Projects: Active work, goals, initiatives
- Notes: General information, references, documentation

Analyze the item and provide:
1. Primary category
2. Subcategory (if applicable)
3. Suggested tags
4. Confidence score (0-1)
5. Recommended cadence for review""",
                active=True,
            )
            session.add(prompt)
            print("✓ Created classification prompt v1")
        else:
            print("○ Classification prompt v1 already exists")

        # 3. Create sample items (if not exist)
        sample_items = [
            {
                "title": "Setup Development Environment",
                "file_path": "/admin/setup.md",
                "category": "Admin",
                "subcategory": "Development",
                "tags": ["setup", "development", "environment"],
                "state": ItemState.COMPLETED,
                "confidence": 0.95,
            },
            {
                "title": "Feature Idea: Multi-user Support",
                "file_path": "/ideas/multi-user.md",
                "category": "Ideas",
                "subcategory": "Features",
                "tags": ["feature", "collaboration", "future"],
                "state": ItemState.UNCATEGORIZED,
                "confidence": 0.85,
            },
            {
                "title": "Contact: Jane Doe (Design Consultant)",
                "file_path": "/people/jane-doe.md",
                "category": "People",
                "subcategory": "Consultants",
                "tags": ["design", "consultant", "contact"],
                "state": ItemState.NOT_STARTED,
                "confidence": 0.90,
            },
            {
                "title": "Project: Noosphere Knowledge System",
                "file_path": "/projects/noosphere.md",
                "category": "Projects",
                "subcategory": "Active",
                "tags": ["knowledge", "system", "active"],
                "state": ItemState.IN_PROGRESS,
                "confidence": 1.0,
                "cadence": "daily",
            },
        ]

        items_created = 0
        items_skipped = 0

        for item_data in sample_items:
            existing = (
                session.query(Item)
                .filter(Item.file_path == item_data["file_path"])
                .first()
            )

            if not existing:
                item = Item(
                    user_id=user.id,
                    embedding=[0.0] * 1536,  # Placeholder embedding
                    no_ai=False,
                    **item_data,
                )
                session.add(item)
                items_created += 1
                print(f"✓ Created item: {item_data['title']}")
            else:
                items_skipped += 1
                print(f"○ Item already exists: {item_data['title']}")

        # Commit all changes
        session.commit()

        print("\n" + "=" * 50)
        print("Seed data summary:")
        print(f"  Items created: {items_created}")
        print(f"  Items skipped: {items_skipped}")
        print("=" * 50)

    except Exception as e:
        session.rollback()
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        if should_close:
            session.close()


if __name__ == "__main__":
    print("Seeding development database...")
    seed_database()
    print("Done!")
