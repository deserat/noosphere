"""Placeholder items endpoints for infrastructure testing.

These endpoints return placeholder responses (empty lists, 404s, 501s)
to enable infrastructure testing before real CRUD implementation.

Real implementation will be added in Issue #17.
"""


from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()


class ItemResponse(BaseModel):
    """Item response model (placeholder)."""

    id: str
    title: str
    # More fields will be added in real implementation


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str


@router.get("/", response_model=list[ItemResponse])
async def list_items():
    """List all items (placeholder).

    Returns empty list for infrastructure testing.
    Real implementation in Issue #17.

    Returns:
        Empty list
    """
    return []


@router.get("/{id}", response_model=ErrorResponse, status_code=status.HTTP_404_NOT_FOUND)
async def get_item(id: str):
    """Get item by ID (placeholder).

    Returns 404 for all IDs during infrastructure testing.
    Real implementation in Issue #17.

    Args:
        id: Item ID

    Returns:
        404 Not Found
    """
    return ErrorResponse(detail="Item not found")


@router.post("/", response_model=ErrorResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def create_item():
    """Create item (placeholder).

    Returns 501 Not Implemented.
    Real implementation in Issue #17.

    Returns:
        501 Not Implemented
    """
    return ErrorResponse(detail="Not implemented yet")


@router.put("/{id}", response_model=ErrorResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def update_item(id: str):
    """Update item (placeholder).

    Returns 501 Not Implemented.
    Real implementation in Issue #17.

    Args:
        id: Item ID

    Returns:
        501 Not Implemented
    """
    return ErrorResponse(detail="Not implemented yet")


@router.delete("/{id}", response_model=ErrorResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
async def delete_item(id: str):
    """Delete item (placeholder).

    Returns 501 Not Implemented.
    Real implementation in Issue #17.

    Args:
        id: Item ID

    Returns:
        501 Not Implemented
    """
    return ErrorResponse(detail="Not implemented yet")
