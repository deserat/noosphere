"""Tests for UserConfig model."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user_config import UserConfig


def test_create_user_config(session, user):
    """Test creating user configuration."""
    config = UserConfig(
        user_id=user.id, key="vault_path", value={"path": "/home/user/vault"}
    )
    session.add(config)
    session.commit()

    assert config.user_id == user.id
    assert config.key == "vault_path"
    assert config.value["path"] == "/home/user/vault"


def test_user_config_composite_primary_key(session, user):
    """Test that user_id+key is the composite primary key."""
    config1 = UserConfig(user_id=user.id, key="setting1", value={"data": "value1"})
    session.add(config1)
    session.commit()

    # Same user_id and key should fail
    config2 = UserConfig(user_id=user.id, key="setting1", value={"data": "value2"})
    session.add(config2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_user_config_same_key_different_users(session):
    """Test that different users can have same key."""
    from app.models.user import User

    user1 = User(email="user1@example.com")
    user2 = User(email="user2@example.com")
    session.add_all([user1, user2])
    session.commit()

    config1 = UserConfig(user_id=user1.id, key="theme", value={"mode": "dark"})
    config2 = UserConfig(user_id=user2.id, key="theme", value={"mode": "light"})
    session.add_all([config1, config2])
    session.commit()

    configs = session.query(UserConfig).filter(UserConfig.key == "theme").all()
    assert len(configs) == 2


def test_user_config_cascade_delete(session, user):
    """Test that configs are deleted when user is deleted."""
    config = UserConfig(user_id=user.id, key="test_key", value={"test": "data"})
    session.add(config)
    session.commit()

    # Delete user
    session.delete(user)
    session.commit()

    # Config should be deleted
    configs = session.query(UserConfig).filter(UserConfig.user_id == user.id).all()
    assert len(configs) == 0


def test_user_config_repr(session, user):
    """Test UserConfig __repr__ method."""
    config = UserConfig(user_id=user.id, key="test", value={"data": "value"})
    session.add(config)
    session.commit()

    repr_str = repr(config)
    assert "UserConfig" in repr_str
    assert "test" in repr_str
