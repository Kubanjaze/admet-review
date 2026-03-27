# Phase 64 — Claude Reviewing ADMET Flags

**Version:** 1.0 | **Tier:** Standard | **Date:** 2026-03-26

## Goal
Give Claude computed ADMET properties for 3 compounds and ask for a structured risk review.
Demonstrates Claude as a structured reviewer producing actionable assessments.

CLI: `python main.py --input data/compounds.csv --n 3`

Outputs: admet_review.json, admet_report.txt

## Logic
- Compute ADMET properties with RDKit (MW, LogP, TPSA, HBD, HBA, RotBonds)
- Send properties table to Claude, ask for structured risk assessment per compound
- Expected output: JSON with risk_level (low/medium/high), flags, recommendation
- Report: review quality, completeness, cost

## Verification Checklist
- [ ] RDKit properties computed locally
- [ ] Claude returns structured review with risk levels
- [ ] One clean API call
