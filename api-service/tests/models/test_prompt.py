"""Tests for Prompt model."""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.prompt import Prompt


def test_create_prompt(session):
    """Test creating a basic prompt."""
    prompt = Prompt(
        name="classify_item",
        version="v1.0",
        content="Classify the following item: {{item_text}}",
        active=True,
    )
    session.add(prompt)
    session.commit()

    assert prompt.id is not None
    assert isinstance(prompt.id, uuid.UUID)
    assert prompt.name == "classify_item"
    assert prompt.version == "v1.0"
    assert prompt.active is True


def test_prompt_with_model_config(session):
    """Test prompt with model configuration."""
    config = {"temperature": 0.7, "max_tokens": 500, "model": "claude-3-5-sonnet"}
    prompt = Prompt(
        name="chat_prompt",
        version="v2.0",
        content="You are a helpful assistant.",
        model_config=config,
        active=True,
    )
    session.add(prompt)
    session.commit()

    assert prompt.model_config == config
    assert prompt.model_config["temperature"] == 0.7


def test_prompt_unique_name_version(session):
    """Test that name+version must be unique."""
    prompt1 = Prompt(
        name="test_prompt", version="v1.0", content="Content 1", active=True
    )
    session.add(prompt1)
    session.commit()

    prompt2 = Prompt(
        name="test_prompt", version="v1.0", content="Content 2", active=True
    )
    session.add(prompt2)

    with pytest.raises(IntegrityError):
        session.commit()


def test_prompt_same_name_different_version(session):
    """Test that same name with different versions is allowed."""
    prompt1 = Prompt(
        name="versioned", version="v1.0", content="Old version", active=False
    )
    prompt2 = Prompt(
        name="versioned", version="v2.0", content="New version", active=True
    )
    session.add_all([prompt1, prompt2])
    session.commit()

    prompts = session.query(Prompt).filter(Prompt.name == "versioned").all()
    assert len(prompts) == 2


def test_prompt_repr(session):
    """Test Prompt __repr__ method."""
    prompt = Prompt(name="test", version="v1.0", content="Test content", active=True)
    session.add(prompt)
    session.commit()

    repr_str = repr(prompt)
    assert "Prompt" in repr_str
    assert "test" in repr_str
    assert "v1.0" in repr_str
