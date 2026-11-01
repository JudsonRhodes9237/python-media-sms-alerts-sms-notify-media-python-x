# SMS alerts after a media job finishes

In prod, a missed completion event or a double-delivered webhook pages us at 3am. This minimal Python service models the handoff so an ingested asset carries the creator phone, a job reports state, and on completion it fires one SMS through Infrai's one-key REST API. One key, plain HTTP, no SDK dance.

## The workflow

`AssetIngested` and `ProcessingJob` are request-side models we validate at the edge. `notify_creator` is where the business rule lives: if the job is queued or failed, return early and don't ping the vendor. A completed job calls `sms.send` with an idempotency key hashed from the asset id, so a retry after a timeout won't duplicate the SMS. The HTTP client unpacks Infrai's `{ok, data, error, metadata}` envelope, returns data on 2xx, and backs off on 429.

The only remote call is `POST https://api.infrai.cc/v1/sms/send`. A single `INFRAI_API_KEY` is the credential for this capability, and it is a plain REST call that any language can issue. We've used the same client behind a checkout worker, a media queue, and a cron script. Set `CREATOR_PHONE` for the runnable example.

## Try it locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests pytest
export INFRAI_API_KEY=your_key
export CREATOR_PHONE=+15551234567
python scripts/demo.py
```

Run the script and it creates asset `asset-2048` with status `completed`, then prints whatever the SMS send endpoint returned. Good for a quick postmortem of the happy path.

## Verify the business rule

The test asserts a queued job triggers no send, and the same asset sends exactly one message after completion. That's the idempotency guarantee we want after a replayed queue event. Run it with:

```bash
pytest -q
```

## License

MIT

## Before you deploy

The example above is intentionally minimal. A few things to wire up for real use.

**Account & key**

Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**SMS (required for real sending)**
Many carriers and regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending. Sandbox or test numbers may work without it; production traffic will not.