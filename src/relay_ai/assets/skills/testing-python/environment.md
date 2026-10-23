# Hermetic tests: configuration and environment

A test that passes because the developer's `.env` is filled in fails in CI and on the next
developer's machine; a test that fails because the `.env` is empty fails for the same reason.
Both depend on the environment. This reference covers how each test sets its own configuration,
how the suite switches the real one off, and how to test configuration requirements.

## Each test sets what it uses

- **Inject first.** When the code receives a settings object, build it in the test with explicit
  values. With pydantic-settings, `Settings(_env_file=None, api_key='test-api-key')`:
  `_env_file=None` keeps that instance from reading the `.env`.
- **Variables the code reads**: `monkeypatch.setenv` and `monkeypatch.delenv(name,
  raising=False)` with pytest, `mock.patch.dict(os.environ, {...})` with `unittest`. Both restore
  the environment at the end of the test, while an assignment to `os.environ` stays for every
  later test.
- **Fictitious values** (`'test-api-key'`), written in the test or in its fixture.

## The suite switches the real environment off

An autouse fixture in the root `conftest.py` runs around every test and:

- removes the application's variables, and only those (their names come from the settings model,
  `.env.example` or the code): `PATH`, `HOME` and the temporary folders belong to the machine;
- switches off the configuration file of the loader the project uses (see the table below);
- clears cached settings, such as an `lru_cache` on `get_settings`.

```python
from collections.abc import Iterator

import pytest

from shop.settings import Settings, get_settings

APP_VARIABLES = ('API_KEY', 'DATABASE_URL')


@pytest.fixture(autouse=True)
def hermetic_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    for name in APP_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setitem(Settings.model_config, 'env_file', None)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
```

With this fixture, every run behaves as if the `.env` were empty, on any machine: the ordinary
run of the suite proves the tests are hermetic, and nobody touches the `.env`.

Create it directly in a new suite, or in one whose tests are already hermetic. Where tests rely
on the `.env` today, the fixture makes them fail: point that out, and add it only with the
developer's agreement, in a commit of its own.

## Known loaders

| Loader | Where it looks for the file | Writes to `os.environ` | Switch the file off | Missing required variable |
|---|---|---|---|---|
| pydantic-settings | `env_file`, relative to the current working directory | No | `_env_file=None` on an instance; `monkeypatch.setitem(Settings.model_config, 'env_file', None)` for a test | `ValidationError`, with the field in `loc` |
| python-dotenv | `load_dotenv()` searches from the folder of the file that calls it upwards, whatever the working directory | Yes, for the whole process | Replace `dotenv.load_dotenv` before the application imports it | Whatever the code does without it (`os.environ['API_KEY']` raises `KeyError`) |
| python-decouple | `config` searches from the folder of the calling file upwards; `settings.ini` wins over `.env` in the same folder | No; the file loaded first stays on the module-level `config` object for the whole process | `monkeypatch.setattr(decouple.config, 'config', Config(RepositoryEmpty()))` (`patch.object` with `unittest`) | `UndefinedValueError`: "API_KEY not found. Declare it as envvar or define a default value." |

In all three, an environment variable wins over the file, so `monkeypatch.setenv` works. But
`monkeypatch.delenv` alone doesn't make a variable absent while the file still provides it:
switch the file off too.

Another loader: find out where it looks for its file and whether it writes to `os.environ`, and
switch it off the same way, from the test, undone at the end of it.

## Configuration read at import time

`load_dotenv()` at the top of a module, `settings = Settings()` or `API_KEY = config('API_KEY')`
at module level run when the module is imported. With the `.env` empty, the import fails and
pytest reports the whole test file as a collection error; with the `.env` filled in, its values
leak into the tests. The autouse fixture runs too late for both.

- **Where the framework can read the configuration later**, as FastAPI can in the lifespan, the
  composition root: point out the import-time read as the cause and propose moving it there. It
  is a structural change: make it only with the developer's agreement.
- **Until then, and where reading at import is the framework's design** (Django's
  `settings.py`): at the top of the root `conftest.py`, before anything imports the application,
  switch off the loaders the project uses and give every application variable a fictitious
  value, for the whole session:

```python
import os
from unittest.mock import patch

import decouple
from decouple import Config, RepositoryEmpty

patch('dotenv.load_dotenv', return_value=False).start()
patch.object(decouple.config, 'config', Config(RepositoryEmpty())).start()
patch.dict(os.environ, {'API_KEY': 'test-api-key', 'DATABASE_URL': 'sqlite://'}).start()
```

A pydantic-settings instance created at module level is covered by the fictitious values,
because environment variables win over the `.env`. Import the application below these lines
(with `# noqa: E402`) or inside the fixtures.

## Testing a configuration requirement

"The application refuses to start without `API_KEY`": with the file switched off, remove the
variable and check the error and the variable it names; `parametrize` when the requirement
covers several variables.

```python
import pytest
from pydantic import ValidationError

from shop.settings import Settings


@pytest.mark.parametrize('name', ['API_KEY', 'DATABASE_URL'])
def test_settings_require_variable(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    monkeypatch.setenv('API_KEY', 'test-api-key')
    monkeypatch.setenv('DATABASE_URL', 'sqlite://')
    monkeypatch.delenv(name)

    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)

    assert error.value.errors()[0]['loc'] == (name.lower(),)
```

When the configuration is read at import time, import the module again inside the test. Remove
it from `sys.modules` with `monkeypatch`, which puts the original module back at the end of the
test, so the tests after it are unaffected:

```python
import importlib
import sys

import pytest
from decouple import UndefinedValueError


def test_settings_module_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv('API_KEY', raising=False)
    monkeypatch.delitem(sys.modules, 'shop.settings', raising=False)

    with pytest.raises(UndefinedValueError, match='API_KEY'):
        importlib.import_module('shop.settings')
```

With `unittest`, do the same inside `patch.dict(sys.modules)` and `patch.dict(os.environ)`.
