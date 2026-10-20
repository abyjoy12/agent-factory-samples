const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');

// Execute the actual inline policy with GitHub API fixtures, without a token.
const workflow = fs.readFileSync(
  path.join(__dirname, '../.github/workflows/contribution-origin.yml'), 'utf8',
);
const script = workflow.split('          script: |\n')[1]
  .split('\n').map(line => line.slice(12)).join('\n');
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const evaluate = new AsyncFunction('github', 'context', 'core', script);

async function runPolicy({ fork = false, permission = 'none', missingRepo = false, apiError = false, manual = false } = {}) {
  const statuses = [];
  const failures = [];
  const permissionRequests = [];
  const context = {
    repo: { owner: 'maintainer', repo: 'samples' },
    serverUrl: 'https://github.com',
    runId: 42,
    payload: {
      pull_request: {
        head: { repo: missingRepo ? null : { id: fork ? 2 : 1 }, sha: 'pr-head-commit' },
        base: { repo: { id: 1 }, sha: 'base-commit' },
        user: { login: 'contributor' },
      },
    },
  };
  const pr = context.payload.pull_request;
  if (manual) context.payload = { inputs: { pull_request_number: '7' } };
  const github = { rest: { pulls: {
    async get(request) {
      assert.equal(request.pull_number, 7);
      return { data: pr };
    },
  }, repos: {
    async getCollaboratorPermissionLevel(request) {
      permissionRequests.push(request);
      if (apiError) throw new Error('Permission API unavailable');
      return { data: { permission } };
    },
    async createCommitStatus(status) { statuses.push(status); },
  } } };
  await evaluate(github, context, {
    error() {},
    setFailed(message) { failures.push(message); },
  });
  assert.equal(statuses.length, 1);
  assert.equal(statuses[0].sha, 'pr-head-commit');
  assert.equal(statuses[0].context, 'fork-origin');
  return { status: statuses[0], failures, permissionRequests };
}

test('fork contributions pass without requiring upstream access', async () => {
  const result = await runPolicy({ fork: true });
  assert.equal(result.status.state, 'success');
  assert.deepEqual(result.failures, []);
  assert.deepEqual(result.permissionRequests, []);
});

test('administrator upstream PRs pass without another maintainer', async () => {
  const result = await runPolicy({ permission: 'admin' });
  assert.equal(result.status.state, 'success');
  assert.deepEqual(result.failures, []);
  assert.equal(result.permissionRequests[0].username, 'contributor');
});

for (const permission of ['maintain', 'write', 'read', 'none']) {
  test(`${permission} contributors cannot submit upstream branch PRs`, async () => {
    const result = await runPolicy({ permission });
    assert.equal(result.status.state, 'failure');
    assert.equal(result.failures.length, 1);
  });
}

test('deleted source repositories fail closed', async () => {
  const result = await runPolicy({ missingRepo: true });
  assert.equal(result.status.state, 'failure');
  assert.equal(result.failures.length, 1);
  assert.deepEqual(result.permissionRequests, []);
});

test('permission lookup errors cannot approve an upstream contribution', async () => {
  const result = await runPolicy({ apiError: true });
  assert.equal(result.status.state, 'error');
  assert.equal(result.failures.length, 1);
});

test('manual rechecks fetch the current PR and preserve the administrator exemption', async () => {
  const result = await runPolicy({ manual: true, permission: 'admin' });
  assert.equal(result.status.state, 'success');
  assert.deepEqual(result.failures, []);
});

test('manual rechecks still reject upstream contributor branches', async () => {
  const result = await runPolicy({ manual: true, permission: 'write' });
  assert.equal(result.status.state, 'failure');
  assert.equal(result.failures.length, 1);
});
