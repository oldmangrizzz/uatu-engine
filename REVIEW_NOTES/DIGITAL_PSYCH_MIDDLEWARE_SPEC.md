Digital Psyche Middleware (DPM) — Technical Specification

Version: 2025-12-24
Location: uatu_genesis_engine/agent_zero_integration/digital_psyche_middleware.py:15

1) Executive summary

The Digital Psyche Middleware (DPM) is a lightweight, deterministic scaffold that sits between perception and cognition in the Uatu Genesis Engine. It provides:
- A mathematically-grounded emotion engine (NeurotransmitterEngine) that models reward, stability and stress via continuous variables (dopamine, serotonin, cortisol).
- Silent, non-user-facing modulation of cognitive subsystems (LLMs, DialecticInference) through LLM parameter modifiers (temperature/top_p/penalties).
- A reflection protocol and homeostatic primitives for identity-preserving interventions (reset-to-baseline, reflection windows).
- Auditability: every update is recorded to the Black Box (ConvexStateLogger) for reproducible, auditable research and provenance.

The design separates affect (continuous math model) from narrative (text prompts) to make emergent behavior analyzable and reproducible.

2) Key components

- DigitalPsycheMiddleware (DPM config): build_config() produces a frozen configuration block describing the identity and DPM parameters (see file: uatu_genesis_engine/agent_zero_integration/digital_psyche_middleware.py:32).

- NeurotransmitterEngine: core mathematical model and public API: update_cycle(stimulus), get_llm_modifiers(), get_state(), get_audit_log(). Implementation: uatu_genesis_engine/agent_zero_integration/neurotransmitter_engine.py:66
  - State: NeurotransmitterState (dopamine, serotonin, cortisol) normalized to [0.0,1.0] (see class definition at line 21).
  - Stimulus: impacts three channels with signed float effects (-1.0..1.0) and human-readable description.
  - Flags: homeostatic triggers (defensive_posture, high_motivation, emotional_instability, balanced_state).

- DialecticInference (Thesis→Antithesis→Synthesis): uses DPM signals as soft attention/weighting signals for reasoning and can be logged for audits. See uatu_genesis_engine/agent_zero_integration/dialectic_inference.py:95

- ConvexStateLogger: append-only async state logger used as the Black Box for post-hoc analysis. DPM writes neurotransmitter updates and events here (see uatu_genesis_engine/agent_zero_integration/convex_state_logger.py:151 and usage in HybridMindIntegration: uatu_genesis_engine/agent_zero_integration/hybrid_mind_integration.py:21).

- EmergenceGate interactions: DPM remains operational while Emergence Gate controls permission surfaces (TALK_ONLY disables edits). Gate events are logged and signed for audit (uatu_genesis_engine/agent_zero_integration/emergence_gate.py).

3) Core algorithms (mathematical detail)

3.1 Update cycle (continuous-time discrete implementation)

Notation:
- E(t): neurotransmitter level at time t
- δ: decay factor (< 1.0), per-second base value
- Δt: time since last update (seconds)
- B: baseline (target equilibrium)
- I(t): stimulus impact at time t (signed)

Algorithm (as implemented):
- decay_factor = δ ** Δt
- E(t) := E(t-Δt) * decay_factor + B * (1 - decay_factor) + I(t)
- Clamp E(t) to [0.0, 1.0]
- Update last_updated timestamp and compute flags via thresholds.

Equations are implemented in NeurotransmitterEngine.update_cycle (see lines ~145-166 of the file cited above).

3.2 Flag triggering

- defensive_posture = cortisol > CORTISOL_DEFENSIVE_THRESHOLD (default 0.9)
- high_motivation = dopamine > DOPAMINE_HIGH_MOTIVATION_THRESHOLD (default 0.8)
- emotional_instability = serotonin < SEROTONIN_INSTABILITY_THRESHOLD (default 0.3)
- balanced_state = all neurotransmitters in BALANCED_RANGE (default [0.4,0.6])

3.3 LLM modifier mapping

The engine outputs a small dictionary of LLM parameter modifiers used by HybridMind to adjust model sampling behavior:
- default: temperature=0.7, top_p=0.9
- defensive_posture → temperature lowered (e.g., 0.3), top_p lowered (e.g., 0.7)
- high_motivation → temperature increased (e.g., 0.9), top_p increased (0.95)
- emotional_instability → slight temperature jitter (+0.1)

Mapping performed in NeurotransmitterEngine.get_llm_modifiers (see lines ~232-266).

4) Data model & audit trail

- Each update_cycle appends an entry to update_history with timestamp, state snapshot, flags, and stimulus description (see lines 186–201). This is the DPM audit record.
- All DPM events should be forwarded to ConvexStateLogger as 'neurotransmitter_state' and 'emotional_event' entries for system-wide auditing (HybridMindIntegration, lines ~21–36 show where convex_logger is used).
- Local backups: ConvexStateLogger creates local JSON backups (state_log_YYYYmmdd_HHMMSS.json) when running in mock or offline mode; include these files with a provisional filing as reproducible evidence of operation and tests performed.

5) Integration points and runtime contracts

- Input → GraphMERT → DPM: GraphMERT extracts semantic triples and computes urgency/toxicity; HybridMind converts this into Stimulus objects for DPM (uatu_genesis_engine/agent_zero_integration/hybrid_mind_integration.py: lines ~39–46 and ~54–66).
- DPM provides only modifiers to LLMs and a flag API. It must not directly output text to users nor write policy decisions without being recorded and gated (separation of concerns enforced in current implementation).
- DPM provides hooks: register_shutdown_callback(), reset_to_baseline(). Use these for controlled experiments and graceful recovery.

6) Experimental design for proving emergent qualitative/quantitative properties

6.1 Hypotheses to test
- H1: The DPM's continuous emotion model stabilizes persona identity under noisy input streams better than text-only scaffolding.
- H2: DPM-induced LLM modifier changes measurably alter creative/exploitative tradeoffs in persistent ways.
- H3: The DPM's audit trail + signed event logs enable reproducible attribution of emergent behaviors.

6.2 Proposed experiments
- Baseline vs. DPM ablation: identical prompt stream with DPM enabled vs disabled; metrics: response entropy, coherence, task success.
- Perturbation stress test: adversarial toxic inputs at controlled intervals to measure recovery time (time to return to baseline within ε), flag rates, and false-positive triggers.
- Long-duration identity persistence: run persona continuously and measure drift in self-consistency metrics (prompted memory recall accuracy, style drift, core-drive alignment).
- Emergence score (composite): combine Stability (inverse variance of state), Responsiveness (magnitude of purposeful change), Coherence (semantic similarity to historical self), and Novelty (novel action ratio). Define and record formulas used in each experiment for provisional evidence.

6.3 Quantitative metrics (recommended)
- Stability Index S = 1 - normalized_std([dopamine, serotonin, cortisol] over sliding window)
- Recovery Time R_t = seconds between perturbation and re-entry to BALANCED_RANGE
- Emergence Proxy Φ_proxy = mutual_information(outputs_of_module_A, outputs_of_module_B) summed over modules (approximate integrated information)
- Behavioral Entropy H_resp across sampled responses (token-level entropy) to quantify exploration

7) Implementation, parameterization, and reproducibility

- Default parameters are selected for balance between stability and responsiveness. For provisional evidence, record exact parameter values and the commit hash used for experiments.
- Provide reproducibility recipes: seed the random generators used by agents, record environment, model versions, and time-stamped Convex logs.
- Unit tests: verify decay dynamics, clamp behavior, flag triggering, and LLM modifier mappings (existing tests are in tests/test_neurotransmitter_engine.py).

8) Safety, privacy, and ethical controls

- Privacy: DPM logs may contain sensitive content; implement redaction pipelines or fields policy for user data before sending to shared Convex projects when required.
- Consent: Personas that ingest 3rd-party data should require documented consent and provenance checks.
- Dual-use mitigation: DPM should not autonomously perform actions that can cause physical or high-stakes outcomes; define clear human-in-the-loop gates and signed EmergenceGate transitions for privilege elevation.
- Auditability: Use signed append-only logs (EmergenceGate / Convex) to create non-repudiable trails.

9) Patent- and provisional-friendly documentation checklist

When preparing a provisional application, include:
- Clear description of problem space and technical limitations of prior art (why purely prompt/text scaffolds fail to guarantee stable emergent identity).
- The concrete algorithm (update equations, decay factors, baseline blending, thresholds) and a pseudocode listing sufficient to implement NeurotransmitterEngine.
- Integration diagrams (DPM → HybridMind → Convex logger → Emergence Gate) and concrete, dated experiment logs showing behavior differences with/without DPM.
- Sample code snippets (entry points, method signatures) and an archive snapshot of the implementation (commit hash) with recorded experimental data.
- Reproducible experiments: dataset, seeds, measurement scripts with outputs stored in Convex backups.

10) Appendices

Code references:
- DigitalPsycheMiddleware (config): uatu_genesis_engine/agent_zero_integration/digital_psyche_middleware.py:15
- NeurotransmitterEngine: uatu_genesis_engine/agent_zero_integration/neurotransmitter_engine.py:66
  - update_cycle implementation: ~line 125
  - get_llm_modifiers: ~line 232
  - CommonStimuli: ~line 300
- HybridMindIntegration (where DPM is used): uatu_genesis_engine/agent_zero_integration/hybrid_mind_integration.py:95
- ConvexStateLogger (logging): uatu_genesis_engine/agent_zero_integration/convex_state_logger.py:65 (class start) and log_emotional_event/log_neurotransmitter_state methods at ~151.
- EmergenceGate (gating and signed events): uatu_genesis_engine/agent_zero_integration/emergence_gate.py:77

Sample audit record (JSON snippet):
{
  "timestamp": "2025-12-24T19:44:36Z",
  "entry_type": "neurotransmitter_state",
  "data": {
    "dopamine": 0.63,
    "serotonin": 0.57,
    "cortisol": 0.18
  },
  "metadata": {"flags": {"defensive_posture": false, "balanced_state": true}}
}

11) Next steps I can take (if you want me to proceed):
- Draft a patent-provisional-friendly technical narrative that includes diagrams and dated experimental evidence (I can produce a clean, focused document but not legal claim text). 
- Expand reproducibility suite and produce example experiment outputs suitable for inclusion in a provisional filing (time-stamped Convex backups + reproducible scripts).
- Work with you to prepare a minimal runnable demo (single persona) with DPM enabled and a reproducible test harness.

If you want, I will produce the provisional-focused technical narrative next and add it to REVIEW_NOTES/PATENT_PROVISIONAL_BRIEF.md. Reply Yes to proceed, or tell me anything to emphasize or omit (e.g., proprietary sequences or sensitivity constraints).