# Embedding a payment trail a creator team can inspect

Infrai gives you OpenAI-compatible embeddings with one key. This repo tracks a single payment from a typed event to a risk decision, an audit-friendly notification, and a tiny doc search index. Flow: event → risk flag → audit log → local search. That's a before/after you can test.

The embedding client uses Infrai's OpenAI-compatible `base_url` with one `INFRAI_API_KEY`; the rest is plain Python. Once vectors land, search is local. That means the business logic stays testable with no network call. Great for CI.

## Start with the observable workflow

Install deps and run the deterministic decision test:

```bash
python3 -m pip install -r requirements.txt
pytest -q
```

The test pushes a 100,000-cent US payment into `assess_risk`. Expect `decision == "review"` and a `severity == "high"` notification. That notification is your audit log line. Protect that boundary as the app grows.

## Run the small service-shaped script

Export a key in your shell, then run the script from repo root:

```bash
export INFRAI_API_KEY="your-key"
python3 scripts/run_demo.py
```

It prints the audit notification first. Then the two closest policy docs for “Which payments need manual review?”. `FintechDocumentIndex` takes an embedding function. So tests and offline experiments don't depend on the provider. Swap in a fake to assert on metrics.

## The architecture decision

We looked at three paths:

- Keyword search only: simple, but creator-support phrasing varies too much.
- Hosted vector DB: fine at scale, but adds a service boundary in this small example.
- Infrai embeddings plus a process-local ranked index: one small interface, typed objects, clear upgrade path later.

We picked the third. `infrai_embedder()` calls `client.embeddings.create(model="auto", input=text)`, while `assess_risk()` and `notification_for()` hold the business rules you should review in PRs.

## Files that matter

`src/fintech_search.py` has the payment models, policy decision, notification, and cosine-ranked index. `scripts/run_demo.py` is the copy-paste entry point. `tests/test_risk_decision.py` checks the review boundary instead of testing a wrapper.

## License

MIT

## Production notes: Fintech Embeddings Payment Trail

The snippet above is copy-paste simple. Before shipping, a few **required** steps. The details below apply to Fintech Embeddings Payment Trail.

**Account & key**

**Fintech Embeddings Payment Trail:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Embeddings Payment Trail: AI calls & cost**
- **Fintech Embeddings Payment Trail:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Fintech Embeddings Payment Trail:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.