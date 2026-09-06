# Master Astrology Correctness Audit

**Date:** 2026-08-31
**Target:** Vedic Astrology AI Reasoning Engine

This document tracks the forensic correctness of the astrological engine. It separates "code that compiles" from "astrology that is classically verified."

## 1. Subsystem Audit (Phase 1)

| Subsystem | Status | Notes |
| :--- | :--- | :--- |
| `vedic_models.py` | LIKELY_CORRECT | Core dataclasses. Requires strict verification that Enums restrict improper data mixing. |
| `astrology_engine.py` | LIKELY_CORRECT | Relies on `pyswisseph` for core astronomy, which is the gold standard. Need to verify Ayanamsa consistency (Lahiri default). |
| `varga_engine.py` | CORRECT | D2, D3, D4, D7, D9, D10, D12, D16, D20, D24, D30, D60 verified against Parashari boundary rules. D24 corrected to start from Leo (odd)/Cancer (even). Odd/Even sign calculation in D30 is correct. |
| `strength_engine.py` (Shadbala) | PARTIAL | Output currently flags `"is_partial": true`. Dig Bala and Sthana Bala are present, but Drik Bala and Cheshta Bala calculations need verification against *Graha and Bhava Balas*. |
| `strength_engine.py` (Bhava Bala) | PARTIAL | Methodology is explicitly sign-based (Whole Sign), but Bhava Dig Bala is heavily approximated (static 60/30) and Bhava Drishti Bala is completely omitted (returns 0.0). |
| `ashtakavarga_engine.py` | PARTIAL | Basic BAV/SAV likely implemented, but synthesis engine reports `"Ashtakavarga exact binding not calculated"`. Trikona/Ekadhipatya reductions need verification. |
| `jaimini_engine.py` | CORRECT | Supports both 7-Karaka and 8-Karaka (Rahu included via backward longitude) schemes based on methodology toggle. Arudha Lagna exception rules (1st->10th, 7th->4th) verified. |
| `yogas.py` | LIKELY_CORRECT | Yogas (Gaja Kesari, Pancha Mahapurusha) correctly track Combustion/Shadbala to filter false positives. Neechabhanga correctly identifies the 4 classical conditions, but fails to check if the *cancelling planet* itself is strong enough to cause a true Raja Yoga (i.e. not combust/debilitated). |
| `condition_engine.py` | PARTIAL | Combustion thresholds perfectly match Surya Siddhanta (including retrograde adjustments). Balaadi Avasthas are exact. Planetary War uses longitude as a standard proxy. However, Dignity calculation uses only Natural Friendship, completely missing Temporal (Tatkalika) and Compound (Panchadha) Friendship calculations needed for proper dignity refinement. |
| `astrology_engine.py` (Vimshottari Dasha) | CORRECT | Proportional timing logic matches standard 365.25 day Vimshottari calculations. Accurately nests down to Pratyantardasha. |
| `jaimini_engine.py` (Chara Dasha) | PARTIAL | Correctly calculates forward/backward counting per K.N. Rao rules. Dual lordship (Scorpio/Aquarius) needs implementation for full accuracy. |
| `astrology_engine.py` (House System) | CORRECT | Explicitly separates Whole Sign (default `house` attribute) from Bhava Chalit (`chalit_house`). Replaced erroneous Placidus calculation with standard Vedic Sri Pati (Porphyry) calculation for Chalit. |
| `condition_engine.py` (Functional Benefics) | CORRECT | Implementation of `FunctionalBeneficEngine` added, covering Functional Roles (Yoga Karakas, Marakas, Trishadayas) and Panchadha Maitri (Compound Friendships) based on Lagna. |
| `domain_engine.py` (House Classifications) | CORRECT | `HouseEngine.get_house_classifications` now maps all houses to structural Vedic classifications (Kendra, Trikona, Upachaya, Dusthana, Maraka, Apoklima, Panapara). |

## 2. Top Priority Astrological Corrections

1. **Jaimini 7 vs 8 Karakas**: Implement a methodology toggle to support both the K.N. Rao (7) and Sanjay Rath (8) systems. Currently, Rahu is completely ignored in the Chara Karaka calculation.
2. **Functional Benefic/Malefic Engine**: The engine currently tracks *Natural* friendships (e.g. Venus is enemy to Sun). It MUST track *Functional* friendships (e.g., for Leo Ascendant, Mars is a Yoga Karaka and highly benefic, regardless of natural enmity).
3. **Shadbala Completion**: Complete the Drik Bala (aspectual strength) and Cheshta Bala (motional strength) equations to remove the `"is_partial": true` flag.
4. **Ashtakavarga Reductions**: Implement Shodhya Pinda calculations for exact transit timing.
5. **Arudha Lagna Exceptions**: Verify that if the Lagna Lord is in the 1st or 7th house, the Arudha Lagna rules fall back to the 10th/4th houses as per Jaimini Sutras.
