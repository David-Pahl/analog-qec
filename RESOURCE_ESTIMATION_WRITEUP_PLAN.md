# Resource Estimation Writeup Plan

This note records the terminology and narrative plan for the resource-estimation
markdown/manuscript section associated with `notebook/05-phenomenological_resource_estimate.ipynb`
and the `analog_qec.phenomenological_resource_estimate` package.

## Coherence Convention

- Use a single observable-sensitive lifetime model for the analog and
  logical-lifetime estimates:
  `$H = n_\mathrm{eff} T_\mathrm{err} / T_2$` and
  `$P_\mathrm{err} = 1 - \exp(-H)$`.
- The default observable task uses `$n_\mathrm{eff}=10$`. Use
  `$n_\mathrm{eff}\approx4$` for energy-density-only sensitivity and
  `$n_\mathrm{eff}=50$` to recover strict register survival. Treat this as an
  internal one-parameter proxy motivated by observable-sensitive simulation
  papers, not as a directly quoted formula from those papers.
- Treat `$T_2$` as the ultimate transverse-coherence limit in all cases. The
  schemes differ in the physical mechanism that sets the effective `$T_2$`, not
  in the failure metric.
- Raw analog: use
  `$1/T_2 = 1/(2T_1) + 1/T_\phi$`. In the regime shown in the figure,
  `$T_\phi \ll 2T_1$`, so `$T_2 \approx T_\phi$`. The plot should therefore
  label raw comparison points by `$T_\phi$`, while the exponent still uses the
  effective `$T_2$`.
- EPS: assume pure dephasing has been removed or strongly suppressed, so the
  remaining coherence limit is relaxation-limited with `$T_2 \le 2T_1$`. The
  nominal EPS case uses `$T_2 = 2T_1$`; plot labels should quote the corresponding
  `$T_1$` while the exponent uses `$T_2$`. If the encoded simulation is a factor
  `$\lambda$` slower, use `$T_\mathrm{EPS}=\lambda T_\mathrm{analog}$` in both
  the time-cost axis and the error exponent
  `$H=n_\mathrm{eff}T_\mathrm{EPS}/T_2$`.
- Surface-code points should be described by their logical lifetime or logical
  `$T_2$` scaling, with labels keyed to code distance. They use the same
  `$n_\mathrm{eff}$` observable-sensitive exponent as Raw and EPS.
- STAR points are controlled by their rotation or gate-error model rather than a
  plotted `$T_2$` sweep. For the plot axis, scale the full STAR
  rotation-plus-Clifford operation exponent by
  `$n_\mathrm{eff}/n_\mathrm{logical}$`, then report the equivalent
  `$T_2$` metadata that reproduces that scaled exponent.

## Figure Language

- Avoid wording that implies raw and EPS use different error metrics. They both
  enter through the same `$T_2$` denominator in `$H$`.
- Avoid wording that implies one local error is assumed to spread instantly
  across the register. The `$n_\mathrm{eff}$` factor is an observable-sensitivity
  proxy, not a microscopic error-spreading model.
- Caption language should say that raw labels quote the dephasing time
  `$T_\phi$` because raw `$T_2$` is dephasing-dominated, whereas EPS labels quote
  `$T_1$` because the effective limit is `$T_2 = 2T_1$`.
- Say that time and space-time costs are task-level costs for a fixed
  observable-estimation problem, while the underlying single-shot values remain
  available as `T_per_shot` and `nT_per_shot`.
- Define the shot multiplier as
  `$N_\mathrm{shots/basis}=\lceil \mathrm{Var}/\epsilon^2\rceil$`. The default
  uses `$ \mathrm{Var}\le 1$`, `$ \epsilon=10^{-2}$`, global X/Y measurement
  bases, and therefore 20,000 total circuit executions.
- When discussing the lower-left direction of the plot, describe it as jointly
  reducing error-proxy probability and task-level space-time overhead.

## Section Outline

1. Define the comparison target and the observable-sensitive error exponent `$H$`.
2. State the shared `$T_2$` convention and distinguish the limiting mechanisms:
   raw is `$T_\phi$`-dominated, EPS is `$T_1$`-dominated with `$T_2 = 2T_1$`.
3. Define the observable task: final XY energy density plus radial transverse
   correlations, estimated from global X and global Y bases with the
   `$ \mathrm{Var}/\epsilon^2$` shot rule.
4. Explain the overhead model for raw analog, EPS, STAR, and surface-code points.
5. Interpret the plotted tradeoff: raw has minimal overhead but poor coherence;
   EPS pays a small overhead to move toward the relaxation limit; surface code
   reaches low failure probability only with large space-time overhead; STAR
   occupies the intermediate regime set by the chosen physical error rates.
