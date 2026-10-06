# PaperFit: Research Paper Onboarding (Deepfake Detection)

PaperFit is a rule-based reasoning engine built for the Calyb AI Engineering Intern Assignment (Domain B: Research Paper Onboarding).

It ingests deepfake detection papers, structures them into a custom knowledge graph (stored as a single JSON file representing the knowledge state) based on modality and cue families, and evaluates how well each paper fits a **new** project description. 

For a detailed explanation of the reasoning, schema tradeoffs, and limitations (including why I chose a rule-based approach over an LLM and how the MesoNet edge-case was handled), see [approach.md](approach.md).

## Project Structure
- `config/` - Contains `lexicon.json` and `schema.json`, which define the rules and keywords for the engine.
- `src/` - Python source code for fetching, building the knowledge state, and analyzing projects.
- `data/` - Holds raw paper JSONs, full-text extractions, and the labeled dataset for validation.
- `knowledge_state/` - The built graph JSON and visualization output.
- `tests/` - Unit tests verifying specific edge cases in the rule engine.

## Setup

1. **Python Version**: Developed on Python 3.12
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The only external dependency is `pypdf`. API fetching relies strictly on the native Python `urllib`).*

## Usage Pipeline

### 1. Fetch Papers
The primary data source is OpenAlex.
```bash
python src/fetch_openalex.py "deepfake video detection" --limit 50
```
*Note: Alternative fetchers (`src/fetch_papers.py` for Semantic Scholar, `fetch_crossref.py`, and `fetch_arxiv.py`) are included but are heavily throttled. If you use Semantic Scholar, you must set `$env:S2_API_KEY="your_api_key_here"`. No environment variables are needed unless you use the Semantic Scholar fetcher.*

### 2. Fetch Full Text (Optional)
Attempts to download open-access PDFs and extracts text to `data/fulltext/<paperId>.txt` to evaluate "demonstrated" claims.
```bash
python src/fetch_fulltext.py
```
**Important limitation:** Full text was available for only **5 of 49 papers**. The other 44 papers are graded from the abstract alone. Additionally, the full text for our seed paper, MesoNet (`arxiv_1809_00888.txt`), was added manually from arXiv's HTML page, not through this automatic PDF step.

### 3. Build the Knowledge State
Generates the structured Knowledge Graph (`knowledge_state/knowledge_base.json`).
```bash
python src/build_kb.py
```
> **Fast-path for reviewers:** You do not need to run Steps 1 and 2! `data/raw_papers.json` and `data/fulltext/` are committed to the repo. To rebuild the knowledge state from the included data without making any API calls, simply run `python src/build_kb.py`.

**How to read the knowledge state:**
The output is a single JSON file. Papers are stored as nodes, and `COVERS_CUE` and `TARGETS_MODALITY` edges link them to the cue families and modalities they demonstrate or claim. Each edge records whether the feature was `claimed` or `demonstrated`. Each paper's `profile` holds the supporting evidence sentences.

To visualize the graph:
```bash
python src/export_graph.py
```
*(Writes `knowledge_state/graph.html`; open it in a browser.)*

### 4. Analyze a New Project
Provide a new project description to evaluate the papers.
```bash
python src/analyze.py "our project detects deepfakes in videos and images using lipsync"
```
Or pipe it from a file in Windows PowerShell:
```powershell
Get-Content my_project.txt | python src/analyze.py -
```

**Sample Output Snippet:**
```text
MesoNet: a Compact Facial Video Forgery ... (2018) | partially_relevant        | [COVERED] technical_traces [MISSING] sound,cross_frame_movement
  |- Reason: Architecture test: claims video but evidence shows frame-level only (image classifier + aggregation).
  |- Frame-Aggregation Evidence:
       "A natural way of doing so is to average the network prediction over the video."
```

### 5. Validate the Engine
To measure agreement with hand labels, run the validation script against `data/labeled_papers.json`:
```bash
python src/validate.py data/labeled_papers.json
```
*Note: `labeled_papers.json` must be formatted as an array of objects:*
```json
[
  {"paperId": "arxiv_1809_00888", "expected_grade": "partially_relevant"}
]
```

## Run Tests
To run the unit tests (e.g., verifying the MesoNet "average precision" exclusion rule):
```bash
python -m unittest tests/test_rules.py
```
