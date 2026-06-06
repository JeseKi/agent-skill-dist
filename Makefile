.PHONY: check lint typecheck test build verify-wheel

check: lint typecheck test build verify-wheel

lint:
	uv run ruff check .

typecheck:
	uv run mypy

test:
	uv run pytest

build:
	uv build

verify-wheel:
	uv run python -c "from pathlib import Path; import zipfile; wheels = sorted(Path('dist').glob('agent_skill_dist-*.whl')); assert wheels, '未找到 wheel'; names = zipfile.ZipFile(wheels[-1]).namelist(); assert 'agent_skill_dist/py.typed' in names, 'wheel 缺少 agent_skill_dist/py.typed'"
