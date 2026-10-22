# AMR-GUARD X Ω
### Explainable antimicrobial resistance intelligence — hackathon MVP

AMR-GUARD X Ω is a research/educational prototype that demonstrates transparent, reference-based interpretation of selected antimicrobial resistance marker names. It includes an interactive Streamlit dashboard, marker reference lookup, unresolved-marker reporting, separate handling of user-supplied AST notes, and downloadable Markdown/CSV reports.

> **Safety and scientific integrity:** This MVP does not analyze raw DNA sequences, run a trained resistance classifier, estimate calibrated resistance probabilities, or recommend treatment. The included surveillance records are synthetic placeholders. It is not a clinical diagnostic tool.

## Features
- Dark, responsive Streamlit interface
- Input of isolate ID, organism, context, and marker names
- Small local reference catalogue with linked external resources
- Explicit unresolved-marker reporting
- AST observations displayed separately from genomic interpretation
- Downloadable Markdown report and CSV findings
- Synthetic surveillance demo with clear labeling
- Methods, limitations, and validation plan page

## Run locally
Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`).

## Deploy to Streamlit Community Cloud
1. Push this folder to a GitHub repository.
2. Sign in to Streamlit Community Cloud and connect GitHub.
3. Select the repository, branch, and `app.py` as the main file.
4. Deploy, then open the public URL in a private/incognito browser window to test access.

## Suggested GitHub repository description
`Explainable AMR research prototype combining resistance-marker reference interpretation, evidence links, uncertainty flags, and One Health demo visualization.`

## Architecture
- `app.py`: UI and user workflow
- `amr_engine.py`: local reference lookup and report generation
- `data/`: reserved for versioned, licensed, curated datasets
- `tests/`: basic automated tests
- `requirements.txt`: Python dependencies

## Validation roadmap
1. Version the marker catalogue and cite the exact release/date for each source.
2. Add sequence-level analysis only through validated tools and documented input formats.
3. For phenotype prediction, use suitable labelled isolate data, leakage-resistant train/test separation, and external validation where possible.
4. Report per-class precision, recall, F1, sensitivity/specificity, AUROC and calibration where appropriate.
5. Review organism, drug, geography, and time coverage; document missingness and class imbalance.
6. Obtain domain-expert review before any operational use.

## External resources
- NCBI AMRFinderPlus: https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/
- CARD: https://card.mcmaster.ca/
- NCBI Pathogen Detection: https://www.ncbi.nlm.nih.gov/pathogens/
- WHO antimicrobial resistance: https://www.who.int/health-topics/antimicrobial-resistance

## License
MIT for the original code in this repository. External databases, names, and linked resources remain subject to their respective licenses and terms.
