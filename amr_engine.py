import re
from datetime import datetime, timezone

RESOURCE_LINKS = {
    "NCBI AMRFinderPlus": "https://www.ncbi.nlm.nih.gov/pathogens/antimicrobial-resistance/AMRFinder/",
    "CARD — Comprehensive Antibiotic Resistance Database": "https://card.mcmaster.ca/",
    "NCBI Pathogen Detection": "https://www.ncbi.nlm.nih.gov/pathogens/",
    "WHO — Antimicrobial resistance": "https://www.who.int/health-topics/antimicrobial-resistance",
}

# Small educational catalogue. These entries are not a comprehensive or clinically validated interpretation database.
MARKER_CATALOG = {
    "blatem": {
        "canonical": "blaTEM family",
        "class": "β-lactam resistance marker",
        "interpretation": "TEM-family β-lactamase genes may be associated with resistance to some β-lactam antibiotics. Exact allele and organism context matter.",
        "caveat": "Family-level name is not sufficient to infer the full susceptibility profile.",
        "resource": "NCBI AMRFinderPlus",
        "url": RESOURCE_LINKS["NCBI AMRFinderPlus"],
    },
    "bla-tem-1": {
        "canonical": "blaTEM-1",
        "class": "β-lactam resistance marker",
        "interpretation": "TEM-1 is a β-lactamase determinant associated with resistance to certain penicillins; phenotype depends on context and testing.",
        "caveat": "Do not infer resistance to every β-lactam or a treatment choice from this marker alone.",
        "resource": "NCBI AMRFinderPlus",
        "url": RESOURCE_LINKS["NCBI AMRFinderPlus"],
    },
    "blactx-m": {
        "canonical": "blaCTX-M family",
        "class": "β-lactam resistance marker",
        "interpretation": "CTX-M-family extended-spectrum β-lactamase determinants are associated with resistance to many extended-spectrum cephalosporins.",
        "caveat": "Exact allele, expression, co-resistance and laboratory results remain important.",
        "resource": "CARD",
        "url": RESOURCE_LINKS["CARD — Comprehensive Antibiotic Resistance Database"],
    },
    "blandm": {
        "canonical": "blaNDM family",
        "class": "β-lactam resistance marker",
        "interpretation": "NDM-family metallo-β-lactamase determinants are associated with resistance to many β-lactams, including carbapenems.",
        "caveat": "Confirm identity and interpret with current organism-specific laboratory standards.",
        "resource": "NCBI AMRFinderPlus",
        "url": RESOURCE_LINKS["NCBI AMRFinderPlus"],
    },
    "blakpc": {
        "canonical": "blaKPC family",
        "class": "β-lactam resistance marker",
        "interpretation": "KPC-family carbapenemase determinants can be associated with carbapenem resistance.",
        "caveat": "Phenotypic susceptibility and current clinical guidance are still required.",
        "resource": "CARD",
        "url": RESOURCE_LINKS["CARD — Comprehensive Antibiotic Resistance Database"],
    },
    "teta": {
        "canonical": "tet(A)",
        "class": "Tetracycline resistance marker",
        "interpretation": "tet(A) commonly encodes an efflux determinant associated with tetracycline resistance.",
        "caveat": "Expression, genetic context and phenotype should be assessed separately.",
        "resource": "CARD",
        "url": RESOURCE_LINKS["CARD — Comprehensive Antibiotic Resistance Database"],
    },
    "sul1": {
        "canonical": "sul1",
        "class": "Sulfonamide resistance marker",
        "interpretation": "sul1 is associated with sulfonamide resistance through an alternative dihydropteroate synthase.",
        "caveat": "Confirm sequence identity and review the complete susceptibility profile.",
        "resource": "NCBI AMRFinderPlus",
        "url": RESOURCE_LINKS["NCBI AMRFinderPlus"],
    },
    "mcr-1": {
        "canonical": "mcr-1",
        "class": "Polymyxin resistance marker",
        "interpretation": "mcr-1 is associated with plasmid-mediated colistin resistance mechanisms.",
        "caveat": "This simplified catalogue is not a substitute for confirmatory testing and current expert interpretation.",
        "resource": "NCBI Pathogen Detection",
        "url": RESOURCE_LINKS["NCBI Pathogen Detection"],
    },
}

def _norm(value: str) -> str:
    return re.sub(r"[\s_]", "", value.strip().lower())

def _lookup_key(value: str) -> str:
    key = _norm(value)
    aliases = {
        "blatem1": "bla-tem-1",
        "blatem-1": "bla-tem-1",
        "bla-tem": "blatem",
        "blactxm": "blactx-m",
        "bla-ctx-m": "blactx-m",
        "bla-ndm": "blandm",
        "bla-kpc": "blakpc",
        "teta": "teta",
        "tet(a)": "teta",
        "mcr1": "mcr-1",
        "sul-1": "sul1",
    }
    return aliases.get(key, key)

def analyze_gene_list(raw: str, organism: str = "Escherichia coli") -> dict:
    tokens = [t.strip() for t in re.split(r"[,;\n]+", raw) if t.strip()]
    findings = []
    seen = set()
    for token in tokens:
        key = _lookup_key(token)
        if key in seen:
            continue
        seen.add(key)
        item = MARKER_CATALOG.get(key)
        if item:
            findings.append({
                "Input marker": token,
                "Reference match": item["canonical"],
                "Marker class": item["class"],
                "Interpretation": item["interpretation"],
                "Caveat": item["caveat"],
                "Reference": item["resource"],
                "Evidence URL": item["url"],
                "Status": "Reference match — verify allele and context",
            })
        else:
            findings.append({
                "Input marker": token,
                "Reference match": "No match in prototype catalogue",
                "Marker class": "Unresolved",
                "Interpretation": "No interpretation generated. Check spelling, sequence evidence, database coverage, and organism context.",
                "Caveat": "Not found in this small prototype catalogue does not mean the marker is absent or novel.",
                "Reference": "—",
                "Evidence URL": "",
                "Status": "Unresolved — manual review required",
            })
    matched = sum(1 for f in findings if f["Status"].startswith("Reference match"))
    return {
        "findings": findings,
        "supplied_count": len(tokens),
        "matched_count": matched,
        "unresolved_count": len(findings) - matched,
        "organism": organism,
        "method": "Local curated demonstration lookup; no raw-sequence analysis or phenotype prediction performed.",
    }

def build_report(analysis: dict, include_links: bool = True) -> str:
    result = analysis["result"]
    lines = [
        "# AMR-GUARD X Ω — Reference Interpretation Report",
        "",
        f"- **Generated (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Isolate ID:** {analysis['isolate_id']}",
        f"- **Organism selected:** {analysis['organism']}",
        f"- **Sample context:** {analysis['source']}",
        f"- **Markers supplied:** {result['supplied_count']}",
        f"- **Reference matches:** {result['matched_count']}",
        f"- **Unresolved markers:** {result['unresolved_count']}",
        "",
        "## Method",
        result["method"],
        "",
        "## Findings",
    ]
    for item in result["findings"]:
        lines.extend([
            f"### {item['Input marker']}",
            f"- **Reference match:** {item['Reference match']}",
            f"- **Class:** {item['Marker class']}",
            f"- **Interpretation:** {item['Interpretation']}",
            f"- **Caveat:** {item['Caveat']}",
            f"- **Status:** {item['Status']}",
        ])
        if include_links and item.get("Evidence URL"):
            lines.append(f"- **Reference:** {item['Evidence URL']}")
        lines.append("")
    lines.extend([
        "## User-supplied phenotypic AST notes",
        analysis["ast_input"].strip() or "No AST notes supplied.",
        "",
        "## Limitations and safe use",
        "- This is a research/educational prototype, not a clinically validated diagnostic system.",
        "- The marker catalogue is small and is not comprehensive.",
        "- A marker match does not prove a complete antimicrobial susceptibility profile.",
        "- No raw sequence alignment, variant calling, ML inference, calibrated probability, or treatment recommendation was performed.",
        "- Verify all findings using current curated databases, organism-specific standards, and appropriate laboratory testing.",
        "",
    ])
    return "\n".join(lines)

DEMO_ISOLATES = [
    {"sample_id": "DEMO-EC-001", "organism": "E. coli", "context": "Veterinary", "markers": "blaTEM-1; tetA", "data_status": "Synthetic"},
    {"sample_id": "DEMO-EC-002", "organism": "E. coli", "context": "Environmental", "markers": "sul1", "data_status": "Synthetic"},
    {"sample_id": "DEMO-EC-003", "organism": "E. coli", "context": "Human", "markers": "blaCTX-M", "data_status": "Synthetic"},
    {"sample_id": "DEMO-EC-004", "organism": "E. coli", "context": "Research / teaching", "markers": "No marker supplied", "data_status": "Synthetic"},
    {"sample_id": "DEMO-EC-005", "organism": "E. coli", "context": "Unknown", "markers": "mcr-1", "data_status": "Synthetic"},
]
