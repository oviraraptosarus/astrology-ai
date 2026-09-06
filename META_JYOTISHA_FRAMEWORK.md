# Meta-Jyotisha Framework

This document outlines the architecture, principles, and execution pipeline of the Ultimate Jyotisha Reasoning System.

## Core Philosophy: Deterministic Grounding
The LLM (Gemini) does not "do astrology." It acts as a synthesizer and interpreter of data provided by a rigid, deterministic, source-grounded Python backend. The system calculates exactly what classical rules dictate and feeds a structured `EventAnalysisResult` payload to the LLM. 

## The Multi-Methodology Pipeline

The core engine (`event_analysis.py` via `EventPredictionEngine`) follows this unyielding pipeline:

### 1. QUESTION & DOMAIN ROUTING
User inputs a question ("Will I get married this year?").
- `MethodologyRouter` extracts the domain ("MARRIAGE") and builds a routing profile.
- Determines the required Vargas (e.g., D9), required Dashas (e.g., Vimshottari), and primary authority (e.g., K.N. Rao).

### 2. NATAL PROMISE (D1 + Varga + Yogas)
- `DomainEngine` checks the strength of the 7th House, 7th Lord, and Venus in D1 and D9.
- `VargaEngine` evaluates Vimsopaka Bala and dignity in D9.
- `StrengthEngine` evaluates exact Shadbala (Virupas).
- Yogas are evaluated, specifically looking for `NeechabhangaRajaYoga` (debilitation cancellations) to prevent false negatives.
- Outputs an overall confidence score: `VERY_STRONG`, `STRONG`, `MODERATE`, `WEAK`, or `VERY_WEAK`.

### 3. ACTIVATION (Dasha)
- `DashaEngine` generates the exact timeline (Mahadasha, Antardasha, Pratyantardasha).
- The engine checks if the current Dasha lords are connected to the Domain (e.g., 7th Lord, Venus).

### 4. TIMING (Transits)
- `TransitEngine` evaluates the exact current positions of heavyweights (Saturn and Jupiter) via `pyswisseph`.
- It executes K.N. Rao's Double Transit logic, identifying which natal houses and lords are simultaneously activated by both planets.

### 5. CONVERGENCE (Method A vs B)
- `SynthesisEngine` compares the primary Parashari analysis against secondary methodologies (like Jaimini Arudhas via `JaiminiEngine`).
- If Parashari says `STRONG` but Jaimini says `WEAK`, the engine flags a `DISAGREEMENT` for the LLM to interpret cautiously.

### 6. LLM GUIDANCE
- The final, synthesized payload is handed to the LLM, which formats the deterministic output into compassionate, highly accurate, and source-cited guidance.

## Advanced Modules
- **Rectification**: Generates candidate charts and checks for Dasha/Varga shifts against known life events.
- **Prashna (Horary)**: Uses Tajaka applying/separating aspects (Ithasala/Easarpha) based on the exact time a question is received.
- **Specialized Engines**: Includes Tajaka (Varshaphala), Compatibility (Ashtakoota), Longevity (Ayurdaya), Remedies (Upayas), Numerology, Lal Kitab, KP, and Western Tropical.

This architecture ensures the Jyotisha AI remains testable, accurate, and faithful to classical texts.
