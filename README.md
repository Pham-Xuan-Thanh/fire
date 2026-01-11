<p align="center">
  <img src="assets/logo.png" width="120" alt="FIRE Logo"/>
</p>

# 🔥 FIRE: Fact-checking with Iterative Retrieval and Verification

[FIRE](https://github.com/mbzuai-nlp/fire) is a novel agent-based framework for **fact-checking atomic claims**, designed to integrate **evidence retrieval and claim verification** in an **iterative and cost-effective manner**.

<p align="center">
  <img src="assets/arch_fire.png" alt="FIRE Architecture" width="100%"/>
</p>

## 🚀 Features

- **Iterative agent-based reasoning** - Dynamically decides when to search or finalize
- **Multi-LLM Support** - OpenAI, Anthropic, Google Gemini, HuggingFace models
- **Web Search Integration** - Uses Google Serper API for evidence retrieval
- **Streamlit Web App** - Interactive UI for fact-checking claims
- **Multi-language Support** - Responds in the same language as the input claim

## 📦 Installation

```bash
git clone https://github.com/mbzuai-nlp/fire.git
cd fire

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

Edit `common/shared_config.py` with your API keys:

```python
openai_api_key = 'YOUR_OPENAI_API_KEY'
anthropic_api_key = 'YOUR_ANTHROPIC_API_KEY'
google_api_key = 'YOUR_GOOGLE_GEMINI_API_KEY'
serper_api_key = 'YOUR_SERPER_API_KEY'
```

Or set environment variables:
```bash
export GOOGLE_API_KEY='YOUR_GOOGLE_GEMINI_API_KEY'
export SERPER_API_KEY='YOUR_SERPER_API_KEY'
```

## 🌐 Streamlit Web App

Launch the interactive fact-checker:

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

<p align="center">
  <img src="assets/streamlit_demo.png" alt="Streamlit App" width="80%"/>
</p>

**Features:**
- 📝 Enter any claim to verify
- 🔍 Real-time progress tracking
- ✅ TRUE/FALSE verdict with confidence
- 📚 Evidence with clickable source links
- 📊 Token usage and timing statistics
- 🌍 Multi-language support (Vietnamese, English, etc.)

## 💻 Python Usage

```python
from common.modeling import Model
from eval.fire.verify_atomic_claim import verify_atomic_claim

# Initialize with Google Gemini
model = Model(
    model_name='google:gemini-2.5-flash',
    temperature=0.5,
    max_tokens=2048
)

# Verify a claim
result, searches, usage = verify_atomic_claim(
    atomic_claim="Paris is the capital of France",
    rater=model
)

print(f"Answer: {result.answer}")  # True or False
print(f"Searches: {len(searches['google_searches'])}")
```

## 🤖 Supported Models

| Provider | Model Examples |
|----------|----------------|
| Google Gemini | `google:gemini-2.5-flash`, `google:gemini-1.5-pro` |
| OpenAI | `openai:gpt-4o-mini`, `openai:gpt-4o` |
| Anthropic | `anthropic:claude-3-sonnet`, `anthropic:claude-3-opus` |
| HuggingFace | `hf:meta-llama/Llama-3.1-8B-Instruct` |

## 📊 How It Works

```
Input Claim
   │
   ▼
[FIRE Decision Module]
   ├── confident → Output Label (True / False)
   └── uncertain → Generate Search Query
                      │
                      ▼
          Web Search (via SerperAPI)
                      │
                      ▼
            Update Evidence Set
                      │
                      └── Loop until confident or max steps
```

## 📁 Project Structure

```
fire/
├── app.py                    # Streamlit web app
├── common/
│   ├── modeling.py           # LLM abstraction layer
│   ├── shared_config.py      # API keys configuration
│   └── utils.py              # Utility functions
├── eval/
│   └── fire/
│       ├── verify_atomic_claim.py  # Main verification logic
│       ├── query_serper.py         # Google search API
│       └── config.py               # FIRE settings
└── datasets/                 # Benchmark datasets
```

## 📄 Citation

```bibtex
@inproceedings{xie-etal-2025-fire,
 author = {Xie, Zhuohan and Xing, Rui and Wang, Yuxia and Geng, Jiahui and Iqbal, Hasan and Sahnan, Dhruv and Gurevych, Iryna and Nakov, Preslav},
 booktitle = {Findings of the Association for Computational Linguistics: NAACL 2025},
 pages = {2901--2914},
 publisher = {Association for Computational Linguistics},
 title = {{FIRE}: Fact-checking with Iterative Retrieval and Verification},
 url = {https://aclanthology.org/2025.findings-naacl.158/},
 year = {2025}
}
```

## 👥 Authors

Developed by **Zhuohan Xie**, Rui Xing, Yuxia Wang, Jiahui Geng, Hasan Iqbal, Dhruv Sahnan, Iryna Gurevych, and Preslav Nakov  
**Affiliations**: MBZUAI, The University of Melbourne

📬 Contact: **zhuohan.xie@mbzuai.ac.ae**

---

_"Fact-checking, now with FIREpower."_ 🔥
