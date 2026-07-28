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
