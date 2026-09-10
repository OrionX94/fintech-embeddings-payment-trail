import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fintech_search import FintechDocumentIndex, PaymentEvent, assess_risk, infrai_embedder, notification_for


def main() -> None:
    event = PaymentEvent(
        event_id="pay_1042",
        account_id="creator_17",
        amount_cents=12500,
        merchant="Studio Supply Co",
        country="US",
    )
    action = assess_risk(event)
    print(notification_for(event, action).model_dump_json())

    index = FintechDocumentIndex(infrai_embedder())
    for document in (
        "Refunds above the account threshold require a human review.",
        "Card payments from supported countries can be approved automatically.",
        "Keep an audit note for every payment decision.",
    ):
        index.add(document)
    for match in index.search("Which payments need manual review?", limit=2):
        print(f"{match.score:.3f} {match.text}")


if __name__ == "__main__":
    main()
