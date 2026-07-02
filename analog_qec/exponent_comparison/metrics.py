"""Pure formulas for the exponent-based resource comparison."""

from __future__ import annotations

import math
from typing import Tuple

from analog_qec.exponent_comparison.config import STARFitConfig


def register_error_exponent(n_logical: float, T_arch: float, T2_limit: float) -> float:
    return n_logical * T_arch / T2_limit


def failure_probability(H: float) -> float:
    return 1 - math.exp(-H)


def overhead(multiplier: float, value: float) -> float:
    return multiplier * value


def surface_code_n_memory(distance: int) -> int:
    return 2 * distance**2 - 1


def surface_code_n_overhead(
    distance: int,
    memory_space_overhead_factor: float = 1,
    compilation_space_overhead_factor: float = 1,
) -> float:
    return (
        surface_code_n_memory(distance)
        * memory_space_overhead_factor
        * compilation_space_overhead_factor
    )


def surface_code_T(T_gate_count: float, distance: int, t_cycle: float) -> float:
    return T_gate_count * distance * t_cycle


def surface_code_Tlogical(
    distance: int,
    Lambda: float,
    Tlogical_3: float,
    reference_Lambda: float = 2,
) -> float:
    Tlogical_3_for_Lambda = Tlogical_3 * (Lambda / reference_Lambda) ** 2
    return Tlogical_3_for_Lambda * Lambda ** ((distance - 3) / 2)


def lattice_edge_count(lattice_shape: Tuple[int, int]) -> int:
    n_rows, n_cols = lattice_shape
    return n_rows * (n_cols - 1) + n_cols * (n_rows - 1)


def star_rotation_count(
    lattice_shape: Tuple[int, int],
    n_trotter_steps: int,
    xy_pauli_rotations_per_edge: int,
) -> int:
    return n_trotter_steps * lattice_edge_count(lattice_shape) * xy_pauli_rotations_per_edge


def star_compact_physical_qubits(n_logical: int, distance: int) -> float:
    return (1.5 * n_logical + 5) * 2 * distance**2


def star_clifford_error_per_clock(
    distance: int,
    p_phys: float,
    fit: STARFitConfig,
) -> float:
    exponent = (distance + 1) / 2
    P_Z = fit.C_Z * (p_phys / fit.p_th_Z) ** exponent
    P_X = fit.C_X * (p_phys / fit.p_th_X) ** exponent
    return P_Z + P_X
