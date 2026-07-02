"""Build comparison points for the phenomenological resource-estimate figure."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from analog_qec.phenomenological_resource_estimate.config import (
    PhenomenologicalResourceEstimateConfig,
    default_phenomenological_resource_estimate_config,
)
from analog_qec.phenomenological_resource_estimate.metrics import (
    failure_probability,
    lattice_edge_count,
    overhead,
    register_error_exponent,
    star_clifford_error_per_clock,
    star_compact_physical_qubits,
    star_rotation_count,
    surface_code_T,
    surface_code_Tlogical,
    surface_code_n_memory,
    surface_code_n_overhead,
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

    def as_dict(self) -> Dict[str, Any]:
        point = {
            "scheme": self.scheme,
            "group": self.group,
            "label": self.label,
            "H": self.H,
            "P_fail": self.P_fail,
            "nT": self.nT,
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
    nT: float,
    group: Optional[str] = None,
    **metadata: Any,
) -> ComparisonPoint:
    return ComparisonPoint(
        scheme=scheme,
        group=group or scheme,
        label=label,
        H=H,
        P_fail=failure_probability(H),
        nT=nT,
        metadata=metadata,
    )


def _add_raw_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    comparison_T: float,
) -> None:
    raw = config.raw
    benchmark = config.benchmark
    nT_raw = overhead(raw.space_overhead_factor, benchmark.n_logical) * overhead(
        raw.time_overhead_factor,
        comparison_T,
    )

    for T_phi_raw in raw.T_phi_values_us:
        H_raw = register_error_exponent(
            benchmark.n_logical,
            overhead(raw.time_overhead_factor, comparison_T),
            T_phi_raw,
        )
        points.append(
            _comparison_point(
                "Raw",
                rf"Raw $T_\phi={T_phi_raw:g}\,\mu\mathrm{{s}}$",
                H_raw,
                nT_raw,
            )
        )


def _add_eps_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    comparison_T: float,
) -> None:
    eps = config.eps
    benchmark = config.benchmark

    for T2_eps in eps.T2_values_us:
        H_eps = register_error_exponent(benchmark.n_logical, comparison_T, T2_eps)
        nT_eps = overhead(eps.space_overhead_factor, benchmark.n_logical) * comparison_T
        points.append(
            _comparison_point(
                "EPS",
                f"EPS T1={T2_eps / 2:g}us",
                H_eps,
                nT_eps,
            )
        )


def _add_star_points(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    surface_n_trotter_steps: int,
) -> None:
    benchmark = config.benchmark
    surface = config.surface
    star = config.star
    star_rotation_depth = (
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
                star_rotation_depth,
            )


def _add_star_point(
    points: List[ComparisonPoint],
    config: PhenomenologicalResourceEstimateConfig,
    distance: int,
    p_phys: float,
    star_rotation_depth: int,
) -> None:
    benchmark = config.benchmark
    surface = config.surface
    star = config.star
    n_edges = lattice_edge_count(benchmark.lattice_shape)
    N_rot_star = star_rotation_count(
        benchmark.lattice_shape,
        int(math.ceil(benchmark.Jt / surface.trotter_step_Jt)),
        surface.xy_pauli_rotations_per_edge,
    )
    P_rot_star = 2 * p_phys / 15
    N_rotation_budget_star = 1 / (2 * P_rot_star)
    H_rotation_star = N_rot_star / N_rotation_budget_star
    N_clifford_clock_star = star_rotation_depth
    P_clifford_clock_star = star_clifford_error_per_clock(
        distance,
        p_phys,
        star.clifford_fit,
    )
    H_clifford_star = N_clifford_clock_star * P_clifford_clock_star
    H_star = H_rotation_star + H_clifford_star
    T_depth_star = star_rotation_depth * distance
    n_phys = star_compact_physical_qubits(benchmark.n_logical, distance)
    nT_star = n_phys * T_depth_star

    points.append(
        _comparison_point(
            "STAR",
            f"d={distance}",
            H_star,
            nT_star,
            group=f"STAR p={p_phys:g}",
            d=distance,
            p_phys=p_phys,
            n_logical=benchmark.n_logical,
            n_active_lattice_sites=benchmark.lattice_shape[0] * benchmark.lattice_shape[1],
            lattice_shape=benchmark.lattice_shape,
            n_edges=n_edges,
            n_phys=n_phys,
            N_rot=N_rot_star,
            N_rotation_budget=N_rotation_budget_star,
            H_rotation=H_rotation_star,
            N_clifford_clock=N_clifford_clock_star,
            P_clifford_clock=P_clifford_clock_star,
            H_clifford=H_clifford_star,
            P_rot=P_rot_star,
            rotation_depth=star_rotation_depth,
            T_depth=T_depth_star,
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
                benchmark.n_logical,
                T_surface,
                T2_surface,
            )
            nT_surface = n_surface * T_surface

            if H_surface <= surface.max_H:
                points.append(
                    _comparison_point(
                        "Surface code",
                        f"d={distance}",
                        H_surface,
                        nT_surface,
                        group=f"Surface code Lambda={Lambda_surface}",
                        Lambda=Lambda_surface,
                        d=distance,
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
