"""Tests for seed data script."""

from app.models.item import EMBEDDING_DIMENSION, Item
from app.models.prompt import Prompt
from app.models.user import User
from migrations.seed_data import seed_database


def test_seed_data_creates_user(session):
    """Test that seed data creates dev user."""
    seed_database(session)

    user = session.query(User).filter(User.email == "dev@noosphere.local").first()
    assert user is not None
    assert user.email == "dev@noosphere.local"


def test_seed_data_creates_prompt(session):
    """Test that seed data creates classification prompt."""
    seed_database(session)

    prompt = (
        session.query(Prompt)
        .filter(Prompt.name == "classify_item", Prompt.version == "v1")
        .first()
    )
    assert prompt is not None
    assert prompt.active is True
    assert "Admin" in prompt.content
    assert "Ideas" in prompt.content


def test_seed_data_creates_items(session):
    """Test that seed data creates sample items."""
    seed_database(session)

    items = session.query(Item).all()
    assert len(items) >= 4  # At least 4 sample items

    # Check categories are represented
    categories = {item.category for item in items}
    assert "Admin" in categories
    assert "Ideas" in categories
    assert "People" in categories
    assert "Projects" in categories


def test_seed_data_idempotent(session):
    """Test that running seed data twice doesn't duplicate."""
    seed_database(session)
    first_count = session.query(Item).count()

    seed_database(session)  # Run again
    second_count = session.query(Item).count()

    assert first_count == second_count  # No duplicates


def test_seed_data_skips_existing_user(session):
    """Test that existing user is not duplicated."""
    # First run - should create user
    seed_database(session)
    first_user_count = (
        session.query(User).filter(User.email == "dev@noosphere.local").count()
    )

    # Second run - should not create duplicate
    seed_database(session)
    second_user_count = (
        session.query(User).filter(User.email == "dev@noosphere.local").count()
    )

    assert first_user_count == 1
    assert second_user_count == 1


def test_seed_data_skips_existing_prompt(session):
    """Test that existing prompt is not duplicated."""
    # First run - should create prompt
    seed_database(session)
    first_prompt_count = (
        session.query(Prompt)
        .filter(Prompt.name == "classify_item", Prompt.version == "v1")
        .count()
    )

    # Second run - should not create duplicate
    seed_database(session)
    second_prompt_count = (
        session.query(Prompt)
        .filter(Prompt.name == "classify_item", Prompt.version == "v1")
        .count()
    )

    assert first_prompt_count == 1
    assert second_prompt_count == 1


def test_seed_data_skips_existing_items(session):
    """Test that existing items are not duplicated."""
    # First run - should create items
    seed_database(session)
    first_item_count = (
        session.query(Item).filter(Item.file_path == "/admin/setup.md").count()
    )

    # Second run - should not create duplicates
    seed_database(session)
    second_item_count = (
        session.query(Item).filter(Item.file_path == "/admin/setup.md").count()
    )

    assert first_item_count == 1
    assert second_item_count == 1


def test_seed_data_embeddings(session):
    """Test that items have correct embedding dimensions."""
    seed_database(session)

    items = session.query(Item).all()
    for item in items:
        if item.embedding is not None:
            assert len(item.embedding) == EMBEDDING_DIMENSION
