"""Bundle contract checks using disposable fixtures, never the demonstration datasets."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bundle', Path(__file__).with_name('prepare-connect-bundle.py'))
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)


class BundleChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.old_root = bundle.ROOT
        bundle.ROOT = self.root
        files = {'app/app.py': 'app = None\n', 'app/qc.py': '# unit-test fixture\n',
                 'app/requirements.txt': 'fastapi==0.115.12\nuvicorn==0.34.2\npython-multipart==0.0.20\n',
                 'app/.python-version': '3.12\n', 'app/frontend/dist/index.html': '<html></html>',
                 'app/frontend/dist/assets/main.js': '// fixture', 'data/README.md': 'Unit-test fixtures only',
                 'app/.env': 'NOT_A_REAL_SECRET=excluded',
                 'app/frontend/node_modules/not_for_deployment.py': '# excluded'}
        files.update({'data/' + name: 'build_id,build_date,uts_mpa\n' for name in bundle.DATASETS})
        for name, contents in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents)
        self.destination = Path(self.temp.name) / 'staged'

    def tearDown(self):
        bundle.ROOT = self.old_root
        self.temp.cleanup()

    def manifest(self):
        files = {p.relative_to(self.destination).as_posix():
                 {'checksum': hashlib.md5(p.read_bytes()).hexdigest()}
                 for p in self.destination.rglob('*') if p.is_file()}
        (self.destination / 'manifest.json').write_text(json.dumps({
            'metadata': {'appmode': 'python-fastapi', 'entrypoint': 'app:app'},
            'python': {'version': '3.12.1'}, 'files': files}))

    def test_staged_bundle_preserves_package_data_and_ui_without_env_or_dependencies(self):
        bundle.stage(self.root, self.destination)
        self.assertTrue((self.destination / 'qc.py').exists())
        self.assertTrue((self.destination / 'frontend/dist/assets/main.js').exists())
        self.assertTrue((self.destination / 'data/unstable_shift.csv').exists())
        self.assertTrue((self.destination / 'data/waam_unstable_shift.csv').exists())
        self.assertTrue((self.destination / 'data/ebpbf_unstable_shift.csv').exists())
        self.assertTrue((self.destination / 'data/laser_ded_unstable_shift.csv').exists())
        self.assertTrue((self.destination / 'data/laser_ded_inspection_demo.csv').exists())
        self.assertFalse((self.destination / '.env').exists())
        self.assertFalse((self.destination / 'frontend/node_modules').exists())
        # The manifest fingerprints bytes: Windows must stage the same requirements as CI.
        self.assertNotIn(b'\r', (self.destination / 'requirements.txt').read_bytes())
        self.manifest()
        bundle.verify(self.destination)

    def test_modified_source_rejects_stale_checksum(self):
        bundle.stage(self.root, self.destination)
        self.manifest()
        (self.destination / 'qc.py').write_text('# changed\n')
        with self.assertRaisesRegex(ValueError, 'Stale manifest checksum'):
            bundle.verify(self.destination)

    def test_omitted_asset_rejects_stale_file_list(self):
        bundle.stage(self.root, self.destination)
        self.manifest()
        (self.destination / 'frontend/dist/new.js').write_text('// new')
        with self.assertRaisesRegex(ValueError, 'Stale manifest file list'):
            bundle.verify(self.destination)

    def test_missing_prerequisites_do_not_create_bundle(self):
        (self.root / 'app/app.py').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing prerequisites: app/app.py'):
            bundle.stage(self.root, self.destination)
        self.assertFalse(self.destination.exists())

    def test_unpinned_dependency_fails(self):
        (self.root / 'app/requirements.txt').write_text('fastapi>=0.115\n')
        with self.assertRaisesRegex(ValueError, 'exact package==version'):
            bundle.stage(self.root, self.destination)


if __name__ == '__main__':
    unittest.main()
