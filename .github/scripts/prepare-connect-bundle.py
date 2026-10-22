"""Stage only app source, built UI, and synthetic demo data; verify a local manifest.

Run --write-manifest on a developer machine. CI stages and checks, never writes.
The bundle keeps the completed H-04 flat app layout and its local imports.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
DATASETS = ('stable_capable.csv', 'stable_incapable.csv', 'unstable_shift.csv')


def pinned_requirements(path, seen=None):
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return []
    seen.add(path)
    if not path.is_relative_to((ROOT / 'app').resolve()):
        raise ValueError('Requirements includes must remain inside app/')
    lines = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('-r '):
            lines.extend(pinned_requirements(path.parent / line[3:].strip(), seen))
        elif re.fullmatch(r'[A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?==[A-Za-z0-9_.+!-]+', line):
            lines.append(line)
        else:
            raise ValueError(f'Use exact package==version requirements: {path.name}')
    return lines


def copy_file(source, target):
    if source.is_symlink() or not source.is_file():
        raise ValueError('Bundle inputs must be regular files, not symbolic links')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)


def stage(root, destination):
    if destination.exists():
        raise ValueError('Bundle destination must not exist; use a fresh temporary path')
    required = ['app/app.py', 'app/qc.py', 'app/requirements.txt', 'app/.python-version',
                'app/frontend/dist/index.html', 'data/README.md']
    required += ['data/' + name for name in DATASETS]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise ValueError('Missing prerequisites: ' + ', '.join(missing) +
                         '. Bring in H-02/H-04 and run the frontend build first.')
    requirements = pinned_requirements(root / 'app/requirements.txt')
    extra = root / 'app/requirements-api.txt'
    if extra.exists():
        requirements.extend(pinned_requirements(extra))
    packages = {line.split('==')[0].lower().replace('_', '-') for line in requirements}
    if not {'fastapi', 'uvicorn', 'python-multipart'}.issubset(packages):
        raise ValueError('H-04 requirements must pin fastapi, uvicorn and python-multipart')
    destination.mkdir(parents=True)
    for source in sorted((root / 'app').rglob('*.py')):
        relative = source.relative_to(root / 'app')
        if any(p in {'node_modules', 'dist', '__pycache__', '.connect-bundle', '.venv'} or p.startswith('.') for p in relative.parts):
            continue
        if source.name.startswith('test'):
            continue
        copy_file(source, destination / relative)
    for source in sorted((root / 'app/frontend/dist').rglob('*')):
        if source.is_file():
            copy_file(source, destination / 'frontend/dist' / source.relative_to(root / 'app/frontend/dist'))
    for name in (*DATASETS, 'README.md'):
        copy_file(root / 'data' / name, destination / 'data' / name)
    copy_file(root / 'app/.python-version', destination / '.python-version')
    # newline='\n': on Windows, write_text would otherwise write CRLF and break the checksum.
    (destination / 'requirements.txt').write_text('\n'.join(dict.fromkeys(requirements)) + '\n', encoding='utf-8', newline='\n')


def verify(destination):
    manifest = json.loads((destination / 'manifest.json').read_text())
    metadata = manifest.get('metadata', {})
    if metadata.get('appmode') != 'python-fastapi' or metadata.get('entrypoint') != 'app:app':
        raise ValueError('Manifest must use python-fastapi and entrypoint app:app')
    wanted = (destination / '.python-version').read_text().strip()
    version = str(manifest.get('python', {}).get('version', ''))
    if version != wanted and not version.startswith(wanted + '.'):
        raise ValueError('Manifest Python version differs from app/.python-version')
    files = manifest.get('files', {})
    actual = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()}
    # Some rsconnect versions include a manifest self-entry without a checksum.
    listed = set(files) - {'manifest.json'}
    if listed != actual - {'manifest.json'}:
        raise ValueError('Stale manifest file list; regenerate locally after source/data/UI changes')
    for name, details in files.items():
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Unsafe path in manifest')
        if name == 'manifest.json':
            continue
        checksum = hashlib.md5((destination / relative).read_bytes()).hexdigest()
        if details.get('checksum') != checksum:
            raise ValueError(f'Stale manifest checksum: {name}; regenerate locally')
    print(f'PASS: manifest verifies {len(listed)} files; python-fastapi; app:app; Python {wanted}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--write-manifest', action='store_true')
    args = parser.parse_args()
    try:
        if args.write_manifest and __import__('os').environ.get('CI'):
            raise ValueError('Manifest generation is local-only; CI must verify the committed manifest')
        destination = args.output.resolve()
        stage(ROOT, destination)
        if args.write_manifest:
            executable = shutil.which('rsconnect', path=str(Path(sys.executable).parent))
            if not executable:
                raise ValueError('Install rsconnect-python in the selected Python environment first')
            subprocess.run([executable, 'write-manifest', 'fastapi',
                            '--entrypoint', 'app:app', str(destination)], check=True)
        else:
            copy_file(ROOT / 'app/manifest.json', destination / 'manifest.json')
        verify(destination)
        if args.write_manifest:
            copy_file(destination / 'manifest.json', ROOT / 'app/manifest.json')
        print('PASS: deployment bundle prepared')
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
