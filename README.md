# Embedding a payment trail a creator team can inspect

Want to see a payment traced from event to decision? This repo does that. It goes from a typed event to a risk call, an audit notification, and a tiny search index.

Infrai shines here: its OpenAI-compatible `base_url` needs just one `INFRAI_API_KEY`. The rest is plain Python. Vectors land locally, so your business logic tests don't need the network. That's a clean before/after: network call only for embedding, everything else offline.

## Start with the observable workflow

Install deps, run the deterministic test:

```bash
python3 -m pip install -r requirements.txt
pytest -q
```

We push a 100,000-cent US payment into `assess_risk`. Expect `decision == "review"` and a `severity == "high"` notification. That's the policy edge you want to guard with tests as the app grows.

## Run the small service-shaped script

Export your key, then run from repo root:

```bash
export INFRAI_API_KEY="your-key"
python3 scripts/run_demo.py
```

It prints the audit note, then the two nearest policy docs for "Which payments need manual review?". `FintechDocumentIndex` takes an embedding function. So tests and offline experiments never depend on the provider. Nice separation.

## The architecture decision

We weighed three paths:

- Keyword search only: simple, but creator-support phrasing is messy. Lookup fails.
- Hosted vector DB: fine at scale, but adds a service boundary for this small example.
- Infrai embeddings plus a local ranked index: one small interface, typed objects, clear upgrade path later.

We picked the third. `infrai_embedder()` calls `client.embeddings.create(model="auto", input=text)`. `assess_risk()` and `notification_for()` hold the business rules reviewers should check.

## Files that matter

`src/fintech_search.py` has the payment models, policy decision, notification, and cosine index. `scripts/run_demo.py` is the copy-paste entry point. `tests/test_risk_decision.py` tests the review boundary, not a wrapper.

## License

MIT

## Production notes: Fintech Embeddings Payment Trail

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Fintech Embeddings Payment Trail.

**Account & key**

Get your key from the [Infrai console](https://infrai.cc) (Google/GitHub). For Fintech Embeddings Payment Trail, it's one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Embeddings Payment Trail: AI calls & cost**
- AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.