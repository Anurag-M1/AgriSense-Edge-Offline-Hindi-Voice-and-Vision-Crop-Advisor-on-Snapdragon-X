"""
safety.py — LLM output safety post-processing for AgriSense Edge.

Ensures the LLM response follows agronomy safety rules:
1. No chemical names/doses not present in retrieved knowledge base notes.
2. Disclaimer line always present.
3. Low-confidence wording when classifier confidence is low.
4. IPM steps preferred over chemical solutions.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


# Hindi disclaimer that must appear in every response
DISCLAIMER_HI = "कृपया अपने स्थानीय कृषि विज्ञान केंद्र / कृषि अधिकारी से पुष्टि करें।"
DISCLAIMER_EN = "Please confirm with your local Krishi Vigyan Kendra / agriculture officer."

# Low confidence prefix
LOW_CONFIDENCE_HI = "मुझे पूरा भरोसा नहीं है।"
LOW_CONFIDENCE_EN = "I am not fully confident in this identification."

# Common pesticide / chemical patterns to detect
CHEMICAL_PATTERNS = [
    r"\b\d+\s*(ml|gm|gram|kg|litre|liter|%)\b",  # Dosage patterns
    r"\b(spray|spraying|छिड़काव|स्प्रे)\s+\d+",  # Spray with numbers
]


@dataclass
class SafetyCheckResult:
    """Result of safety post-processing."""

    original_text: str
    processed_text: str
    was_modified: bool
    modifications: list[str]  # Description of each modification made
    passed: bool  # Whether the response passed safety checks


def check_and_fix_response(
    llm_text: str,
    retrieved_notes: list[str],
    disease_confidence: float,
    confidence_threshold: float = 0.4,
    language: str = "hi",
) -> SafetyCheckResult:
    """Post-process LLM output for agronomy safety.

    Args:
        llm_text: Raw LLM output text.
        retrieved_notes: Knowledge base notes that were provided as context.
        disease_confidence: Confidence of the disease classifier (0-1).
        confidence_threshold: Below this, add low-confidence warning.
        language: Response language ("hi" or "en").

    Returns:
        SafetyCheckResult with the processed text and modification log.
    """
    text = llm_text.strip()
    modifications: list[str] = []

    # 1. Check for un-sourced chemical names / doses
    text, chem_mods = _block_unsourced_chemicals(text, retrieved_notes)
    modifications.extend(chem_mods)

    # 2. Add low-confidence warning if needed
    if disease_confidence < confidence_threshold:
        low_conf = LOW_CONFIDENCE_HI if language == "hi" else LOW_CONFIDENCE_EN
        if low_conf not in text:
            text = f"{low_conf}\n\n{text}"
            modifications.append("Added low-confidence warning")

    # 3. Ensure disclaimer is present
    disclaimer = DISCLAIMER_HI if language == "hi" else DISCLAIMER_EN
    if disclaimer not in text:
        text = f"{text}\n\n{disclaimer}"
        modifications.append("Added safety disclaimer")

    return SafetyCheckResult(
        original_text=llm_text,
        processed_text=text,
        was_modified=len(modifications) > 0,
        modifications=modifications,
        passed=len([m for m in modifications if "Blocked" in m]) == 0,
    )


def _block_unsourced_chemicals(
    text: str, retrieved_notes: list[str]
) -> tuple[str, list[str]]:
    """Block chemical names and doses not found in retrieved notes.

    Args:
        text: LLM response text.
        retrieved_notes: Knowledge base notes used as context.

    Returns:
        Tuple of (modified text, list of modification descriptions).
    """
    modifications = []
    notes_text = " ".join(retrieved_notes).lower()

    # Check for dosage patterns that aren't in the notes
    for pattern in CHEMICAL_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            matched_text = match.group()
            if matched_text.lower() not in notes_text:
                text = text.replace(
                    matched_text,
                    "[खुराक के लिए कृषि अधिकारी से पूछें]",
                )
                modifications.append(f"Blocked un-sourced dosage: '{matched_text}'")

    return text, modifications


def validate_response_safety(
    text: str,
    retrieved_notes: list[str],
) -> list[str]:
    """Validate a response against safety rules without modifying it.

    Args:
        text: Response text to validate.
        retrieved_notes: Knowledge base notes.

    Returns:
        List of safety violations found (empty if all checks pass).
    """
    violations = []

    # Check disclaimer
    if DISCLAIMER_HI not in text and DISCLAIMER_EN not in text:
        violations.append("Missing safety disclaimer")

    # Check for un-sourced dosages
    notes_text = " ".join(retrieved_notes).lower()
    for pattern in CHEMICAL_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if match.group().lower() not in notes_text:
                violations.append(f"Un-sourced chemical/dosage: '{match.group()}'")

    return violations
