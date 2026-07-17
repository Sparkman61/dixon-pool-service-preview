// Public audit source: hash this placeholder-bearing file; the deployed Worker substitutes that SHA-256 and returns it in x-handler-evidence-sha256.
const HANDLER_EVIDENCE_SHA256 = "20b5df799795033f90dce513bdb554f0d41dd8cbb37f1192a9dbd166bee34903";
const ORIGINAL_CONTACT = "https://dixonpoolsmd.com/contact/";
const MAX_BODY_BYTES = 32 * 1024;

function responsePage(status, title, message) {
  const safe = (value) => String(value).replace(/[&<>"']/g, (ch) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  return new Response(`<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${safe(title)} | Dixon Pool Service</title><body><div>📋 This is a free concept redesign — Dixon Pool Service's actual site is at <a href="https://dixonpoolsmd.com/">dixonpoolsmd.com</a></div><main><h1>${safe(title)}</h1><p>${safe(message)}</p><p><a href="/contact">Return to Request Service</a></p></main></body></html>`, {status, headers:{"content-type":"text/html; charset=utf-8","cache-control":"no-store","x-content-type-options":"nosniff","referrer-policy":"no-referrer","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
}

function extract(source, pattern, label) {
  const match = source.match(pattern);
  if (!match) throw new Error(`Original contact form is missing ${label}`);
  return match[1];
}

function field(form, name, max) {
  const value = form.get(name);
  if (value === null) return "";
  const clean = value.trim();
  if (clean.length > max) throw new RangeError(`${name} is too long`);
  return clean;
}

function base64urlEncode(bytes) {
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function base64urlDecode(value) {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - normalized.length % 4) % 4);
  return Uint8Array.from(atob(padded), (character) => character.charCodeAt(0));
}

async function challengeKey(secret) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(secret));
  return crypto.subtle.importKey("raw", digest, "AES-GCM", false, ["encrypt", "decrypt"]);
}

async function encryptChallenge(payload, secret) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await challengeKey(secret);
  const plaintext = new TextEncoder().encode(JSON.stringify(payload));
  const ciphertext = new Uint8Array(await crypto.subtle.encrypt({name:"AES-GCM", iv}, key, plaintext));
  const packed = new Uint8Array(iv.length + ciphertext.length);
  packed.set(iv); packed.set(ciphertext, iv.length);
  return base64urlEncode(packed);
}

async function decryptChallenge(token, secret) {
  const packed = base64urlDecode(token);
  if (packed.length < 29) throw new Error("Invalid challenge token");
  const iv = packed.slice(0, 12);
  const key = await challengeKey(secret);
  const plaintext = await crypto.subtle.decrypt({name:"AES-GCM", iv}, key, packed.slice(12));
  const payload = JSON.parse(new TextDecoder().decode(plaintext));
  if (!payload.nonce || !payload.expires || Date.now() > payload.expires) throw new Error("Expired challenge token");
  return payload;
}

async function issueChallenge(env) {
  if (!env.TURNSTILE_SECRET) return new Response(JSON.stringify({error:"unavailable"}), {status:503, headers:{"content-type":"application/json","cache-control":"no-store","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
  try {
    const page = await fetch(ORIGINAL_CONTACT, {headers:{"user-agent":"Website Rescue contact-form bridge/1.1","accept":"text/html"}});
    if (!page.ok) throw new Error("Original contact form unavailable");
    const source = await page.text();
    const nonce = extract(source, /name="_wpnonce-et-pb-contact-form-submitted-0" value="([^"]+)"/, "security token");
    const captchaTag = extract(source, /(<input[^>]*name="et_pb_contact_captcha_0"[^>]*>)/, "CAPTCHA field");
    const first = extract(captchaTag, /data-first_digit="(\d+)"/, "first CAPTCHA digit");
    const second = extract(captchaTag, /data-second_digit="(\d+)"/, "second CAPTCHA digit");
    const token = await encryptChallenge({nonce, expires:Date.now() + 10 * 60 * 1000}, env.TURNSTILE_SECRET);
    return new Response(JSON.stringify({prompt:`What is ${first} + ${second}?`, token}), {headers:{"content-type":"application/json","cache-control":"no-store","x-content-type-options":"nosniff","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
  } catch (_) {
    return new Response(JSON.stringify({error:"unavailable"}), {status:502, headers:{"content-type":"application/json","cache-control":"no-store","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
  }
}

async function readBoundedBody(request, maxBytes) {
  if (!request.body) return "";
  const reader = request.body.getReader();
  const chunks = [];
  let total = 0;
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    total += value.byteLength;
    if (total > maxBytes) {
      await reader.cancel();
      throw new RangeError("Request body is too large");
    }
    chunks.push(value);
  }
  const body = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.byteLength; }
  return new TextDecoder("utf-8", {fatal:true}).decode(body);
}

async function forwardToOriginal(request, env) {
 try {
  const origin = request.headers.get("origin");
  if (origin !== new URL(request.url).origin) return responsePage(403, "Submission blocked", "Please use the Request Service form on this site.");
  const type = request.headers.get("content-type") || "";
  if (!type.includes("application/x-www-form-urlencoded")) {
    return responsePage(415, "Unsupported submission", "Please use the Request Service form.");
  }
  const raw = await readBoundedBody(request, MAX_BODY_BYTES);
  const form = new URLSearchParams(raw);
  if (field(form, "company_website", 240)) return responsePage(200, "Request received", "Thank you.");
  const values = {
    name: field(form, "name", 120),
    phone: field(form, "phone", 40),
    email: field(form, "email", 254),
    service: field(form, "service", 240),
    message: field(form, "message", 4000),
  };
  if (!values.name || !values.phone || !values.email || !values.message) {
    return responsePage(422, "Please complete the form", "Name, phone number, email address, and message are required.");
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(values.email)) return responsePage(422, "Check your email", "Enter a valid email address.");
  const challengeToken = field(form, "upstream_challenge_token", 4096);
  const userCaptchaAnswer = field(form, "upstream_captcha_answer", 12);
  if (!challengeToken || !/^\d{1,12}$/.test(userCaptchaAnswer)) return responsePage(422, "Verification required", "Answer the service form verification question and try again.");
  let challenge;
  try {
    challenge = await decryptChallenge(challengeToken, env.TURNSTILE_SECRET || "");
  } catch (_) {
    return responsePage(422, "Verification expired", "Reload the Request Service page and answer the new verification question.");
  }
  const turnstile = field(form, "cf-turnstile-response", 4096);
  if (!turnstile || !env.TURNSTILE_SECRET) return responsePage(422, "Verification required", "Complete the anti-spam check and try again.");
  const verifyBody = new URLSearchParams({secret:env.TURNSTILE_SECRET,response:turnstile,remoteip:request.headers.get("CF-Connecting-IP") || ""});
  const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {method:"POST",headers:{"content-type":"application/x-www-form-urlencoded"},body:verifyBody.toString()});
  const verdict = await verify.json();
  if (!verify.ok || verdict.success !== true) return responsePage(422, "Verification failed", "Complete the anti-spam check and try again.");

  const upstream = new URLSearchParams({
    et_pb_contact_name_0: values.name,
    et_pb_contact_phone_number_0: values.phone,
    et_pb_contact_email_0: values.email,
    et_pb_contact_service_0: values.service,
    et_pb_contact_message_0: values.message,
    et_pb_contact_captcha_0: userCaptchaAnswer,
    et_pb_contactform_submit_0: "et_contact_proccess",
    et_builder_submit_button: "Submit",
    "_wpnonce-et-pb-contact-form-submitted-0": challenge.nonce,
    _wp_http_referer: "/contact/",
  });
  const sent = await fetch(ORIGINAL_CONTACT, {method:"POST", headers:{"content-type":"application/x-www-form-urlencoded","user-agent":"Website Rescue contact-form bridge/1.0","referer":ORIGINAL_CONTACT}, body:upstream.toString(), redirect:"follow"});
  if (!sent.ok) return responsePage(502, "Request not sent", "Please call Dixon Pool Service at (301) 607-1011.");
  const result = await sent.text();
  const message = result.match(/<div class="et-pb-contact-message">([\s\S]*?)<\/div>/i);
  const plain = message ? message[1].replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim() : "";
  const formStillPresent = /<form class="et_pb_contact_form\b/i.test(result);
  const confirmed = plain === "Thanks for contacting us";
  if (!confirmed || formStillPresent) return responsePage(502, "Request not confirmed", "Please call Dixon Pool Service at (301) 607-1011.");
  return responsePage(200, "Request sent", "Dixon Pool Service's original contact system accepted your request.");
 } catch (error) {
  const status = error instanceof RangeError ? 413 : 502;
  const title = status === 413 ? "Request too large" : "Service temporarily unavailable";
  return responsePage(status, title, "Please call Dixon Pool Service at (301) 607-1011.");
 }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/api/request-service-challenge") {
      if (request.method !== "GET") return new Response("Method Not Allowed", {status:405, headers:{allow:"GET","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
      return issueChallenge(env);
    }
    if (url.pathname === "/api/request-service") {
      if (request.method !== "POST") return new Response("Method Not Allowed", {status:405, headers:{allow:"POST","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
      return forwardToOriginal(request, env);
    }
    return env.ASSETS.fetch(request);
  }
};
