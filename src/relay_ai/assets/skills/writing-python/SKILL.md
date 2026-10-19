---
name: writing-python
description: Defines how Python code is written — English-only code, the ruff configuration (line length, quotes) and the ruff rules that check this style, absolute imports in three sorted blocks, the order of methods, constants and attributes, the layout of hardcoded dictionaries (payloads, API parameters), mandatory native type hints (PEP 695 generics on 3.12+), no comments or docstrings explaining code (only for exceptionally complex business rules), and exception handling (fail fast, catch only at the edge, chain with `from`, never swallow cancellation). The project's own configuration takes precedence. ALWAYS consult this skill when writing, generating, reviewing, refactoring or formatting any Python code, even when nobody explicitly asks to "follow the project's style" — this applies to scripts, modules, classes, standalone functions and code snippets inside answers.
---

# Python code style

This is the default Python code style guide. It complements (does not replace) PEP 8 and
ruff: where they are silent or allow variations, this document fixes the choice. Apply these
rules whenever you **write, generate, edit or review** Python code — including short
snippets inside a chat answer, not only complete files.

## Precedence

1. **The project's explicit configuration wins**: its ruff settings (`[tool.ruff]` in
   `pyproject.toml`, or `ruff.toml`), its Python version (`requires-python`, ruff's
   `target-version`) and any documented coding standard (`CODING_STANDARDS.md`,
   `CONTRIBUTING.md`, `AGENTS.md`). Where they set something, follow them, and point out
   the conflict with this skill if there is one. Never change the project's configuration on
   your own.
2. **This skill** covers everything the project doesn't set.
3. **Undocumented habits of the existing code come last**: new code follows this skill.

The project's Python version decides what syntax is available: `list[str]` needs 3.9,
`X | None` at runtime 3.10, and the type parameter syntax of section 5 needs 3.12.

## English only

All code is written in English, whatever language the developer talks to you in:
identifiers (variables, functions, classes, modules, packages), comments and docstrings where
they are allowed, log messages and exception messages. PEP 8 asks for comments in English
unless you are "120% sure" the code will never be read by someone who doesn't speak your
language, and for English words in identifiers wherever feasible.

Incorrect:
```python
def calcular_frete(pedido: Pedido) -> Decimal:
    if not pedido.itens:
        raise ValueError('pedido sem itens')
    return TAXA_FRETE * len(pedido.itens)
```

Correct:
```python
def calculate_shipping(order: Order) -> Decimal:
    if not order.items:
        raise ValueError('order has no items')
    return SHIPPING_RATE * len(order.items)
```

Two exceptions:

- **Names that mirror an external schema keep their original spelling**: database columns,
  fields of a third-party API, keys of a file format the project doesn't own. A translated
  alias would only add a mapping to maintain and hide the correspondence:
  ```python
  row = {'NM_COMPLETO_POCO': well_name, 'SG_ZONA': zone}
  ```
- **Text shown to end users follows the product's language**: it is content, not code.

## Quick checklist

- [ ] Code in **English**: identifiers, comments, docstrings, log and exception messages
      (except names from external schemas and text shown to end users)
- [ ] Line length: **100 columns**; string quotes: **always single** (`'text'`)
- [ ] After writing code: `ruff check --fix`, then `ruff format`
- [ ] Imports in 3 blocks (stdlib → third party → local), alphabetical within each block,
      `import` before `from ... import`
- [ ] Imports are always **absolute, full path** — never relative (`.`/`..`); check first
      whether the project root is part of the path
- [ ] Inside classes: dunders (fixed semantic order) → every other method in alphabetical
      order (public and private together, including `@classmethod`/`@staticmethod`)
- [ ] Module constants and `__init__` attributes: alphabetical order, unless one depends on
      another
- [ ] Local variables: natural order of use (never alphabetical)
- [ ] Hardcoded dictionaries (payloads/API parameters): keys in alphabetical order, compact
      up to 100 columns, otherwise one key per line with a trailing comma
- [ ] Type hints always on function/method parameters and returns, with the correct type
      (never omitted, never `Any` as a shortcut)
- [ ] Type hints use **native types** (`list[str]`, `dict[str, int]`, `X | None`, `class
      Box[T]`) — `typing` only for what has no native equivalent
- [ ] Comments explaining code are NOT allowed — only for a business rule too complex for
      the code to express, and even then rarely; tool directives (`# noqa: E501`) are not
      comments
- [ ] Docstrings follow the same rule as comments — never redundant with what the type
      hints already say
- [ ] Exceptions: never a bare `except:` nor `except BaseException`; raise as early as
      possible (fail fast); catch only at the edge or when an intermediate layer can
      actually act on the error; always `raise ... from original_error` when re-raising;
      never swallow `asyncio.CancelledError`

---

## 0. Formatting and checks (ruff)

Defaults, when the project doesn't set them:

- **`line-length = 100`** — all code, not only the hardcoded dictionaries of section 4.
  It is the same ruler used there; it is not a number chosen separately.
- **`quote-style = "single"`** — strings always in single quotes (`'like this'`), including
  f-strings (`f'like this {variable}'`) and one-line docstrings. Only use double quotes when
  the string itself contains an apostrophe and that avoids escaping (`"don't break"`).

### Let ruff check what it can

These rules of this skill are checked by ruff rules:

| Rule of this skill | ruff rule |
|---|---|
| Imports sorted in three blocks | `I` |
| Absolute imports | `TID252`, with `ban-relative-imports = "all"` |
| Type hints on every parameter and return, no `Any` | `ANN` |
| Native types and type parameter syntax | `UP` |
| No bare `except:` | `E722` (on by default) |
| `except Exception` only where the handler re-raises or logs the error | `BLE001` |
| Chain with `from` | `B904` |
| Tool directives with a specific code | `PGH003`, `PGH004` |

The configuration for this style:

```toml
[tool.ruff]
line-length = 100

[tool.ruff.format]
quote-style = "single"

[tool.ruff.lint]
extend-select = ["ANN", "B904", "BLE001", "I", "PGH003", "PGH004", "TID252", "UP"]

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"
```

ruff takes the Python version from `requires-python`, so the `UP` rules match the project.

- **After writing or changing Python code**, run `ruff check --fix` and then `ruff format`
  on the files you touched, through the project's tooling (`uv run ruff ...`) or with
  `uvx ruff ...` when ruff isn't a project dependency. The formatter does not sort imports:
  that comes from rule `I` in `ruff check`.
- **If the project has no ruff configuration**, or lacks these rules, propose adding the
  block above. Don't change `pyproject.toml` without the developer's agreement.
- **If the existing code follows another style**, don't reformat files piecemeal inside
  feature changes, which buries the real change in the diff. Propose one formatting-only
  commit and list its hash in `.git-blame-ignore-revs`, so `git blame` skips it (GitHub reads
  the file automatically; locally, `git config blame.ignoreRevsFile .git-blame-ignore-revs`).
- Method and attribute order, dictionary key order and the comment rules are not checked by
  any tool: they depend on you.

---

## 1. Imports

Three blocks, separated by **one blank line**, in this order:

1. Standard library (`os`, `json`, `datetime`...)
2. Third-party libraries (`requests`, `numpy`, `django`...)
3. Local/project modules

Within each block: alphabetical order by module name. `import x` always before
`from x import y` within the same block.

```python
import json
import os
from datetime import datetime

import numpy as np
import requests
from django.conf import settings

from myapp.models import User
from myapp.utils import format_date
```

This is the isort order that ruff's rule `I` applies — it is not a quirk, apply it directly.

### Absolute imports, never relative

Never use relative imports with a dot (`.`, `..`) to reach modules at the same level or
higher, even inside the same package. Always write the full path.

Incorrect (relative import):
```python
from ..models import User
from .utils import format_date
```

Correct (full path):
```python
from myapp.models import User
from myapp.utils import format_date
```

### Before importing, check the project "root"

Projects differ on whether the root folder is part of the import path — for example
`from myapp.models import User` (the root `myapp` is part of the path) vs
`from models import User` (the root is not, only its contents) vs a `src/` layout where
`src` never appears in the import. Writing the wrong full path causes an
`ImportError`/`ModuleNotFoundError`, so don't assume — check before writing a new import:

1. **Look at how neighbouring files in the project already import each other.** It is the
   most reliable signal, because it reflects that specific project's real configuration.
2. If there is no nearby example to compare with, check `pyproject.toml`/`setup.cfg`/
   `setup.py` (`src/` layout vs flat layout, `package_dir`,
   `[tool.setuptools.packages.find]`) to understand whether the root is installed as a
   package.

This holds project by project — don't extrapolate one project's pattern to another.

---

## 2. Order of methods inside classes

Inside a class, methods follow this order:

1. **Dunders**, in a fixed semantic order (not alphabetical), in the sequence below — skip
   the ones the class doesn't have:
   `__init__` → `__new__` → `__repr__` → `__str__` → `__eq__`/`__hash__`/other comparisons →
   `__enter__`/`__exit__` → other dunders (`__len__`, `__iter__`, `__getitem__`, etc.)
2. **Every other method, in a single alphabetical order** — public, private
   (`_prefixed`), `@classmethod` and `@staticmethod` all mixed in the same block, ordered
   only by name. Don't create separate sub-blocks by decorator type.

```python
import os
from decimal import Decimal
from typing import Self


class PaymentClient:
    def __init__(self, api_key: str, timeout: int = 30) -> None:
        self.api_key = api_key
        self.timeout = timeout

    def __repr__(self) -> str:
        return f'PaymentClient(timeout={self.timeout})'

    def _build_headers(self) -> dict[str, str]:
        return {'Authorization': f'Bearer {self.api_key}'}

    @classmethod
    def from_env(cls) -> Self:
        return cls(api_key=os.environ['PAYMENT_API_KEY'])

    def refund(self, charge_id: str, amount: Decimal) -> Refund: ...

    def _validate_amount(self, amount: Decimal) -> None: ...
```

Note that `_build_headers`, `from_env`, `refund` and `_validate_amount` are all in the same
alphabetical block, with no separation for being private, a classmethod or public.

---

## 3. Order of variables, constants and attributes

| Kind | Order |
|---|---|
| Module constants (`UPPER_CASE`, top of the file) | Alphabetical |
| Instance attributes defined in `__init__` | Alphabetical |
| Local variables inside a function | Natural order of use (where the variable becomes needed) — **never** alphabetical |

```python
API_TIMEOUT = 30
BASE_URL = 'https://api.example.com'
MAX_RETRIES = 3


class Client:
    def __init__(self, base_url: str, timeout: int, token: str) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self.token = token

    def fetch(self, endpoint: str) -> dict[str, object]:
        url = f'{self.base_url}/{endpoint}'
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        return response.json()
```

Reading order in the example: `API_TIMEOUT`, `BASE_URL`, `MAX_RETRIES` (constants,
alphabetical) → `base_url`, `timeout`, `token` (attributes, alphabetical) → `url`,
`headers`, `response` (local variables, order of use).

**A value that depends on another comes after it.** Python binds names in order, so a
constant or attribute built from another one must be defined after it — alphabetically,
`API_URL` would come first and raise `NameError`. Only the dependent value moves; the rest
stays alphabetical:

```python
BASE_URL = 'https://api.example.com'
API_URL = f'{BASE_URL}/v1'
```

---

## 4. Hardcoded dictionaries (payloads / API parameters)

This applies to dictionaries written "by hand" in the code — typically the body of an API
call, `params=`, `json=`, configuration kwargs, etc. (it does not apply to dictionaries built
dynamically from business variables.)

Rules:
- **Keys in alphabetical order.**
- **Compact on one line** if the whole line fits within the **100 columns** of `ruff`'s
  `line-length` (section 0) — the same ruler as the rest of the project, not a separate
  limit.
- If it goes past 100 columns, break it into **one key: value per line**, with a
  **trailing comma** after the last item.

The layout is what `ruff format` produces; the key order is up to you. Don't add a trailing
comma to a dictionary that fits on one line: the formatter treats it as a "magic trailing
comma" and keeps the dictionary broken into lines.

Fits in 100 columns → one line:
```python
payload = {'amount': 100, 'currency': 'BRL'}
```

Goes past 100 columns → break, one key per line, trailing comma:
```python
payload = {
    'amount': 15000,
    'currency': 'BRL',
    'customer_id': 'cus_1234567890abcdef',
    'description': 'Annual plan payment with loyalty discount',
    'metadata': {'order_id': 'ord_9876543210', 'source': 'checkout-web'},
}
```

---

## 5. Type hints

Every function/method parameter and every return has a type hint, with the **correct type
of the data** — never leave it out because it seems "obvious", and never use `Any` as a
shortcut to avoid thinking about the right type.

```python
def calculate_discount(price: float, percentage: int) -> float:
    return price - (price * percentage / 100)


class Order:
    def __init__(self, customer_id: str, items: list[str]) -> None:
        self.customer_id = customer_id
        self.items = items

    def total(self, prices: dict[str, float]) -> float:
        return sum(prices[item] for item in self.items)
```

This includes methods that return `None` (such as `__init__`) — the `-> None` is explicit,
not left out.

### Native types, not `typing`

Always prefer the language's native generics and syntax over importing from `typing`:

| Instead of (`typing`) | Use |
|---|---|
| `typing.List[str]` | `list[str]` |
| `typing.Dict[str, int]` | `dict[str, int]` |
| `typing.Tuple[int, int]` | `tuple[int, int]` |
| `typing.Set[str]` | `set[str]` |
| `typing.Optional[str]` | `str \| None` |
| `typing.Union[int, str]` | `int \| str` |
| `typing.Callable[[int], str]` | `collections.abc.Callable[[int], str]` |

```python
def find_user(user_id: str) -> dict[str, str] | None: ...
```

### Generics: type parameter syntax (PEP 695)

On Python 3.12+, generic classes, generic functions and type aliases use the native syntax,
not `TypeVar`, `Generic` or `TypeAlias`:

```python
class Box[T]:
    def __init__(self, item: T) -> None:
        self.item = item


def first[T](items: list[T]) -> T | None:
    return items[0] if items else None


type UserId = str
```

ruff flags the old forms (`UP040`, `UP046`, `UP047`), but its automatic fixes are marked
unsafe because type parameter variance becomes inferred: convert existing code deliberately,
and write new code with the native syntax directly. On Python older than 3.12, `TypeVar` and
`Generic` are still the way.

**What still comes from `typing`** — no native equivalent exists: `Protocol`, `TypedDict`,
`overload`, `ClassVar`, `Final`, `Self` (PEP 673, for methods that return the instance,
such as alternate constructors: the class name would be wrong in a subclass) and `override`
(PEP 698). Use `typing` only when the case needs one of these — never as the first option for
common types.

---

## 6. Comments and docstrings

**General rule: don't write comments explaining what the code does.** Code that needs a
comment to be understood is usually badly written — poor variable/function names, a
function doing too much, badly structured logic. In those cases the fix is to improve the
code (rename, extract a function, simplify), not to document the problem with a comment
next to it.

Incorrect (the comment only repeats what the code already says):
```python
# Sum the total of the order's items
total = sum(item.price for item in order.items)
```

Correct (the variable name already makes it clear, no comment):
```python
order_total = sum(item.price for item in order.items)
```

**Exception — a business rule genuinely too complex for the code to express on its own.**
Here a short comment explaining the business *reason* (not what the line does) is acceptable
— but this is the rare exception, not the norm, and it is usually the human developer who
writes that comment (because they have the business context first hand). If, while
generating code, it seems necessary to comment a complex business rule, it is safer to ask
the user for the exact motivation before inventing an explanation — and even then, treat it
as a one-off exception, not a habit.

### Tool directives are not comments

`# noqa: E501`, `# type: ignore[attr-defined]`, `# pragma: no cover` and
`# fmt: off`/`# fmt: on` are instructions to tools, not explanations: keep them. Always give
the specific code (a blanket `# noqa` or `# type: ignore` is flagged by `PGH004`/`PGH003`),
and use them only when the tool is wrong, never to silence a real problem.

### Docstrings follow the same rule

A docstring that only repeats what the typed signature already says (`Takes an int and
returns a float`) is redundant — and worse than a comment in that sense, because **a
docstring goes stale more easily**: the code changes, nobody remembers to update the text
next to it, and now the documentation lies about the real behaviour. With mandatory type
hints (section 5) already covering parameter and return types, a docstring that only
restates them adds nothing.

The same exception as for comments applies here: write a docstring when the business rule
behind the function is too complex to be clear from names and types alone — not as a
default practice on every function/class/method.

This departs on purpose from PEP 257, which asks for docstrings on every public module,
class and function: don't enable ruff's `D` (pydocstyle) rules.

---

## 7. Exception handling

- **Never a bare `except:` nor `except BaseException`.** They catch even
  `KeyboardInterrupt`/`SystemExit`, which is almost never the intent. Always use a specific
  exception, or at least `except Exception:` when you really need to catch broadly — and
  then only at the edge, where the handler logs or translates the error.
- **Never swallow cancellation in async code.** Don't catch `asyncio.CancelledError` without
  re-raising it: `asyncio.TaskGroup` and `asyncio.timeout()` work through cancellation and
  misbehave when a coroutine swallows it. `except Exception` doesn't catch it —
  `CancelledError` derives from `BaseException` since Python 3.8.
- **Which exception type to raise** (custom per domain vs Python built-in): no fixed rule —
  decide case by case.
- **Raise as early as possible — fail fast.** Validate the precondition at the top of the
  function and raise right there if it fails, instead of nesting the logic inside an
  `if valid:`. Same spirit as an early return, applied to errors.
- **Catch (`try/except`) only at the edge**, or when an intermediate layer can actually act
  on the error (a retry on a transient failure, translating a low-level exception into a
  domain exception). Don't catch in the middle of business logic just to log and re-raise
  right away — that only adds noise; the edge is what really handles it.
- **Always chain with `from`** when raising a different exception inside an `except`, to
  keep the original traceback: `raise NewException(...) from original_error`.

```python
from decimal import Decimal

import requests


def charge_card(amount: Decimal, card: Card) -> Receipt:
    if amount <= 0:
        raise ValueError('amount must be positive')

    try:
        return gateway.charge(amount, card.token)
    except requests.ConnectionError as err:
        raise PaymentGatewayUnavailableError(card.id) from err


def handle_charge_request(request: ChargeRequest) -> ChargeResponse:
    try:
        receipt = charge_card(request.amount, request.card)
    except PaymentGatewayUnavailableError as err:
        return ChargeResponse(status=503, error=str(err))
    except ValueError as err:
        return ChargeResponse(status=400, error=str(err))
    return ChargeResponse(status=200, receipt=receipt)
```

`charge_card` fails fast on validation, and translates the network error into a domain
exception chained with `from`. What actually catches it to decide what to answer is
`handle_charge_request`, at the edge. Amounts of money are `Decimal` (or integer cents),
never `float`: binary floating point can't represent values like `1.1` exactly.

---

## What this skill does NOT cover

Out of scope (follow standard PEP 8/ruff, or ask the user if a new case comes up):
- Naming of variables/functions/classes (`snake_case`, `PascalCase` etc. — already
  standard)
- Any other ruff rule the project configures: it follows the project (see Precedence).

If a case not covered here comes up, ask the user how they prefer it rather than assume. If
the answer looks like a general rule (not specific to that file), suggest recording it in
the project's own coding standard (`CODING_STANDARDS.md` or `AGENTS.md`), which takes
precedence over this skill — edits to this skill itself are overwritten by
`relay-ai update`.
