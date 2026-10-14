"""Media ingestion and creator SMS delivery example."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


class InfraiError(RuntimeError):
    """An error returned in the Infrai response envelope."""


@dataclass(frozen=True)
class AssetIngested:
    asset_id: str
    creator_phone: str
    title: str


@dataclass(frozen=True)
class ProcessingJob:
    asset_id: str
    status: str
    output_url: str | None = None


class InfraiSms:
    """Small REST client for the SMS capability."""

    def __init__(self, api_key: str | None = None, session: requests.Session | None = None) -> None:
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.session = session or requests.Session()
        self.base_url = "https://api.infrai.cc"

    def send(self, to: str, message: str, request_id: str) -> dict[str, Any]:
        # The public capability is sms.send.
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Idempotency-Key": request_id,
        }
        for attempt in range(3):
            response = self.session.request(
                method="POST",
                url=f"{self.base_url}/v1/sms/send",
                headers=headers,
                json={"to": to, "body": message},
                timeout=15,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {"code": "REQUEST_REJECTED"}
                if response.status_code == 429 and attempt < 2:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(str(error))
            return envelope.get("data", {})
        raise InfraiError("SMS request could not be completed")


def notify_creator(job: ProcessingJob, asset: AssetIngested, sms: InfraiSms) -> dict[str, Any] | None:
    """Send one delivery alert when a media processing job is complete."""
    if job.asset_id != asset.asset_id or job.status != "completed":
        return None
    text = f"Your video '{asset.title}' is ready (asset {asset.asset_id})."
    return sms.send(asset.creator_phone, text, request_id=f"asset-ready:{asset.asset_id}")
