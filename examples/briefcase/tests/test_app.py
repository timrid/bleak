import asyncio

from bleak import BleakScanner


def test_first():
    """An initial test for the app."""
    assert 1 + 1 == 2


async def test_bleak_scanner():
    async with BleakScanner() as scanner:
        await asyncio.sleep(5)
        assert len(scanner.discovered_devices) == 1


async def test_bleak_scanner2():
    result = await BleakScanner.discover(return_adv=True)
    assert len(result) == 1
