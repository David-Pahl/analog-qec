"""Build comparison points for the phenomenological resource-estimate figure."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from analog_qec.phenomenological_resource_estimate.config import (
    ObservableTaskConfig,
    PhenomenologicalResourceEstimateConfig,
    default_phenomenological_resource_estimate_config,
)
from analog_qec.phenomenological_resource_estimate.metrics import (
    crosstalk_angle,
    crosstalk_error_exponent,
    failure_probability,
    lattice_edge_count,
    overhead,
    register_error_exponent,
    star_clifford_error_per_clock,
    star_compact_physical_qubits,
    star_rotation_count,
    success_retry_multiplier,
    surface_code_T,
    surface_code_Tlogical,
    surface_code_n_memory,
    surface_code_n_overhead,
    twirled_gaussian_envelope_error,
)


@dataclass(frozen=True)
class ComparisonPoint:
    """One plotted point in the resource estimate."""

    scheme: str
    group: str
    label: str
    H: float
    P_fail: float
    nT: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    n: Optional[float] = None
    T: Optional[float] = None
    nT_per_shot: Optional[float] = None
    T_per_shot: Optional[float] = None
    task_repetitions: float = 1

    @property
    def P_err(self) -> float:
        return self.P_fail

    def as_dict(self) -> Dict[str, Any]:
        point = {
            "scheme": self.scheme,
            "group": self.group,
            "label": self.label,
            "H": self.H,
            "P_err": self.P_err,
            "P_fail": self.P_fail,
            "nT": self.nT,
            "n": self.n,
            "T": self.T,
            "nT_per_shot": self.nT_per_shot,
            "T_per_shot": self.T_per_shot,
            "task_repetitions": self.task_repetitions,
        }
        point.update(self.metadata)
        return point


def build_comparison_points(
    config: Optional[PhenomenologicalResourceEstimateConfig] = None,
) -> List[ComparisonPoint]:
    """Build raw, EPS, STAR, and surface-code points in plot order."""

    config = config or default_phenomenological_resource_estimate_config()
    points: List[ComparisonPoint] = []

    benchmark = config.benchmark
    surface = config.surface

    comparison_T = benchmark.evolution_time_us
    surface_n_trotter_steps = int(math.ceil(benchmark.Jt / surface.trotter_step_Jt))
    surface_n_edges = lattice_edge_count(benchmark.lattice_shape)
    surface_T_depth = (
        surface_n_trotter_steps
        * surface.edge_color_depth
        * surface.xy_pauli_rotations_per_edge
        * surface.T_depth_per_arbitrary_rotation
    )
    surface_T_count = (
        surface_n_trotter_steps
        * surface_n_edges
        * surface.xy_pauli_rotations_per_edge
        * surface.T_depth_per_arbitrary_rotation
    )
    surface_parallel_T_demand = int(math.ceil(surface_T_count / surface_T_depth))

    _add_raw_points(points, config, comparison_T)
    _add_eps_points(points, config, comparison_T)
    _add_star_points(points, config, surface_n_trotter_steps)
    _add_surface_code_points(
        points,
        config,
        surface_T_depth,
        surface_T_count,
        surface_parallel_T_demand,
    )

    return points


def _comparison_point(
    scheme: str,
    label: str,
    H: float,
    n: float,
    T: float,
    task: ObservableTaskConfig,
    group: Optional[str] = None,
    **metadata: Any,
) -> ComparisonPoint:
    task_repetitions = _task_repetitions(task, H)
    T_task = T * task_repetitions
    nT_per_shot = n * T
    nT_task = n * T_task
    metadata.update(
        observable_task_enabled=task.enabled,
        observable_task=task.observable_set,
        measurement_bases=task.measurement_bases,
        n_measurement_bases=len(task.measurement_bases),
        error_sensitivity_qubits=task.error_sensitivity_qubits,
        target_standard_error=task.target_standard_error,
        single_shot_variance_bound=task.single_shot_variance_bound,
        effective_standard_error_bound=task.effective_standard_error_bound,
        shots_per_basis=task.effective_shots_per_basis,
        computed_shots_per_basis=task.computed_shots_per_basis,
        total_measurement_shots=task.total_measurement_shots,
        include_success_retry_overhead=task.include_success_retry_overhead,
        success_retry_multiplier=(
            success_retry_multiplier(H) if task.include_success_retry_overhead else 1
        ),
    )
    return ComparisonPoint(
        scheme=scheme,
        group=group or scheme,
        label=label,
        H=H,
        P_fail=failure_probability(H),
        nT=nT_task,
        n=n,
        T=T_task,
        nT_per_shot=nT_per_shot,
        T_per_shot=T,
        task_repetitions=task_repetitions,
        metadata=metadata,
    )


def _task_repetitions(task: ObservableTaskConfig, H: float) -> float:
    if not task.enabled:
        return 1

    repetitions = float(task.total_measurement_shots)
    if task.include_success_retry_overhead:
        repetitions *= success_retry_multiplier(H)
    return repetitions


def _error_sensitivity_qubits(
    config: PhenomenologicalResourceEstimateConfig,
) -> float:
    return config.observable_task.error_sensitivity_qubits


def _crosstalk_sensitivity_factor(
    config: PhenomenologicalResourceEstimateConfig,
) -> float:
    return (
        config.crosstalk.sensitivity_factor
        if config.crosstalk.sensitivity_factor is not None
        else _error_sensitivity_qubits(config)
    )


def _crosstalk_terms(
    config: PhenomenologicalResourceEstimateConfig,
    T_arch: float,
    control_scale_factor: float,
    eps_suppression_factor: Optional[float] = None,
) -> Dict[str, Any]:
    crosstalk = config.crosstalk
    sensitivity_factor = _crosstalk_sensitivity_factor(config)
    suppression_factor = (
        1.0 if eps_suppression_factor is None else eps_suppression_factor
    )
    metadata: Dict[str, Any] = {
        "H_crosstalk": 0.0,
        "xtalk_theta_static_rad": 0.0,
        "xtalk_theta_drive_rad": 0.0,
        "xtalk_theta_rad": 0.0,
        "xtalk_p_proxy": 0.0,
        "xtalk_static_ratio": crosstalk.static_crosstalk_ratio,
        "xtalk_drive_ratio_at_unit_scale": (
            crosstalk.drive_induced_crosstalk_ratio_at_unit_scale
        ),
        "xtalk_sensitivity_factor": sensitivity_factor,
        "xtalk_eps_suppression_factor": eps_suppression_factor or 0.0,
        "xtalk_model": "disabled",
    }
    if not crosstalk.enabled:
        return metadata

    theta_static = crosstalk_angle(
        crosstalk.static_crosstalk_ratio,
        T_arch,
        config.benchmark.full_rotation_time_us,
    )
    theta_drive = crosstalk_angle(
        crosstalk.drive_induced_crosstalk_ratio_at_unit_scale
        * control_scale_factor,
        T_arch,
        config.benchmark.full_rotation_time_us,
    )
    theta_total = suppression_factor * math.hypot(theta_static, theta_drive)
    p_xtalk = twirled_gaussian_envelope_error(theta_total)
    H_crosstalk = crosstalk_error_exponent(sensitivity_factor, theta_total)

    metadata.update(
        H_crosstalk=H_crosstalk,
        xtalk_theta_static_rad=suppression_factor * theta_static,
        xtalk_theta_drive_rad=suppression_factor * theta_drive,
        xtalk_theta_rad=theta_total,
        xtalk_p_proxy=p_xtalk,
        xtalk_model="twirled Gaussian angle envelope",
    )
    return metadata


def _add_raw_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    comparison_T: float,
) -> None:
    raw = config.raw
    benchmark = config.benchmark
    n_error = _error_sensitivity_qubits(config)
    n_raw = overhead(raw.space_overhead_factor, benchmark.n_logical)
    T_raw = overhead(raw.time_overhead_factor, comparison_T)
    raw_control_scale_factor = (
        config.crosstalk.raw_control_scale_factor
        if config.crosstalk.raw_control_scale_factor is not None
        else 1 / raw.time_overhead_factor
    )
    crosstalk_metadata = _crosstalk_terms(
        config,
        T_raw,
        raw_control_scale_factor,
    )

    for T_phi_raw in raw.T_phi_values_us:
        H_coherence = register_error_exponent(
            n_error,
            T_raw,
            T_phi_raw,
        )
        H_raw = H_coherence + crosstalk_metadata["H_crosstalk"]
        points.append(
            _comparison_point(
                "Raw",
                rf"Raw $T_\phi={T_phi_raw:g}\,\mu\mathrm{{s}}$",
                H_raw,
                n_raw,
                T_raw,
                config.observable_task,
                n_logical=benchmark.n_logical,
                n_error=n_error,
                error_exponent_model="observable lifetime sensitivity",
                H_coherence=H_coherence,
                raw_control_scale_factor=raw_control_scale_factor,
                T_arch=T_raw,
                T_arch_units="us",
                **crosstalk_metadata,
            )
        )


def _add_eps_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    comparison_T: float,
) -> None:
    eps = config.eps
    benchmark = config.benchmark
    n_error = _error_sensitivity_qubits(config)
    n_eps = overhead(eps.space_overhead_factor, benchmark.n_logical)
    lambda_values = eps.lambda_values or (eps.time_overhead_factor,)
    lambda_sweep_enabled = bool(eps.lambda_values)

    include_dephasing_T_phi_in_label = _eps_include_dephasing_T_phi_in_label(config)

    for T2_index, T2_eps in enumerate(eps.T2_values_us):
        T1_eps = T2_eps / 2
        dephasing_T_phi_us = _eps_dephasing_T_phi_us(config, T2_index)
        label = _eps_label(
            T1_eps,
            dephasing_T_phi_us,
            include_dephasing_T_phi_in_label,
        )
        group = label if lambda_sweep_enabled else "EPS"
        for lambda_eps in lambda_values:
            time_overhead_factor = (
                1 + lambda_eps if lambda_sweep_enabled else lambda_eps
            )
            T_eps = overhead(time_overhead_factor, comparison_T)
            eps_suppression_factor = _eps_crosstalk_suppression_factor(
                config,
                lambda_eps,
            )
            crosstalk_metadata = _crosstalk_terms(
                config,
                T_eps,
                config.crosstalk.eps_control_scale_factor,
                eps_suppression_factor,
            )
            coherence_metadata = _eps_coherence_terms(
                config,
                n_error,
                T_eps,
                T2_eps,
                dephasing_T_phi_us,
                _eps_dephasing_suppression_factor(config, lambda_eps),
            )
            H_coherence = coherence_metadata["H_coherence"]
            H_eps = H_coherence + crosstalk_metadata["H_crosstalk"]
            points.append(
                _comparison_point(
                    "EPS",
                    label,
                    H_eps,
                    n_eps,
                    T_eps,
                    config.observable_task,
                    group=group,
                    n_logical=benchmark.n_logical,
                    n_error=n_error,
                    error_exponent_model="observable lifetime sensitivity",
                    space_overhead_factor=eps.space_overhead_factor,
                    time_overhead_factor=time_overhead_factor,
                    lambda_eps=lambda_eps,
                    eps_time_overhead_factor=time_overhead_factor,
                    eps_lambda_time_overhead_offset=(1 if lambda_sweep_enabled else 0),
                    eps_lambda_sweep=lambda_sweep_enabled,
                    eps_control_scale_factor=(
                        config.crosstalk.eps_control_scale_factor
                    ),
                    T_arch=T_eps,
                    T_arch_units="us",
                    T1_limit=T1_eps,
                    T1_limit_units="us",
                    T2_limit_units="us",
                    **coherence_metadata,
                    **crosstalk_metadata,
                )
            )


def _eps_crosstalk_suppression_factor(
    config: PhenomenologicalResourceEstimateConfig,
    lambda_eps: float,
) -> float:
    suppression_by_lambda = config.crosstalk.eps_suppression_factor_by_lambda
    if lambda_eps in suppression_by_lambda:
        return suppression_by_lambda[lambda_eps]
    for configured_lambda, suppression_factor in suppression_by_lambda.items():
        if math.isclose(configured_lambda, lambda_eps, rel_tol=0.0, abs_tol=1e-12):
            return suppression_factor
    return config.crosstalk.eps_suppression_factor


def _eps_dephasing_suppression_factor(
    config: PhenomenologicalResourceEstimateConfig,
    lambda_eps: float,
) -> float:
    suppression_by_lambda = config.eps.dephasing_suppression_factor_by_lambda
    if lambda_eps in suppression_by_lambda:
        return suppression_by_lambda[lambda_eps]
    for configured_lambda, suppression_factor in suppression_by_lambda.items():
        if math.isclose(configured_lambda, lambda_eps, rel_tol=0.0, abs_tol=1e-12):
            return suppression_factor
    return config.eps.dephasing_suppression_factor


def _eps_dephasing_T_phi_us(
    config: PhenomenologicalResourceEstimateConfig,
    T2_index: int,
) -> Optional[float]:
    dephasing_T_phi_us = config.eps.dephasing_T_phi_us
    if dephasing_T_phi_us is None:
        return None
    if isinstance(dephasing_T_phi_us, (list, tuple)):
        if len(dephasing_T_phi_us) == 1:
            return float(dephasing_T_phi_us[0])
        return float(dephasing_T_phi_us[T2_index])
    return float(dephasing_T_phi_us)


def _eps_include_dephasing_T_phi_in_label(
    config: PhenomenologicalResourceEstimateConfig,
) -> bool:
    dephasing_T_phi_us = config.eps.dephasing_T_phi_us
    if not isinstance(dephasing_T_phi_us, (list, tuple)):
        return False
    return len({float(T_phi_us) for T_phi_us in dephasing_T_phi_us}) > 1


def _eps_label(
    T1_eps: float,
    dephasing_T_phi_us: Optional[float],
    include_dephasing_T_phi: bool,
) -> str:
    label = f"EPS T1={T1_eps:g}us"
    if include_dephasing_T_phi and dephasing_T_phi_us is not None:
        label = f"{label}, Tφ={dephasing_T_phi_us:g}us"
    return label


def _eps_coherence_terms(
    config: PhenomenologicalResourceEstimateConfig,
    n_error: float,
    T_arch: float,
    T2_relaxation_limit: float,
    dephasing_T_phi_us: Optional[float],
    dephasing_suppression_factor: float,
) -> Dict[str, Any]:
    relaxation_rate = 1 / T2_relaxation_limit
    dephasing_rate = 0.0
    dephasing_model = "disabled"

    if dephasing_T_phi_us is not None and dephasing_suppression_factor > 0:
        dephasing_rate = dephasing_suppression_factor / dephasing_T_phi_us
        dephasing_model = "suppressed pure-dephasing rate"

    total_rate = relaxation_rate + dephasing_rate
    T2_effective_limit = 1 / total_rate
    H_relaxation = n_error * T_arch * relaxation_rate
    H_dephasing = n_error * T_arch * dephasing_rate
    H_coherence = H_relaxation + H_dephasing

    return {
        "H_coherence": H_coherence,
        "H_relaxation": H_relaxation,
        "H_dephasing": H_dephasing,
        "T2_limit": T2_effective_limit,
        "T2_effective_limit": T2_effective_limit,
        "T2_relaxation_limit": T2_relaxation_limit,
        "eps_dephasing_T_phi_us": dephasing_T_phi_us,
        "eps_dephasing_suppression_factor": dephasing_suppression_factor,
        "eps_dephasing_rate_per_us": dephasing_rate,
        "eps_relaxation_rate_per_us": relaxation_rate,
        "eps_coherence_model": dephasing_model,
    }


def _add_star_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    surface_n_trotter_steps: int,
) -> None:
    benchmark = config.benchmark
    surface = config.surface
    star = config.star
    star_rotation_depth_clocks = (
        surface_n_trotter_steps
        * surface.edge_color_depth
        * surface.xy_pauli_rotations_per_edge
        * star.rotation_latency_clocks
    )

    for p_phys in star.physical_error_rates:
        for distance in star.distances:
            _add_star_point(
                points,
                config,
                distance,
                p_phys,
                star_rotation_depth_clocks,
            )


def _add_star_point(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    distance: int,
    p_phys: float,
    star_rotation_depth_clocks: int,
) -> None:
    benchmark = config.benchmark
    surface = config.surface
    star = config.star
    n_error = _error_sensitivity_qubits(config)
    n_edges = lattice_edge_count(benchmark.lattice_shape)
    N_rot_star = star_rotation_count(
        benchmark.lattice_shape,
        int(math.ceil(benchmark.Jt / surface.trotter_step_Jt)),
        surface.xy_pauli_rotations_per_edge,
    )
    P_rot_star = 2 * p_phys / 15
    N_rotation_budget_star = 1 / (2 * P_rot_star)
    H_rotation_star_full = N_rot_star / N_rotation_budget_star
    N_clifford_clock_star = star_rotation_depth_clocks
    P_clifford_clock_star = star_clifford_error_per_clock(
        distance,
        p_phys,
        star.clifford_fit,
    )
    H_clifford_star_full = N_clifford_clock_star * P_clifford_clock_star
    observable_sensitivity_factor = n_error / benchmark.n_logical
    H_rotation_star = H_rotation_star_full * observable_sensitivity_factor
    H_clifford_star = H_clifford_star_full * observable_sensitivity_factor
    H_star = H_rotation_star + H_clifford_star
    T_arch_star = star_rotation_depth_clocks * distance * surface.t_cycle
    T2_limit_star = n_error * T_arch_star / H_star
    n_phys = star_compact_physical_qubits(benchmark.n_logical, distance)

    points.append(
        _comparison_point(
            "STAR",
            f"d={distance}",
            H_star,
            n_phys,
            T_arch_star,
            config.observable_task,
            group=f"STAR p={p_phys:g}",
            d=distance,
            p_phys=p_phys,
            n_logical=benchmark.n_logical,
            n_error=n_error,
            error_exponent_model="STAR operation-error model",
            T_arch=T_arch_star,
            T2_limit=T2_limit_star,
            T_arch_units="us",
            T2_limit_units="us",
            limiting_lifetime_model="equivalent STAR operation-error lifetime",
            n_active_lattice_sites=benchmark.lattice_shape[0] * benchmark.lattice_shape[1],
            lattice_shape=benchmark.lattice_shape,
            n_edges=n_edges,
            n_phys=n_phys,
            N_rot=N_rot_star,
            N_rotation_budget=N_rotation_budget_star,
            observable_sensitivity_factor=observable_sensitivity_factor,
            H_rotation=H_rotation_star,
            H_rotation_full_register=H_rotation_star_full,
            N_clifford_clock=N_clifford_clock_star,
            P_clifford_clock=P_clifford_clock_star,
            H_clifford=H_clifford_star,
            H_clifford_full_register=H_clifford_star_full,
            H_full_register=H_rotation_star_full + H_clifford_star_full,
            P_rot=P_rot_star,
            rotation_depth=star_rotation_depth_clocks,
            rotation_depth_clocks=star_rotation_depth_clocks,
            t_cycle_us=surface.t_cycle,
            T_arch_star_us=T_arch_star,
            T_depth=T_arch_star,
        )
    )


def _add_surface_code_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    surface_T_depth: int,
    surface_T_count: int,
    surface_parallel_T_demand: int,
) -> None:
    benchmark = config.benchmark
    surface = config.surface
    n_error = _error_sensitivity_qubits(config)

    def optimistic_T_factory_area(distance: int) -> float:
        return (
            surface_parallel_T_demand
            * surface.T_factory_patch_equivalents
            * surface_code_n_memory(distance)
        )

    for Lambda_surface in surface.Lambda_values:
        for distance in _surface_distances_for_Lambda(
            surface.candidate_distances,
            Lambda_surface,
        ):
            T_surface = surface_code_T(surface_T_depth, distance, surface.t_cycle)
            T2_surface = surface_code_Tlogical(
                distance,
                Lambda_surface,
                surface.T2_distance_3_us,
                surface.reference_Lambda,
            )
            n_surface_memory = (
                surface_code_n_overhead(
                    distance,
                    surface.memory_space_overhead_factor,
                    surface.compilation_space_overhead_factor,
                )
                * benchmark.n_logical
            )
            n_surface_factory = optimistic_T_factory_area(distance)
            n_surface = n_surface_memory + n_surface_factory
            H_surface = register_error_exponent(
                n_error,
                T_surface,
                T2_surface,
            )

            if H_surface <= surface.max_H:
                points.append(
                    _comparison_point(
                        "Surface code",
                        f"d={distance}",
                        H_surface,
                        n_surface,
                        T_surface,
                        config.observable_task,
                        group=f"Surface code Lambda={Lambda_surface}",
                        Lambda=Lambda_surface,
                        d=distance,
                        n_logical=benchmark.n_logical,
                        n_error=n_error,
                        error_exponent_model="observable lifetime sensitivity",
                        n_memory=n_surface_memory,
                        n_factory=n_surface_factory,
                        T_depth=surface_T_depth,
                        T_count=surface_T_count,
                    )
                )
            if H_surface <= surface.min_H:
                break


def _surface_distances_for_Lambda(
    candidate_distances: Iterable[int],
    Lambda_surface: int,
) -> Iterable[int]:
    return (
        distance
        for distance in candidate_distances
        if Lambda_surface != 2 or (distance - 3) % 4 == 0
    )
