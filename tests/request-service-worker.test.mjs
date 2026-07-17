import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const workerPath = new URL('../public/_worker.js', import.meta.url);
const workerSource = await readFile(workerPath, 'utf8');
const workerModule = await import(`data:text/javascript;base64,${Buffer.from(workerSource).toString('base64')}`);
const worker = workerModule.default;

const originalFetch = globalThis.fetch;

test.afterEach(() => {
  globalThis.fetch = originalFetch;
});

test('application source never calculates or manufactures an upstream CAPTCHA answer', () => {
  const forbidden = [
    /String\s*\(\s*first\s*\+\s*second\s*\)/,
    /Number\s*\([^)]*first_digit/,
    /(?:captcha|answer)\w*\s*=\s*[^;\n]*\+[^;\n]*/i,
    /encryptChallenge\s*\(\s*\{[^}]*\bfirst\b[^}]*\bsecond\b/,
  ];

  for (const pattern of forbidden) {
    assert.doesNotMatch(workerSource, pattern);
  }
  assert.match(workerSource, /const userCaptchaAnswer = field\(form, "upstream_captcha_answer", 12\);/);
  assert.match(workerSource, /et_pb_contact_captcha_0: userCaptchaAnswer/);
});

test('mocked authorized flow forwards only the user-entered CAPTCHA answer', async () => {
  const fetchCalls = [];
  globalThis.fetch = async (input, init = {}) => {
    const url = typeof input === 'string' ? input : input.url;
    fetchCalls.push({ url, init });

    if (url === 'https://dixonpoolsmd.com/contact/' && !init.method) {
      return new Response(
        '<input name="_wpnonce-et-pb-contact-form-submitted-0" value="mock-nonce">' +
        '<input name="et_pb_contact_captcha_0" data-first_digit="3" data-second_digit="4">',
        { status: 200 },
      );
    }
    if (url === 'https://challenges.cloudflare.com/turnstile/v0/siteverify') {
      return Response.json({ success: true });
    }
    if (url === 'https://dixonpoolsmd.com/contact/' && init.method === 'POST') {
      const forwarded = new URLSearchParams(init.body);
      assert.equal(forwarded.get('et_pb_contact_captcha_0'), '7');
      assert.equal(forwarded.get('_wpnonce-et-pb-contact-form-submitted-0'), 'mock-nonce');
      return new Response('<div class="et-pb-contact-message">Thanks for contacting us</div>', { status: 200 });
    }
    throw new Error(`Unexpected network request in mocked test: ${url}`);
  };

  const env = { TURNSTILE_SECRET: 'test-only-secret' };
  const challengeResponse = await worker.fetch(
    new Request('https://preview.test/api/request-service-challenge'),
    env,
  );
  assert.equal(challengeResponse.status, 200);
  const challenge = await challengeResponse.json();
  assert.equal(challenge.prompt, 'What is 3 + 4?');
  assert.ok(challenge.token);

  const body = new URLSearchParams({
    name: 'Test Person',
    phone: '555-0100',
    email: 'test@example.invalid',
    service: 'Mock service',
    message: 'This is a deterministic mock and must not leave the test process.',
    upstream_challenge_token: challenge.token,
    upstream_captcha_answer: '7',
    'cf-turnstile-response': 'mock-valid-token',
  });
  const submissionResponse = await worker.fetch(
    new Request('https://preview.test/api/request-service', {
      method: 'POST',
      headers: {
        origin: 'https://preview.test',
        'content-type': 'application/x-www-form-urlencoded',
      },
      body,
    }),
    env,
  );

  assert.equal(submissionResponse.status, 200);
  assert.match(await submissionResponse.text(), /<h1>Request sent<\/h1>/);
  assert.equal(fetchCalls.filter(({ url, init }) => url === 'https://dixonpoolsmd.com/contact/' && init.method === 'POST').length, 1);
});
