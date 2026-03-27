# Phase 64 — Claude Reviewing ADMET Flags

**Version:** 1.1 | **Tier:** Standard | **Date:** 2026-03-27

## Goal
Give Claude computed ADMET properties for compounds and ask for a structured risk review.
Demonstrates Claude as a structured reviewer producing actionable drug-likeness assessments.

CLI: `python main.py --input data/compounds.csv --n 3`

Outputs: admet_review.json, admet_report.txt

## Logic
- Compute ADMET properties locally with RDKit (MW, LogP, TPSA, HBD, HBA, RotBonds, rings, heavy atoms)
- Format properties as JSON table and send to Claude
- Ask for per-compound risk assessment: risk_level (low/medium/high), flags array, recommendation string
- Parse structured JSON response and report review quality

## Key Concepts
- Hybrid pattern: RDKit computes properties locally, Claude interprets them
- Structured review output with actionable risk levels
- Claude applies medicinal chemistry heuristics (RO5, metabolic stability, lipophilicity concerns)
- Tests whether Claude can identify meaningful ADMET flags vs generic responses

## Verification Checklist
- [x] RDKit properties computed locally (MW, LogP, TPSA, HBD, HBA, RotBonds)
- [x] Claude returns structured review with risk levels for all compounds
- [x] One clean API call
- [x] Flags reference specific property values

## Results
| Metric | Value |
|--------|-------|
| Compounds reviewed | 3 |
| Reviews returned | 3/3 |
| Risk levels | benz_001_F=low, benz_002_Cl=low, benz_003_Br=medium |
| Br flag | MW approaching threshold, elevated LogP, halogenation concern |
| Input tokens | 505 |
| Output tokens | 466 |
| Est. cost | $0.0023 |

## Risks (resolved)
- Claude may hallucinate property values — mitigated by computing properties locally with RDKit, only sending computed values
- Generic "all low risk" responses — not observed; Claude correctly flagged Br-specific metabolic concerns
- Risk level thresholds may be inconsistent across calls — mitigated by explicit system prompt

Key finding: Claude correctly identified benz_003_Br as medium risk due to bromine-specific metabolic/bioaccumulation concerns — a nuanced medchem flag beyond simple RO5 violations.
