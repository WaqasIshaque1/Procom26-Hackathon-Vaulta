"""
Unit Tests for Banking Tools
"""

import pytest
from app.services.banking_api import (
    verify_identity,
    get_account_balance,
    get_recent_transactions,
    block_card
)


@pytest.mark.asyncio
async def test_verify_identity_success():
    """Test successful identity verification."""
    result = await verify_identity("1234", "5678")
    assert result is True


@pytest.mark.asyncio
async def test_verify_identity_failure():
    """Test failed identity verification."""
    result = await verify_identity("1234", "0000")
    assert result is False


@pytest.mark.asyncio
async def test_get_balance_verified():
    """Test balance retrieval for verified customer."""
    balance = await get_account_balance("1234")
    assert "balance" in balance
    assert balance["balance"] == 1250.50


@pytest.mark.asyncio
async def test_block_card():
    """Test card blocking functionality."""
    result = await block_card("CARD_001", "lost")
    assert "SUCCESS" in result
    assert "CARD_001" in result
