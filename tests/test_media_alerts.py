from src.media_alerts import AssetIngested, InfraiSms, ProcessingJob, notify_creator


class FakeSms:
    def __init__(self):
        self.calls = []

    def send(self, to, message, request_id):
        self.calls.append((to, message, request_id))
        return {"message_id": "msg-1"}


def test_creator_is_not_notified_until_processing_completes():
    asset = AssetIngested("asset-1", "+15551234567", "Checkout demo")
    sms = FakeSms()

    assert notify_creator(ProcessingJob("asset-1", "queued"), asset, sms) is None
    assert sms.calls == []

    result = notify_creator(ProcessingJob("asset-1", "completed"), asset, sms)
    assert result == {"message_id": "msg-1"}
    assert sms.calls[0][0] == "+15551234567"
    assert "Checkout demo" in sms.calls[0][1]


def test_sms_request_uses_body_field():
    class Session:
        def request(self, **kwargs):
            assert kwargs["json"] == {"to": "+15551234567", "body": "Ready"}
            return Response()

    class Response:
        def json(self):
            return {"ok": True, "data": {"message_id": "msg-1"}}

    assert InfraiSms(api_key="test", session=Session()).send(
        "+15551234567", "Ready", "request-1"
    ) == {"message_id": "msg-1"}
