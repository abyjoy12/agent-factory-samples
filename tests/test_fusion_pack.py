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
    def test_flow_listing_is_scoped_to_authenticated_user(self):
        paf = deploy.PAF.__new__(deploy.PAF)
        paf.user_id = 'editor@example.org'
        paf.request = Mock(return_value={'data': {'items': [{'agentId': 'owned'}]}})
        self.assertEqual([{'agentId': 'owned'}], paf.agents())
        paf.request.assert_called_once_with('/v1/users/editor%40example.org/agents')

    def test_state_cannot_be_reused_by_another_account(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'state.json'
            config = {'stateFile': str(path), 'pafUrl': 'https://paf.example.org',
                      'fusionUrl': 'https://fusion.example.org', 'pafCredentialsFile': 'unused'}
            deploy.secure_json(path, {'pafUrl': config['pafUrl'], 'fusionUrl': config['fusionUrl'],
                                      'userId': 'another@example.org', 'agents': {}})
            with patch.object(deploy, 'credentials', return_value=('editor@example.org', 'secret')):
                with self.assertRaisesRegex(deploy.DeploymentError, 'another user'):
                    deploy.state_for(config)

    def test_twenty_distinct_get_only_contracts_and_portable_bindings(self):
        self.assertEqual(20, len(PACK))
        self.assertEqual(20, len({s['slug'] for s in PACK}))
        for spec in PACK:
            with self.subTest(spec=spec['slug']):
                folder = ROOT / 'agents' / ('fusion-' + spec['group']) / spec['slug'].removeprefix('fusion-')
                api = deploy.read_json(folder / 'assets/openapi.json')
                self.assertEqual(deploy.openapi(spec, 'https://fusion.example.invalid'), api)
                path = '/' + spec['resource'].rsplit('/', 1)[1]
                self.assertEqual([path] + (['/inventoryOrganizations'] if spec.get('requiresOrganization') else []), list(api['paths']))
                self.assertEqual('https://fusion.example.invalid' + spec['resource'], api['servers'][0]['url'] + path)
                self.assertRegex('GET_' + path[1:], r'^[a-zA-Z0-9_-]{1,64}$')
                self.assertEqual(['get'], list(api['paths'][path]))
                params = {p['name']: p for p in api['paths'][path]['get']['parameters']}
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

    def test_invoice_action_paths_keep_valid_tool_names_and_original_urls(self):
        folder = ROOT / 'agents/fusion-erp/invoice-review-actions/assets'
        prefix = '/fscmRestApi/resources/11.13.18.05'
        for path in folder.glob('*openapi.json'):
            api = deploy.read_json(path)
            self.assertEqual('https://your-fusion-environment.example.com' + prefix,
                             api['servers'][0]['url'])
            for endpoint in api['paths']:
                with self.subTest(contract=path.name, endpoint=endpoint):
                    resource_name = endpoint[1:].replace('/', '_').replace('{', '').replace('}', '')
                    for method in api['paths'][endpoint]:
                        self.assertRegex(method.upper() + '_' + resource_name,
                                         r'^[a-zA-Z0-9_-]{1,64}$')
                    self.assertTrue(endpoint.startswith('/invoices'))
                    self.assertNotIn(prefix, endpoint)

    def test_missing_model_prevents_probes_and_writes(self):
        paf = Mock()
        paf.request.return_value = {'data': [{'value': 'another-model'}]}
        with patch.object(deploy, 'probe') as probe:
            with self.assertRaisesRegex(deploy.DeploymentError, 'not accessible'):
                deploy.apply({'model': 'required-model'}, PACK, paf, Path('/tmp/unused'), {})
        probe.assert_not_called()
        self.assertEqual([('/v1/agentBuilderGetRegisteredLLMS',)], [c.args for c in paf.request.call_args_list])
        paf.upload.assert_not_called()

    def test_invoice_actions_expose_required_media_headers_and_item_lines(self):
        folder = ROOT / 'agents/fusion-erp/invoice-review-actions/assets'
        actions = deploy.read_json(folder / 'invoice-actions-openapi.json')
        for endpoint, methods in actions['paths'].items():
            operation = methods['post']
            media = ('application/vnd.oracle.adf.action+json' if '/action/' in endpoint
                     else 'application/vnd.oracle.adf.resourceitem+json')
            headers = {p['name']: p for p in operation['parameters'] if p['in'] == 'header'}
            self.assertTrue(headers['Content-Type']['required'])
            self.assertEqual([media], headers['Content-Type']['schema']['enum'])
            self.assertIn(media, operation['requestBody']['content'])
        create = actions['paths']['/invoices']['post']['requestBody']['content']
        schema = create['application/vnd.oracle.adf.resourceitem+json']['schema']
        self.assertIn('invoiceLines', schema['required'])
        line = schema['properties']['invoiceLines']['items']
        self.assertTrue({'LineNumber', 'LineAmount', 'DistributionCombination'} <= set(line['required']))
        reads = deploy.read_json(folder / 'invoice-read-openapi.json')
        self.assertIn('/invoices/{invoicesUniqID}/child/invoiceLines', reads['paths'])

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

    def inventory_connection(self, rows):
        connection = Mock()
        responses = []
        for body in rows:
            response = Mock()
            response.__enter__ = Mock(return_value=io.StringIO(json.dumps(body)))
            response.__enter__.return_value.status = 200
            response.__exit__ = Mock(return_value=False)
            responses.append(response)
        connection.open.side_effect = responses
        return connection

    def test_inventory_discovers_scope_before_bounded_read(self):
        spec = next(s for s in PACK if s.get('requiresOrganization'))
        row = {k: 'sample' for k in spec['fields']}
        connection = self.inventory_connection([{'items': [{'OrganizationId': 321, 'OrganizationCode': 'SAMPLE'}]}, {'items': [row]}])
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
            result = deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, [spec])
        self.assertTrue(result[spec['slug']]['eligible'])
        lookup, onhand = [c.args[0].full_url for c in connection.open.call_args_list]
        self.assertIn('/inventoryOrganizations?', lookup)
        self.assertIn('limit=3', lookup)
        self.assertIn('q=InventoryFlag%3Dtrue', lookup)
        self.assertIn('q=OrganizationId%3D321', onhand)
        self.assertIn('limit=1', onhand)

    def test_inventory_empty_scope_does_not_query_onhand(self):
        spec = next(s for s in PACK if s.get('requiresOrganization'))
        connection = self.inventory_connection([{'items': []}])
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
            result = deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, [spec])
        self.assertFalse(result[spec['slug']]['eligible'])
        self.assertEqual(1, connection.open.call_count)

    def test_configured_inventory_scope_disables_discovery(self):
        spec = copy.deepcopy(next(s for s in PACK if s.get('requiresOrganization')))
        spec['query'] = 'OrganizationId=321'
        self.assertNotIn('/inventoryOrganizations', deploy.openapi(spec, 'https://example.org')['paths'])
        self.assertIn('never broaden', deploy.inventory_scope(spec))
        connection = self.inventory_connection([{'items': []}])
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
            result = deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, [spec])
        self.assertTrue(result[spec['slug']]['eligible'])
        self.assertEqual(1, connection.open.call_count)
        self.assertIn('q=OrganizationId%3D321', connection.open.call_args.args[0].full_url)

    def test_invalid_inventory_scope_stops_before_onhand(self):
        spec = next(s for s in PACK if s.get('requiresOrganization'))
        bodies = [[], {'items': {}}, {'items': ['invalid']},
                  {'items': [{'OrganizationId': True}]},
                  {'items': [{'OrganizationId': '1;OrganizationId=2'}]}]
        for body in bodies:
            with self.subTest(body=body):
                connection = self.inventory_connection([body])
                with patch.object(deploy, 'credentials', return_value=('user', 'secret')), patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
                    result = deploy.probe({'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'unused'}, [spec])
                self.assertFalse(result[spec['slug']]['eligible'])
                self.assertEqual(1, connection.open.call_count)

    def test_auth_failure_does_not_retry_profile_or_block_another_profile(self):
        connection = self.inventory_connection([{'items': []}])
        good = connection.open.side_effect
        connection.open.side_effect = [urllib.error.HTTPError('https://example.org', 401, 'Unauthorized', {}, None), next(good)]
        specs = PACK[:3]
        config = {'fusionUrl': 'https://example.org', 'fusionCredentialsFile': 'default', 'credentialOverrides': {specs[2]['slug']: 'different'}}
        with patch.object(deploy, 'credentials', return_value=('user', 'secret')) as credentials, patch.object(deploy, 'opener', return_value=connection), redirect_stdout(io.StringIO()):
            result = deploy.probe(config, specs)
        self.assertEqual(2, connection.open.call_count)
        self.assertFalse(result[specs[1]['slug']]['eligible'])
        self.assertTrue(result[specs[2]['slug']]['eligible'])
        self.assertEqual(['default', 'different'], [c.args[0] for c in credentials.call_args_list])

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
