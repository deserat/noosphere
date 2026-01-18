"""Tests for ItemLink model."""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.item import Item
from app.models.item_link import ItemLink


def test_create_item_link(session, user, item):
    """Test creating an item link."""
    item2 = Item(
        title="Related Item",
        file_path="/related.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item2)
    session.commit()

    link = ItemLink(
        from_item_id=item.id,
        to_item_id=item2.id,
        link_type="related",
        why_related="Both discuss similar topics",
        confidence=0.85,
    )
    session.add(link)
    session.commit()

    assert link.id is not None
    assert isinstance(link.id, uuid.UUID)
    assert link.from_item_id == item.id
    assert link.to_item_id == item2.id
    assert link.link_type == "related"
    assert link.confidence == 0.85


def test_item_link_no_self_links(session, user, item):
    """Test that an item cannot link to itself."""
    link = ItemLink(
        from_item_id=item.id,
        to_item_id=item.id,
        link_type="self",
    )
    session.add(link)

    with pytest.raises(IntegrityError):
        session.commit()


def test_item_link_unique_constraint(session, user, item):
    """Test that from_item+to_item+link_type must be unique."""
    item2 = Item(
        title="Target",
        file_path="/target.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item2)
    session.commit()

    link1 = ItemLink(
        from_item_id=item.id,
        to_item_id=item2.id,
        link_type="references",
    )
    session.add(link1)
    session.commit()

    # Same from, to, and type should fail
    link2 = ItemLink(
        from_item_id=item.id,
        to_item_id=item2.id,
        link_type="references",
    )
    session.add(link2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_item_link_different_types_allowed(session, user, item):
    """Test that same items with different link types is allowed."""
    item2 = Item(
        title="Multi-linked",
        file_path="/multi.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item2)
    session.commit()

    link1 = ItemLink(
        from_item_id=item.id, to_item_id=item2.id, link_type="related"
    )
    link2 = ItemLink(
        from_item_id=item.id, to_item_id=item2.id, link_type="references"
    )
    session.add_all([link1, link2])
    session.commit()

    links = (
        session.query(ItemLink)
        .filter(
            ItemLink.from_item_id == item.id, ItemLink.to_item_id == item2.id
        )
        .all()
    )
    assert len(links) == 2


def test_item_link_cascade_delete(session, user, item):
    """Test that links are deleted when items are deleted."""
    item2 = Item(
        title="Will be deleted",
        file_path="/delete.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item2)
    session.commit()

    link = ItemLink(
        from_item_id=item.id,
        to_item_id=item2.id,
        link_type="related",
    )
    session.add(link)
    session.commit()

    link_id = link.id

    # Delete item2
    session.delete(item2)
    session.commit()

    # Link should be deleted
    deleted_link = session.query(ItemLink).filter(ItemLink.id == link_id).first()
    assert deleted_link is None


def test_item_link_repr(session, user, item):
    """Test ItemLink __repr__ method."""
    item2 = Item(
        title="Link target",
        file_path="/target.md",
        user_id=user.id,
        no_ai=False,
    )
    session.add(item2)
    session.commit()

    link = ItemLink(
        from_item_id=item.id,
        to_item_id=item2.id,
        link_type="depends-on",
    )
    session.add(link)
    session.commit()

    repr_str = repr(link)
    assert "ItemLink" in repr_str
    assert "depends-on" in repr_str
