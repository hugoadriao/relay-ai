# Async tests

Pick the mechanism by what the project declares (see "Tools" in [SKILL.md](SKILL.md)): the first
one available wins.

## pytest-asyncio

Use it in the mode the pytest configuration sets (`asyncio_mode`):

- **strict**, the default: mark every async test with `@pytest.mark.asyncio` and declare async
  fixtures with `@pytest_asyncio.fixture`. An unmarked async test fails with "async def
  functions are not natively supported". The order of the `asyncio` and `parametrize` marks
  doesn't matter.
- **auto**: async tests and fixtures need no marker.

## anyio, declared by the project

Mark async tests with `@pytest.mark.anyio`, and define the backend once, in the root
`conftest.py`:

```python
import pytest


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'
```

FastAPI, Starlette and httpx depend on anyio, so its pytest plugin is often importable even
when the project doesn't declare it; it counts only when the project declares `anyio` itself.

## Neither: `asyncio.run` inside a sync test

The test stays a plain pytest function, so `mocker`, fixtures and `parametrize` keep working,
and it runs the async part with `asyncio.run`:

```python
import asyncio
from decimal import Decimal

from pytest_mock import MockerFixture

from shop.checkout import checkout
from shop.prices import PriceClient


def test_member_pays_discounted_price(mocker: MockerFixture) -> None:
    prices = mocker.create_autospec(PriceClient, instance=True)
    prices.fetch.return_value = Decimal(100)

    total = asyncio.run(checkout(prices, member=True))

    assert total == Decimal(90)
```

Each `asyncio.run` starts a new event loop. When the setup is async too, or the test uses
objects bound to a loop (clients, locks, queues), write the whole scenario as one `async def`
and run it once.

FastAPI's `TestClient` is synchronous: endpoint tests through it need none of this.

## unittest

`unittest.IsolatedAsyncioTestCase`: `async def test_*` methods, `asyncSetUp` for async setup and
`addAsyncCleanup` for teardown. pytest runs these classes without any async plugin.
