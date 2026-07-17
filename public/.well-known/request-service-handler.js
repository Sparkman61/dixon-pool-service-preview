// Public audit source: hash this placeholder-bearing file; the deployed Worker substitutes that SHA-256 and returns it in x-handler-evidence-sha256.
const HANDLER_EVIDENCE_SHA256 = "__EVIDENCE_SHA256__";
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
  const turnstile = field(form, "cf-turnstile-response", 4096);
  if (!turnstile || !env.TURNSTILE_SECRET) return responsePage(422, "Verification required", "Complete the anti-spam check and try again.");
  const verifyBody = new URLSearchParams({secret:env.TURNSTILE_SECRET,response:turnstile,remoteip:request.headers.get("CF-Connecting-IP") || ""});
  const verify = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {method:"POST",headers:{"content-type":"application/x-www-form-urlencoded"},body:verifyBody.toString()});
  const verdict = await verify.json();
  if (!verify.ok || verdict.success !== true) return responsePage(422, "Verification failed", "Complete the anti-spam check and try again.");

  const page = await fetch(ORIGINAL_CONTACT, {headers:{"user-agent":"Website Rescue contact-form bridge/1.0","accept":"text/html"}});
  if (!page.ok) return responsePage(502, "Service temporarily unavailable", "Please call Dixon Pool Service at (301) 607-1011.");
  const source = await page.text();
  let nonce, first, second;
  try {
    nonce = extract(source, /name="_wpnonce-et-pb-contact-form-submitted-0" value="([^"]+)"/, "security token");
    const captchaTag = extract(source, /(<input[^>]*name="et_pb_contact_captcha_0"[^>]*>)/, "CAPTCHA field");
    first = Number(extract(captchaTag, /data-first_digit="(\d+)"/, "first CAPTCHA digit"));
    second = Number(extract(captchaTag, /data-second_digit="(\d+)"/, "second CAPTCHA digit"));
  } catch (_) {
    return responsePage(502, "Service temporarily unavailable", "Please call Dixon Pool Service at (301) 607-1011.");
  }
  const upstream = new URLSearchParams({
    et_pb_contact_name_0: values.name,
    et_pb_contact_phone_number_0: values.phone,
    et_pb_contact_email_0: values.email,
    et_pb_contact_service_0: values.service,
    et_pb_contact_message_0: values.message,
    et_pb_contact_captcha_0: String(first + second),
    et_pb_contactform_submit_0: "et_contact_proccess",
    et_builder_submit_button: "Submit",
    "_wpnonce-et-pb-contact-form-submitted-0": nonce,
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
    if (url.pathname === "/api/request-service") {
      if (request.method !== "POST") return new Response("Method Not Allowed", {status:405, headers:{allow:"POST","x-handler-evidence-sha256":HANDLER_EVIDENCE_SHA256}});
      return forwardToOriginal(request, env);
    }
    return env.ASSETS.fetch(request);
  }
};
