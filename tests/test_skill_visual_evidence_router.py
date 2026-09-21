from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_notecard_skill_routes_visual_evidence_without_adding_card_roles() -> None:
    skill = (ROOT / "skills" / "notecard-teacher-style" / "SKILL.md").read_text()
    router = (
        ROOT
        / "skills"
        / "notecard-teacher-style"
        / "references"
        / "visual-evidence-router.md"
    ).read_text()

    assert "visual-evidence-router.md" in skill
    assert "Reference comparison recipe" in router
    assert "No new card" not in router  # routing guidance, not another card family
    assert "**Dashboard:** out of scope" in router
    assert "PR curve plus prevalence baseline" in router
    assert "PCA scatter is not the setup" in router
    assert "Color reinforces" in router
    assert "Supervised-classification story spine" in router
    assert "Do not hard-code a winning model assertion" in router
    assert "Do not draw one equal-length bar per unique decision" in router
    assert "Do not invent a business target" in router

    vocabulary = (
        ROOT
        / "skills"
        / "notecard-teacher-style"
        / "references"
        / "visual-vocabulary-contract.md"
    ).read_text()
    assert "inventory" in vocabulary.lower() and "evidence job" in vocabulary.lower()
    assert "histogram" in vocabulary and "violin" in vocabulary
    assert "confusion matrix" in vocabulary and "threshold tradeoff" in vocabulary
    assert "plain-language reason" in vocabulary and "planning cell" in vocabulary


def test_skill_requires_local_pandas_rhythm_and_target_contract() -> None:
    skill = (ROOT / "skills" / "notecard-teacher-style" / "SKILL.md").read_text()
    rhythm = (
        ROOT
        / "skills"
        / "notecard-teacher-style"
        / "references"
        / "pandas-notecard-rhythm.md"
    ).read_text()
    target = (
        ROOT
        / "skills"
        / "notecard-teacher-style"
        / "references"
        / "target-analysis-contract.md"
    ).read_text()

    assert "pandas-notecard-rhythm.md" in skill
    assert "target-analysis-contract.md" in skill
    assert "Pandas is the audit trail" in rhythm
    normalized_rhythm = " ".join(rhythm.split())
    assert "same cell or in immediately adjacent cells" in normalized_rhythm
    assert "complete missingness evidence" in rhythm.lower()
    assert "customer goodwill" in target
    assert "binary target does not have box-plot outliers" in target.lower()
    assert "test is opened once" in target


def test_release_checklist_protects_reference_and_rare_event_comparisons() -> None:
    checklist = (ROOT / "docs" / "OPEN_SOURCE_GRAPH_CHECKLIST.md").read_text()

    assert "Rare-outcome classification" in checklist
    assert "Actual/prior/target comparisons" in checklist
    assert "red marker does not silently imply" in checklist


def test_formula_source_uses_explicit_math_spacing() -> None:
    builder = (ROOT / "scripts" / "build_synthetic_seasonal_demo.py").read_text()

    assert r"\mathrm{split\;in\;time}" in builder
    assert r"\text{{split in time}}" not in builder


def test_private_writing_skill_is_not_part_of_the_oss_package() -> None:
    readme = (ROOT / "README.md").read_text()
    manifest = (ROOT / "MANIFEST.in").read_text()

    assert not (ROOT / "skills" / "wilton-campaign-persuasion").exists()
    assert "wilton-campaign-persuasion" not in readme
    assert "wilton-campaign-persuasion" not in manifest
