[**English**](README.md) · [Русский](README.ru.md)

# The Wisdom Chest · Сундук Мудрости

A fairy-tale bank advisor you can look inside. Pick a character, ask a financial question, and watch a small retrieval-augmented generation (RAG) pipeline decide which fictional products the character is allowed to see, find the relevant ones, and build an answer.

**[Open the live demo](https://fairy-financial-rag-demo.streamlit.app/)** · All characters, products, rates, and advice are fictional.

![The Wisdom Chest welcome screen](docs/screenshots/intro.png)

Streamlit Community Cloud may put the demo to sleep between visits. If it offers to wake the app, the first search can take longer while the embedding model loads.

## Try it in two minutes

1. Click **Начать** (“Start”) and use the demo character profiles.
2. Enter `3333` to play as Ilya Muromets, or `5555` as Yuliy the Horse. Yuliy is 12, so the eligibility filter has opinions about retirement products.
3. Ask, for example, **«Нужен заём на нового коня»** (“I need a loan for a new horse”).
4. Load the demo bank catalogue, then follow the rule filter, product search, prompt, and final answer.

The screens deliberately show the working: rejected products and reasons, the search method and scores, what is stored in Chroma, and the exact prompt sent to the language model. There is no hidden “AI magic” step.

## What happens under the lid

```text
character + question                 fictional product catalogue
          │                                      │
          └──────────────┬───────────────────────┘
                         ▼
           eligibility rules (age, income, citizenship)
                         ▼
           semantic retrieval of up to five products
                         ▼
           grounded prompt with character details
                         ▼
              Groq / gpt-oss-20b answer
                 or marked template fallback
```

- **Rules first.** Ineligible products are removed before retrieval. A second eligibility condition is applied inside Chroma; tests compare it with the Python filter across all demo characters.
- **Search you can inspect.** The default route uses `paraphrase-multilingual-MiniLM-L12-v2` embeddings and an in-memory Chroma collection with cosine similarity. If a component is unavailable, the app tries in-memory embeddings, TF-IDF, then a keyword search.
- **A bounded answer.** The model receives only the selected product descriptions, the question, and the character profile. The prompt is visible in the UI. If Groq is unavailable or no key is configured, the app labels its template answer instead of presenting it as model output.

The catalogue has **11 characters** and **32 products** in `data/`. You can upload your own JSON files; the app validates the entire file before accepting it. The format and required fields are shown beside each upload step.

## Scope and limitations

This is a portfolio demo of a decision pipeline, not a bank or a source of real financial advice. Its catalogue is small and fictional. Chroma lives only in process memory and is rebuilt for a new catalogue or process restart; a production catalogue would need persistent storage. Similarity thresholds were chosen for the sample questions and may need tuning for other data. The model sees short product descriptions and can still miss details.

The new chest illustration is an original storybook character. The playful setting makes the rule filter and retrieval path easier to follow; the actual decisions remain visible at every step.

## Run locally

Python 3.11 is required (`runtime.txt` pins 3.11.9 for Streamlit Cloud).

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-macos.txt  # macOS; use requirements.txt on Linux
streamlit run app.py
```

`requirements.txt` pins a Linux CPU PyTorch wheel for Streamlit Cloud; `requirements-macos.txt` uses the standard macOS wheel with the same dependency versions.

For a generated answer, put a Groq key in `.streamlit/secrets.toml` (ignored by Git):

```toml
GROQ_API_KEY = "your-key"
```

Without a key the full filter and retrieval flow still works; the last screen displays a clearly marked template response.

## Tests and code map

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover JSON validation, eligibility and its Chroma equivalent, retrieval fallbacks, prompt construction, and the Streamlit flow without a live Groq call.

| Path | Purpose |
| --- | --- |
| `app.py`, `screens/` | Streamlit story and seven observable steps |
| `rag/` | Validation, rules, retrieval, vector store, prompt, fallback |
| `data/` | Fictional characters and bank products |
| `assets/` | Original chest illustration and visual theme |
| `tests/` | Pipeline and end-to-end app checks |

## License

MIT — see [LICENSE](LICENSE).
