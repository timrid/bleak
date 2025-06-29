import asyncio

import pytest

from bleak import BleakScanner


def test_first():
    """An initial test for the app."""
    assert 1 + 1 == 2

@pytest.mark.asyncio
async def test_bleak_scanner():
    async with BleakScanner() as scanner:
        await asyncio.sleep(1)
        assert len(scanner.discovered_devices_and_advertisement_data) == 0
