from amr_engine import analyze_gene_list, build_report

def test_known_marker_matches():
    result = analyze_gene_list("blaTEM-1, tetA")
    assert result["supplied_count"] == 2
    assert result["matched_count"] == 2
    assert result["unresolved_count"] == 0

def test_unknown_marker_is_not_called_absent():
    result = analyze_gene_list("madeup-marker")
    assert result["unresolved_count"] == 1
    assert "does not mean" in result["findings"][0]["Caveat"]

def test_duplicate_marker_deduplication():
    result = analyze_gene_list("tetA, tetA")
    assert result["matched_count"] == 1
    assert result["supplied_count"] == 2

def test_report_has_safety_limitations():
    analysis = {
        "isolate_id": "TEST-1",
        "organism": "Escherichia coli",
        "source": "Research / teaching dataset",
        "ast_input": "",
        "result": analyze_gene_list("blaTEM-1"),
    }
    report = build_report(analysis)
    assert "not a clinically validated diagnostic system" in report
    assert "No raw sequence alignment" in report
