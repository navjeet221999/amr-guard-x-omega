import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from io import StringIO

from amr_engine import analyze_gene_list, build_report, DEMO_ISOLATES, RESOURCE_LINKS

st.set_page_config(
    page_title="AMR-GUARD X Ω | Resistance Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { --ink:#e8eef8; --muted:#9eacc2; --panel:#111b2b; --line:#26364c; --cyan:#4ed9e2; }
.stApp { background: radial-gradient(ellipse at top left, #172b42 0%, #0b1220 48%, #080d17 100%); color: var(--ink); }
[data-testid="stSidebar"] { background:#0d1726; border-right:1px solid #26364c; }
h1,h2,h3 { color:#f5f8ff !important; letter-spacing:-.025em; }
p, label, .stMarkdown { color:#d4deec; }
.hero { padding:1.4rem 1.6rem; border:1px solid #2b435a; border-radius:20px; background:linear-gradient(120deg,rgba(24,50,72,.94),rgba(14,23,39,.94)); margin-bottom:1.1rem; }
.kicker { color:#4ed9e2; font-size:.78rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.subtle { color:#a7b7cc; }
.metric-card { background:rgba(18,29,46,.92); border:1px solid #263b52; padding:1rem 1.1rem; border-radius:14px; min-height:110px; }
.metric-label { color:#9eacc2; font-size:.82rem; }
.metric-value { color:#f6f9ff; font-size:1.7rem; font-weight:750; margin-top:.25rem; }
.note { border-left:3px solid #e6b75a; background:rgba(230,183,90,.08); padding:.8rem 1rem; border-radius:6px; color:#e8d6aa; }
.oknote { border-left:3px solid #4ed9e2; background:rgba(78,217,226,.07); padding:.8rem 1rem; border-radius:6px; }
div[data-testid="stDataFrame"] { border:1px solid #263b52; border-radius:12px; }
a { color:#70e3eb !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧬 AMR-GUARD X Ω")
    st.caption("Research prototype • One Health intelligence")
    page = st.radio("Workspace", ["Overview", "Analyze an isolate", "Demo surveillance", "Methods & sources"], label_visibility="visible")
    st.divider()
    st.markdown("**Prototype scope**")
    st.caption("Organism focus: *Escherichia coli*")
    st.caption("Mechanism focus: selected β-lactam resistance markers")
    st.caption("Mode: reference-based interpretation")
    st.divider()
    st.caption("Not for clinical diagnosis or treatment selection.")

if page == "Overview":
    st.markdown("""
    <div class="hero">
      <div class="kicker">Agentic-ready • Explainable • Evidence-linked</div>
      <h1 style="font-size:2.55rem;margin:.35rem 0;">Antimicrobial resistance intelligence</h1>
      <p style="font-size:1.08rem;max-width:900px;">A transparent research workspace for interpreting selected resistance markers, separating observed laboratory results from genomic findings, and producing source-linked reports.</p>
      <p class="subtle">Built as a focused, auditable first prototype—not as a clinically validated prediction system.</p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col, label, value, desc in [
        (c1,"Analysis workflow","3 stages","Input → interpret → export"),
        (c2,"Evidence model","Traceable","Every marker maps to a reference resource"),
        (c3,"Safety design","Human-reviewed","No autonomous prescribing"),
    ]:
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="subtle">{desc}</div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown("### What this prototype can do")
    left,right = st.columns(2)
    with left:
        st.markdown("""
        - Interpret a user-provided list of resistance gene symbols against a small, transparent reference catalogue.
        - Distinguish detected markers from phenotypic antimicrobial susceptibility testing (AST).
        - Flag unknown markers and missing information rather than silently guessing.
        """)
    with right:
        st.markdown("""
        - Display reference links for follow-up verification.
        - Export a timestamped, structured analysis report.
        - Demonstrate a clear pathway toward validated ML and broader One Health surveillance.
        """)
    st.markdown('<div class="note"><b>Important:</b> This initial version does not run sequence alignment, infer clinical susceptibility, or generate a validated resistance probability. A gene marker alone cannot establish a complete susceptibility profile.</div>', unsafe_allow_html=True)
    st.button("Start an isolate analysis →", on_click=lambda: st.session_state.update({"jump_analysis": True}))
    if st.session_state.pop("jump_analysis", False):
        st.info("Choose **Analyze an isolate** in the left navigation to begin.")

elif page == "Analyze an isolate":
    st.markdown("## Analyze an isolate")
    st.write("Enter marker symbols already identified by a validated pipeline or use the demo input. This form interprets supplied names; it does not analyze raw FASTA files.")
    col1,col2 = st.columns([1.2,1])
    with col1:
        isolate_id = st.text_input("Isolate / sample ID", value="ECOLI-DEMO-001", max_chars=80)
        organism = st.selectbox("Organism", ["Escherichia coli", "Other / not confirmed"])
        source = st.selectbox("Sample context", ["Research / teaching dataset", "Veterinary", "Human", "Environmental", "Unknown"])
        gene_input = st.text_area("Detected resistance markers (comma or newline separated)", value="blaTEM-1, tetA", height=130,
                                  help="Enter marker names only if they were identified by a suitable analysis workflow.")
        ast_input = st.text_area("Observed AST results (optional)", placeholder="Example: ampicillin=Resistant; cefotaxime=Not tested", height=90)
    with col2:
        st.markdown("### Analysis settings")
        st.info("Reference-based mode: transparent lookup only. Unknown names are reported as unresolved.")
        include_links = st.checkbox("Include reference links in report", value=True)
        st.caption("Do not enter personal, patient-identifiable, or confidential laboratory information.")
        st.caption("No information is transmitted to an external prediction service by this demo.")
    if st.button("Run reference interpretation", type="primary", use_container_width=True):
        if not isolate_id.strip():
            st.error("Please provide an isolate ID.")
        elif not gene_input.strip():
            st.error("Enter at least one marker or use the demo input.")
        else:
            result = analyze_gene_list(gene_input, organism)
            st.session_state["last_analysis"] = {
                "isolate_id": isolate_id.strip(),
                "organism": organism,
                "source": source,
                "gene_input": gene_input,
                "ast_input": ast_input,
                "include_links": include_links,
                "result": result,
            }
    if "last_analysis" in st.session_state:
        a = st.session_state["last_analysis"]
        result = a["result"]
        st.divider()
        st.markdown(f"### Results for `{a['isolate_id']}`")
        m1,m2,m3 = st.columns(3)
        m1.metric("Markers supplied", result["supplied_count"])
        m2.metric("Reference matches", result["matched_count"])
        m3.metric("Unresolved markers", result["unresolved_count"])
        if result["unresolved_count"]:
            st.warning("Some supplied names were not matched to this prototype's reference catalogue. This does not mean the marker is absent or biologically irrelevant.")
        if a["organism"] != "Escherichia coli":
            st.warning("The current reference catalogue is scoped to selected markers commonly discussed in E. coli. Interpretations may not transfer to other organisms.")
        df = pd.DataFrame(result["findings"])
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("### Phenotypic AST notes")
        if a["ast_input"].strip():
            st.write(a["ast_input"])
            st.caption("AST text is displayed as user-supplied observation and is not independently verified or interpreted by this prototype.")
        else:
            st.write("No phenotypic AST results supplied.")
        st.markdown('<div class="note">Genotype-to-phenotype inference is complex. Confirm findings with validated laboratory susceptibility testing and organism-specific standards. This report is for research/educational use only.</div>', unsafe_allow_html=True)
        report = build_report(a, include_links=a["include_links"])
        st.download_button("Download analysis report (.md)", report, file_name=f"{a['isolate_id'].replace(' ','_')}_amr_report.md", mime="text/markdown")
        st.download_button("Download findings (.csv)", pd.DataFrame(result["findings"]).to_csv(index=False), file_name=f"{a['isolate_id'].replace(' ','_')}_findings.csv", mime="text/csv")

elif page == "Demo surveillance":
    st.markdown("## Demo surveillance workspace")
    st.write("Illustrative records demonstrate dashboard behavior only. They are synthetic and must not be presented as real surveillance findings.")
    df = pd.DataFrame(DEMO_ISOLATES)
    a,b,c = st.columns(3)
    a.metric("Illustrative records", len(df))
    b.metric("Contexts represented", df["context"].nunique())
    c.metric("Data status", "Synthetic")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.bar_chart(df.groupby("context").size(), x_label="Context", y_label="Illustrative record count")
    st.markdown('<div class="note">These example records are synthetic placeholders, not measured prevalence estimates. Do not use them to infer trends or make public-health claims.</div>', unsafe_allow_html=True)
    st.download_button("Download synthetic demo data (.csv)", df.to_csv(index=False), file_name="synthetic_demo_surveillance.csv", mime="text/csv")

else:
    st.markdown("## Methods, limitations & sources")
    st.markdown("""
    ### Current method
    1. Accepts user-supplied marker symbols.
    2. Normalizes text and matches symbols against a small local reference catalogue.
    3. Reports known reference descriptions and unresolved inputs.
    4. Keeps AST notes as separately labelled user-supplied observations.
    5. Exports a report with scope and safety caveats.

    ### Not implemented in this MVP
    - Raw sequence alignment or variant calling.
    - A trained resistance classifier or calibrated resistance probabilities.
    - Automated live database queries.
    - Clinical decision-making or drug recommendations.
    - Real-time surveillance data ingestion.
    """)
    st.markdown("### Reference resources")
    for label, url in RESOURCE_LINKS.items():
        st.markdown(f"- [{label}]({url})")
    st.markdown("""
    ### Validation plan before scientific use
    - Freeze a versioned, documented reference dataset.
    - Evaluate gene detection against an appropriate curated benchmark.
    - For any future phenotype classifier, use isolate-level train/test separation and external validation where possible.
    - Report per-class sensitivity, specificity, precision, recall, F1, AUROC and calibration when appropriate.
    - Audit organism, antimicrobial, geographic and temporal coverage; document class imbalance and missingness.
    - Obtain domain-expert review before any operational deployment.
    """)
