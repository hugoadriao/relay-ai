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

import yaml

from relay_ai import console
from relay_ai.errors import SetupError
from relay_ai.platforms import COPILOT, Platform

MATTPOCOCK_CATEGORIES = ('engineering', 'productivity')
MATTPOCOCK_REF = 'main'
MATTPOCOCK_ZIP_URL = (
    f'https://codeload.github.com/mattpocock/skills/zip/refs/heads/{MATTPOCOCK_REF}'
)
SKILL_FILE = 'SKILL.md'


@dataclass(frozen=True)
class Agent:
    description: str
    name: str
    path: Path


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


def install_relay_agents(project: Path, platform: Platform, owned: set[str]) -> list[Agent]:
    source = asset('agents')
    if not source.is_dir():
        return []

    installed = []
    with as_file(source) as agents_dir:
        for agent_file in sorted(agents_dir.glob('*.md')):
            agent = _read_agent(agent_file, platform)
            destination = project / agent.path
            if not _can_replace(destination, owned):
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(_render_agent(agent_file, platform), encoding='utf-8')
            installed.append(agent)
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


def remove_if_empty(directory: Path) -> None:
    if directory.is_dir() and not any(directory.iterdir()):
        directory.rmdir()


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


def _read_agent(agent_file: Path, platform: Platform) -> Agent:
    frontmatter, _ = _split_frontmatter(agent_file)
    if not frontmatter.get('name') or not frontmatter.get('description'):
        raise SetupError(f'agent {agent_file.name} needs a name and a description')
    path = platform.agents_dir / f'{frontmatter["name"]}{platform.agent_suffix}'
    return Agent(description=frontmatter['description'], name=frontmatter['name'], path=path)


def _render_agent(agent_file: Path, platform: Platform) -> str:
    frontmatter, body = _split_frontmatter(agent_file)
    common = {'description': frontmatter['description']}
    if platform is COPILOT:
        common = {'name': frontmatter['name'], **common}
    rendered = {**common, **frontmatter.get(platform.name, {})}
    header = yaml.safe_dump(rendered, allow_unicode=True, sort_keys=False, width=10_000)
    return f'---\n{header}---\n{body}'


def _replace_dir(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def _skill_dirs(root: Path) -> list[Path]:
    if not root.is_dir():
        raise SetupError(f'skills folder not found: {root}')
    return sorted(path for path in root.iterdir() if (path / SKILL_FILE).is_file())


def _split_frontmatter(agent_file: Path) -> tuple[dict, str]:
    text = agent_file.read_text(encoding='utf-8').replace('\r\n', '\n')
    _, header, body = text.split('---\n', 2)
    return yaml.safe_load(header), body
