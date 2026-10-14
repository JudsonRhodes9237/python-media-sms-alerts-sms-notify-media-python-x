from src.media_alerts import AssetIngested, InfraiSms, ProcessingJob, notify_creator


def main() -> None:
    asset = AssetIngested(
        asset_id="asset-2048",
        creator_phone=os.environ["CREATOR_PHONE"],
        title="Spring storefront reel",
    )
    job = ProcessingJob(asset_id=asset.asset_id, status="completed")
    result = notify_creator(job, asset, InfraiSms())
    print("creator alert sent:", result)


if __name__ == "__main__":
    import os

    main()

