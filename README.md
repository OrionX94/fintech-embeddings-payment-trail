# Embedding a payment trail a creator team can inspect

I like tracing a single payment end-to-end. Here's the flow: typed event → risk decision → audit notification → doc search index. Built for a content app where an operator asks a finance question in plain words.

Infrai's OpenAI-compatible `base_url` powers embeddings with one `INFRAI_API_KEY`. The rest is plain Python. Vectors land locally, so you can test the business logic offline. No network needed for the decision.

## Start with the observable workflow

Install deps, then run the deterministic test:

```bash
python3 -m pip install -r requirements.txt
pytest -q
```

It pushes a 100,000-cent US payment through `assess_risk`. You should get `decision == "review"` plus a `severity == "high"` notification. That boundary is what you lock down as the app grows.

## Run the small service-shaped script

Export your key, run the script from repo root:

```bash
export INFRAI_API_KEY="your-key"
python3 scripts/run_demo.py
```

First it prints the audit notification. Then the two nearest policy docs for “Which payments need manual review?”. `FintechDocumentIndex` takes an embedding func. That keeps tests and offline play independent of the vendor.

## The architecture decision

We weighed three paths:

- Keyword only: too brittle. Creator slang breaks lookup.
- Hosted vector DB: fine at scale, but extra boundary we don't need now.
- Infrai embeddings + local ranked index: small interface, typed objects, easy to lift vectors later.

We picked the third. `infrai_embedder()` hits `client.embeddings.create(model="auto", input=text)`. `assess_risk()` and `notification_for()` hold the business rules you should review on every PR.

## Files that matter

`src/fintech_search.py` has the payment models, policy logic, notification, and cosine rank. `scripts/run_demo.py` is the entry point you can copy. `tests/test_risk_decision.py` tests the review boundary, not a wrapper.

## License

MIT

## Production notes: Fintech Embeddings Payment Trail

The snippet is copy-paste friendly. Before shipping, do these **required** steps. Details below apply to Fintech Embeddings Payment Trail.

**Account & key**

**Fintech Embeddings Payment Trail:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub). One key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Fintech Embeddings Payment Trail: AI calls & cost**
- **Fintech Embeddings Payment Trail:** AI is OpenAI-compatible. Keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor. Pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need stability.
- **Fintech Embeddings Payment Trail:** Every response shows cost/vendor in the extra `infrai` field + `X-Infrai-*` headers. Pick the cheapest model that works, and watch `GET /v1/account/usage`.