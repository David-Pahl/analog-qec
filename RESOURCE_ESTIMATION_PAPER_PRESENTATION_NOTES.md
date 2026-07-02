# Paper Presentation Notes for the Resource-Estimation Figure

This note records a paper-facing strategy for presenting the
phenomenological resource-estimation plot. It is intentionally separate from
`RESOURCE_CALCULATION_AUDIT.md`: the audit is the calculation ledger, while this
file is a memory aid for manuscript framing, robustness, and reviewer defense.

## Core Framing

The plot should not be presented as a neutral best-estimate resource estimator.
It should be presented as an adversarial, competitor-favorable comparison:

> We deliberately give STAR and surface-code baselines optimistic assumptions.
> If EPS remains in a favorable resource-error regime even under those
> assumptions, the conclusion is not an artifact of pessimistic encoded-baseline
> modeling.

This framing is important because many surface-code and STAR constants are
phenomenological or optimistic. The figure is strongest when the paper is clear
that these choices are intentional and conservative from the perspective of the
EPS claim.

## Placement in the Paper

Put the single-column resource-estimation plot in a short section immediately
before the conclusion and after the simulation results have established that EPS
can reach the relaxation-limited regime:

```text
Simulation results -> EPS reaches T2 = 2T1 -> resource-estimation comparison
-> conclusion
```

The section should be compact. Its job is to translate the simulation result
into a systems-level implication, not to reproduce the full calculation ledger.
Detailed calculations, assumptions, and sensitivity analysis should go in an
appendix or Supplementary Information.

## Main-Text Claim

Use a claim with this shape:

> Having established that EPS can suppress dephasing to approach the
> relaxation-limited lifetime, we compare the resulting coherence-limited
> register exponent against deliberately optimistic STAR and surface-code
> baselines. Across the plotted regimes, EPS occupies a favorable region of
> low observable-estimation space-time cost and low cumulative register-failure
> exponent.

Avoid stronger claims such as:

- "EPS outperforms surface code."
- "This is a complete resource estimate."
- "STAR/surface-code estimates are realistic central estimates."
- "The plot proves scalability."

Prefer:

- "phenomenological comparison"
- "competitor-favorable encoded baselines"
- "optimistic STAR and surface-code assumptions"
- "favorable EPS regime"
- "resource-error regime"
- "sensitivity analysis in the appendix"

## What the Main Text Should Explain

The main text should explain only the minimum needed to read the plot:

1. The x-axis is the cumulative register error exponent
   `H = n_logical T_arch / T2_limit`, with `P_fail = 1-exp(-H)`.
2. The y-axis is task-level physical-qubit-time, `nT`, after multiplying the
   single-shot circuit time by the observable-estimation shot count.
3. The default task estimates final XY energy density and radial transverse
   correlations from global X and global Y measurement bases.
4. The shot count is `ceil(Var/epsilon^2)` per basis, using `Var<=1` and
   `epsilon=1e-2`, for 10,000 shots per basis and 20,000 total shots.
5. Raw and EPS use the analog evolution time directly.
6. EPS uses the simulation-motivated relaxation-limited regime
   `T2 = 2T1`.
7. STAR and surface-code depths are converted to microseconds using a QEC cycle
   time.
8. The encoded baselines intentionally use optimistic assumptions.

Do not overload the main text with every constant. One or two representative
examples are enough; the appendix should carry the full table.

## Single-Column Plot Guidance

The single-column figure should visually support the intended claim:

- Keep the top axis mapping `H` to `P_fail`, because it makes the exponent
  interpretable.
- Keep EPS visually simple and readable.
- Label STAR and surface-code curves clearly as optimistic baselines or explain
  that in the caption.
- Avoid visual language that implies all schemes are equally mature or equally
  complete resource estimates.
- Consider using a caption phrase such as "phenomenological,
  competitor-favorable comparison."

Suggested caption skeleton:

> Phenomenological resource-error comparison for a 50-logical-qubit analog
> benchmark. The horizontal axis gives the cumulative register-failure exponent
> `H`, with the corresponding failure probability shown on the top axis; the
> vertical axis gives the task-level physical-qubit-time cost to estimate final
> XY energy density and transverse correlations using the stated shot model. EPS
> points use the relaxation-limited coherence regime established in the
> preceding simulations. STAR and surface-code baselines are evaluated with
> optimistic, competitor-favorable assumptions; full assumptions and sensitivity
> sweeps are reported in Appendix X.

## Appendix/Supplement Structure

Add an appendix section with approximately this structure:

### A. Resource-Estimate Definitions

- Define `H`, `P_fail`, `nT`, `T_arch`, and `T2_limit`.
- Define the observable-estimation shot multiplier
  `N_shots/basis=ceil(Var/epsilon^2)` and distinguish single-shot
  `T_arch`/`nT` from task-level `T`/`nT`.
- State that `T2_limit` is a physical coherence convention for Raw/EPS and an
  effective logical limiting lifetime for encoded schemes.
- Explain that STAR and surface code use the same register-exponent axis, but
  reach `T2_limit` differently:
  - Surface code starts from an assumed logical-lifetime scaling and computes
    `H`.
  - STAR starts from a rotation-plus-Clifford operation-error budget and
    back-solves the equivalent `T2_limit`.

### B. Architecture-Specific Calculations

- Raw: `T2 ~= T_phi` in the dephasing-dominated limit.
- EPS: `T2 = 2T1` after dephasing suppression.
- STAR: total analog rotations, STAR clock depth, 18-clock analog-rotation
  injection/RUS latency, `d` QEC rounds per clock, compact patch count, and
  rotation/Clifford error budget.
- Surface code: Trotter steps, T depth/count, factory area, memory area,
  logical-lifetime scaling, and QEC-cycle conversion.
- Observable task: final XY energy density and radial transverse correlations;
  global X/Y bases; `Var<=1`, `epsilon=1e-2`, 20,000 total shots.

This appendix can be based directly on `RESOURCE_CALCULATION_AUDIT.md`.

### C. Assumption Directionality

Include a table that states whether each assumption favors EPS, STAR, or
surface code. This is the central robustness argument.

| Assumption | Direction |
| --- | --- |
| Surface `Lambda=4,6` | Favors surface code over EPS |
| Surface no routing/layout overhead | Favors surface code |
| Surface small factory-area constant | Favors surface code |
| Surface memory-lifetime model without full operation-failure accounting | Favors surface code |
| Light two-basis XY observable task | Favors all schemes relative to heavier diagnostics |
| STAR compact block and ideal schedule | Favors STAR |
| STAR no routing/idle/scheduling penalty beyond the modeled clocks | Favors STAR |
| EPS `T2=2T1` | Favors EPS, but is justified by preceding simulations |
| EPS no analog control-error budget | Favors EPS; should be acknowledged |

The conclusion should emphasize that encoded baselines are intentionally
strengthened. EPS assumptions that favor EPS should be tied directly to the
simulation results, not left as free optimism.

### D. Sensitivity Analysis

Include sensitivity plots or tables for the parameters most likely to move the
conclusion:

- Surface-code `Lambda`: include measured-scale values near `2.14`, plus
  optimistic `4` and `6`.
- QEC cycle time: e.g. `0.5 us`, `1 us`, `2 us`.
- Surface factory area: vary `T_factory_patch_equivalents`.
- Surface arbitrary-rotation cost: vary `T_depth_per_arbitrary_rotation`.
- STAR physical error rate and distance.
- STAR schedule overhead: vary an additional multiplicative scheduling factor.
- EPS lifetime: vary `T1` and include a degraded case below `T2=2T1`.
- Optional EPS control-error term: show how large an analog-control error budget
  would have to be to erase the favorable regime.
- Shot/observable task: vary `epsilon`, `Var`, and the observable set,
  especially if adding heavier 69-qubit XY-magnet diagnostics such as entropy,
  vortex correlators, vorticity, or transport.

The most convincing appendix plot would be a small grid showing that EPS
remains favorable when STAR/surface-code assumptions are pushed optimistically
and EPS assumptions are degraded modestly.

### E. Reviewer-Defense Paragraph

Add a paragraph with this logic:

> These estimates are not intended as complete architecture-level resource
> counts. Instead, they test whether the EPS regime identified by simulation is
> plausibly competitive against deliberately optimistic encoded baselines. The
> surface-code and STAR assumptions are chosen to strengthen the alternative
> encoded strategies rather than to penalize them. The persistence of the EPS
> region under these assumptions supports the qualitative claim that
> dephasing-protected analog evolution can occupy a favorable intermediate
> resource regime.

## Reviewer Risks to Preempt

Preempt these attacks explicitly:

- The encoded-baseline estimates are incomplete.
  - Response: yes; they are intentionally optimistic and used as
    competitor-favorable baselines, not central estimates.
- Surface-code `Lambda=4,6` is extrapolated.
  - Response: yes; this strengthens surface code relative to current measured
    values.
- STAR timing includes `d` rounds despite analog rotations.
  - Response: STAR avoids magic-state factories, but consuming the rotation
    resource still requires an encoded injection/RUS operation with
    lattice-surgery timing.
- EPS ignores analog control errors.
  - Response: acknowledge this and include a sensitivity threshold for how large
    those errors would need to be to change the conclusion.
- Observable/shot model is too light.
  - Response: yes; the default is a simple energy/correlation task motivated by
    the 69-qubit XY-magnet literature, not the full cost of entropy, vorticity,
    or transport diagnostics. Include shot/observable sensitivity in the
    appendix.
- `T2_limit` is not the same microscopic object in every scheme.
  - Response: define it as the limiting lifetime in the common register-exponent
    model; for encoded schemes it is an effective logical lifetime.

## Recommended Manuscript Wording

Possible section title:

```text
Resource-error comparison under optimistic encoded baselines
```

Possible opening:

> The preceding simulations show that EPS can suppress dephasing and approach
> the relaxation-limited coherence time `T2=2T1`. We next ask whether this
> coherence gain survives a systems-level comparison against encoded
> alternatives. To avoid overstating the EPS advantage, we use optimistic
> assumptions for the STAR and surface-code baselines and report the resulting
> cumulative register-failure exponent versus the physical-qubit-time cost of a
> fixed observable-estimation task.

Possible closing:

> The comparison is therefore intentionally conservative with respect to the
> EPS claim: the encoded baselines are strengthened by optimistic logical
> suppression factors, compact factory assumptions, and minimal routing
> overheads. The observable task is deliberately simple: final XY energy density
> and transverse correlations estimated from two global measurement bases. EPS
> nevertheless remains in a low-overhead, low-exponent region, suggesting that
> relaxation-limited analog evolution can provide a favorable operating regime
> before full fault-tolerant resource costs become practical.

## Action Items Before Submission

- Add the assumption-directionality table to the appendix.
- Add at least one sensitivity plot for surface-code `Lambda`.
- Add at least one sensitivity plot or threshold calculation for EPS analog
  control error.
- Add shot-count and observable-set sensitivity, including heavier 69-qubit
  XY-magnet diagnostics such as entropy, vortex correlators, and transport.
- Make the single-column caption explicitly say "optimistic encoded baselines."
- Ensure the conclusion says "favorable regime" rather than "architecture-level
  advantage" unless the appendix sensitivity analysis is strong enough to
  support the latter.
