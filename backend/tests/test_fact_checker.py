from app.services.fact_checker import find_speculative_claims


def test_flags_unsupported_ai_and_superlative_claims() -> None:
    draft = (
        "Pathos Labs launched Pulse, an AI platform that will eliminate all reporting errors. "
        "It is the first tool of its kind and improves results by 95 percent."
    )

    findings = find_speculative_claims(draft)

    categories = {finding.category for finding in findings}
    assert "ai_capability" in categories
    assert "superlative" in categories
    assert "statistic" in categories


def test_does_not_flag_plain_factual_copy() -> None:
    draft = "Pathos Labs opened its Manchester office in 2025 and employs twelve people."

    assert find_speculative_claims(draft) == []
