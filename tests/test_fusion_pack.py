import copy
import importlib.util
import io
import json
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('fusion_deploy', ROOT / 'integrations/fusion-apps/deploy.py')
deploy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy)
PACK = deploy.read_json(ROOT / 'integrations/fusion-apps/pack.json')['agents']


class FusionPackTests(unittest.TestCase):
    def test_twenty_distinct_get_only_contracts_and_portable_bindings(self):
        self.assertEqual(20, len(PACK))
        self.assertEqual(20, len({s['slug'] for s in PACK}))
        for spec in PACK:
            with self.subTest(spec=spec['slug']):
                folder = ROOT / 'agents' / ('fusion-' + spec['group']) / spec['slug'].removeprefix('fusion-')
                api = deploy.read_json(folder / 'assets/openapi.json')
                self.assertEqual(deploy.openapi(spec, 'https://fusion.example.invalid'), api)
                self.assertEqual([spec['resource']], list(api['paths']))
                self.assertEqual(['get'], list(api['paths'][spec['resource']]))
                params = {p['name']: p for p in api['paths'][spec['resource']]['get']['parameters']}
                self.assertEqual([10], params['limit']['schema']['enum'])
                self.assertEqual([True], params['onlyData']['schema']['enum'])
                self.assertEqual([','.join(spec['fields'])], params['fields']['schema']['enum'])
                self.assertNotIn('query', spec)
                if spec.get('requiresOrganization'):
                    self.assertTrue(params['q']['required'])
                    self.assertNotIn('default', params['q']['schema'])
                flow = deploy.read_json(folder / 'workflow.json')
                self.assertFalse(flow['published'])
                bindings = [n['data']['template']['src_select']['value'] for n in flow['data']['nodes'] if n['data'].get('type') == 'restAPITools']
                self.assertEqual([''], bindings)

    def test_missing_model_prevents_probes_and_writes(self):
        paf = Mock()
        paf.request.return_value = {'data': [{'value': 'another-model'}]}
        with patch.object(deploy, 'probe') as probe:
            with self.assertRaisesRegex(deploy.DeploymentError, 'not accessible'):
                deploy.apply({'model': 'required-model'}, PACK, paf, Path('/tmp/unused'), {})
        probe.assert_not_called()
        self.assertEqual([('/v1/agentBuilderGetRegisteredLLMS',)], [c.args for c in paf.request.call_args_list])
        paf.upload.assert_not_called()

    def test_failed_resource_preflight_prevents_source_creation(self):
        paf = Mock()
        paf.request.return_value = {'data': [{'value': 'required-model'}]}
        with tempfile.TemporaryDirectory() as temporary:
            state = {'agents': {}}
            with patch.object(deploy, 'probe', return_value={PACK[0]['slug']: {'eligible': False}}):
                with self.assertRaisesRegex(deploy.DeploymentError, 'No PAF writes'):
                    deploy.apply({'model': 'required-model'}, PACK[:1], paf, Path(temporary) / 'state.json', state)
        paf.upload.assert_not_called()
        self.assertEqual(1, paf.request.call_count)

    def test_empty_probe_is_eligible_but_not_projection_verified(self):
        response = Mock()
        response.__enter__ = Mock(return_value=io.StringIO('{"items": []}'))
        response.__enter__.return_value.status = 200
        response.__exit__ = Mock(return_value=False)
        connection = Mock()
        connection.open.return_value = response
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
            result = deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, PACK[:1])
        self.assertTrue(result[PACK[0]['slug']]['eligible'])
        self.assertFalse(result[PACK[0]['slug']]['projectionVerifiedWithRows'])

    def test_authentication_failure_stops_remaining_probes(self):
        connection = Mock()
        connection.open.side_effect = urllib.error.HTTPError('https://example.org', 401, 'Unauthorized', {}, None)
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
            result = deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, PACK[:2])
        self.assertEqual(1, connection.open.call_count)
        self.assertFalse(result[PACK[0]['slug']]['eligible'])

    def test_inventory_requires_approved_scope_before_read(self):
        spec = next(s for s in PACK if s.get('requiresOrganization'))
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener') as op:
            with self.assertRaisesRegex(deploy.DeploymentError, 'approved OrganizationId'):
                deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, [spec])
        op.return_value.open.assert_not_called()

    def test_defaults_reconciliation_cannot_hide_wiring_or_instruction_edits(self):
        desired = {'nodes': [{'id': 'a', 'data': {'type': 'agentStep', 'template': {'llmToUse': {'value': 'required'}, 'custom_instruction': {'value': 'Keep scope'}}}}], 'edges': []}
        saved = {'data': copy.deepcopy(desired)}
        saved['data']['_workflowMetadata'] = {'version': 1}
        saved['data']['nodes'][0]['data']['template']['llmToUse']['value'] = 'default'
        self.assertTrue(deploy.creation_defaults_only(saved, desired))
        saved['data']['nodes'][0]['data']['template']['custom_instruction']['value'] = 'Changed'
        self.assertFalse(deploy.creation_defaults_only(saved, desired))

    def test_incomplete_draft_cannot_be_exported_as_verified(self):
        paf = Mock()
        state = {'agents': {PACK[0]['slug']: {'flowId': 'incomplete'}}}
        with self.assertRaisesRegex(deploy.DeploymentError, 'No verified deployment'):
            deploy.export({}, PACK[:1], paf, state, Path('/tmp/unused'))
        paf.request.assert_not_called()

    def test_private_state_rejects_repository_and_uses_private_permissions(self):
        with self.assertRaises(deploy.DeploymentError):
            deploy.secure_json(ROOT / 'private-test.json', {'secret': 'not written'})
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'state.json'
            deploy.secure_json(path, {'agents': {}})
            self.assertEqual(0o600, path.stat().st_mode & 0o777)
            self.assertEqual({'agents': {}}, json.loads(path.read_text()))


if __name__ == '__main__':
    unittest.main()
