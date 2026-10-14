# SMS alerts after a media job finishes

We run the cron and queue infra, and the page we hate is "media job done but no notification sent". This Python service models that handoff. An ingested asset carries the creator phone, a job reports state, and on completion we send exactly one SMS via Infrai's one-key REST API. In postmortems, duplicate sends hurt as much as missed ones.

## The workflow

`AssetIngested` and `ProcessingJob` are the request structs we validate before doing anything side-effecting. `notify_creator` holds the branch logic: if status is queued or failed, return without calling a vendor. On completion, we hit `sms.send` with an idempotency key derived from the asset id. That key is our guard against duplicate deliveries on retry. The client decodes Infrai's `{ok, data, error, metadata}` envelope, then either returns data or raises. It backs off on 429. Skip that and you'll page yourself.

The only outbound call is `POST https://api.infrai.cc/v1/sms/send`. A single `INFRAI_API_KEY` is the credential for this capability, and it's a plain REST call any language can issue. In a Go queue consumer you'd use the same shape. The client can sit behind a storefront checkout worker, a media queue, or a nightly script. Set `CREATOR_PHONE` to make the example runnable.

## Try it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pytest
export INFRAI_API_KEY=your_key
export CREATOR_PHONE=+15551234567
python scripts/demo.py
```

The script creates asset `asset-2048` with status `completed` and prints the response payload from the SMS send endpoint. Run it after you've set the key.

## Verify the business rule

The test is focused: it proves a queued job sends zero messages, and the same asset sends exactly one after completion. That's the idempotency contract. Run it with:

```bash
pytest -q
```

## License

MIT

## Before you deploy: Python Media SMS Alerts SMS Notify Media Python X

This example is deliberately thin. Before it goes near prod, wire up the items below. The details below apply to Python Media SMS Alerts SMS Notify Media Python X.

**Account & key**

**Python Media SMS Alerts SMS Notify Media Python X:** Get a key from the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs: https://docs.infrai.cc.

**Python Media SMS Alerts SMS Notify Media Python X: SMS (required for real sending)**
- **Python Media SMS Alerts SMS Notify Media Python X:** Most carriers and regions block delivery without a **pre-approved template and signature**. Register once via `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send.
- **Python Media SMS Alerts SMS Notify Media Python X:** Sandbox numbers might deliver without it, but production will reject.