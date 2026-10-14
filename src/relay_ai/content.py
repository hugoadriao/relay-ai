import io
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from importlib.resources import as_file, files
from importlib.resources.abc import Traversable
from pathlib import Path

from relay_ai import console
from relay_ai.errors import SetupError

AGENT_SUFFIX = '.agent.md'
MATTPOCOCK_CATEGORIES = ('engineering', 'productivity')
MATTPOCOCK_REF = 'main'
MATTPOCOCK_ZIP_URL = (
    f'https://codeload.github.com/mattpocock/skills/zip/refs/heads/{MATTPOCOCK_REF}'
)
SKILL_FILE = 'SKILL.md'


@dataclass(frozen=True)
class Agent:
    description: str
    file_name: str
    name: str


def asset(name: str) -> Traversable:
    return files('relay_ai') / 'assets' / name


def install_mattpocock_skills(target: Path, owned: set[str]) -> list[str]:
    console.info(f'Downloading mattpocock/skills ({MATTPOCOCK_REF})...')
    archive = _download(MATTPOCOCK_ZIP_URL)

    installed = []
    with tempfile.TemporaryDirectory() as workdir:
        zipfile.ZipFile(io.BytesIO(archive)).extractall(workdir)
        repository = next(Path(workdir).iterdir())
        license_file = repository / 'LICENSE'
        for category in MATTPOCOCK_CATEGORIES:
            for skill in _skill_dirs(repository / 'skills' / category):
                destination = target / skill.name
                if not _can_replace(destination, owned):
                    continue
                _replace_dir(skill, destination)
                shutil.copy2(license_file, destination / 'LICENSE')
                installed.append(skill.name)
    return installed


def install_relay_agents(target: Path, owned: set[str]) -> list[Agent]:
    source = asset('agents')
    if not source.is_dir():
        return []

    installed = []
    with as_file(source) as agents_dir:
        agent_files = sorted(agents_dir.glob(f'*{AGENT_SUFFIX}'))
        if agent_files:
            target.mkdir(parents=True, exist_ok=True)
        for agent_file in agent_files:
            if not _can_replace(target / agent_file.name, owned):
                continue
            shutil.copy2(agent_file, target / agent_file.name)
            installed.append(_read_agent(agent_file))
    return installed


def install_relay_skills(target: Path, owned: set[str]) -> list[str]:
    source = asset('skills')
    if not source.is_dir():
        return []

    installed = []
    with as_file(source) as skills_dir:
        for skill in _skill_dirs(skills_dir):
            if not _can_replace(target / skill.name, owned):
                continue
            _replace_dir(skill, target / skill.name)
            installed.append(skill.name)
    return installed


def remove_installed(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _can_replace(destination: Path, owned: set[str]) -> bool:
    if not destination.exists() or destination.name in owned:
        return True
    console.warn(
        f'{destination} already exists and was not installed by RelayAI; '
        'leaving it untouched (rename it to get the RelayAI version).'
    )
    return False


def _download(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            return response.read()
    except urllib.error.URLError as err:
        raise SetupError(f'could not download {url}') from err


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != '---':
        return {}

    fields = {}
    for line in lines[1:]:
        if line.strip() == '---':
            break
        key, separator, value = line.partition(':')
        if separator and not line.startswith((' ', '\t')):
            fields[key.strip()] = value.strip().strip('\'"')
    return fields


def _read_agent(agent_file: Path) -> Agent:
    fields = _frontmatter(agent_file.read_text(encoding='utf-8'))
    if not fields.get('description'):
        raise SetupError(f'agent {agent_file.name} has no description in its frontmatter')
    name = fields.get('name') or agent_file.name.removesuffix(AGENT_SUFFIX)
    return Agent(description=fields['description'], file_name=agent_file.name, name=name)


def _replace_dir(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _skill_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        raise SetupError(f'skills folder not found: {root}')
    return sorted(path for path in root.iterdir() if (path / SKILL_FILE).is_file())
