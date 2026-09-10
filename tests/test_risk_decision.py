from src.fintech_search import PaymentEvent, assess_risk, notification_for


def test_large_payment_creates_review_notification() -> None:
    event = PaymentEvent(
        event_id="pay_large",
        account_id="acct_1",
        amount_cents=100_000,
        merchant="Video Ads",
        country="US",
    )
    action = assess_risk(event)
    notice = notification_for(event, action)
    assert action.decision == "review"
    assert notice.severity == "high"
    assert notice.event_id == "pay_large"
