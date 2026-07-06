"""Configuration defaults for the phenomenological resource-estimate figure."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class BenchmarkConfig:
    """Shared simulation target for all comparison schemes."""

    n_logical: int = 50
    Jt: float = 20 * 2 * math.pi
    full_rotation_time_us: float = 25e-3
    lattice_shape: Tuple[int, int] = (5, 10)

    @property
    def Jt_time_unit_us(self) -> float:
        return self.full_rotation_time_us / (2 * math.pi)

    @property
    def evolution_time_us(self) -> float:
        return self.Jt * self.Jt_time_unit_us


@dataclass(frozen=True)
class RawConfig:
    """Raw analog comparison assumptions."""

    space_overhead_factor: float = 1
    time_overhead_factor: float = 1
    T_phi_values_us: Tuple[float, ...] = (5, 10, 50)


@dataclass(frozen=True)
class EPSConfig:
    """EPS comparison assumptions."""

    space_overhead_factor: float = 2
    T2_values_us: Tuple[float, ...] = (100, 200, 1_000)


@dataclass(frozen=True)
class SurfaceCodeConfig:
    """Surface-code baseline assumptions."""

    T2_distance_3_us: float = 100
    reference_Lambda: float = 2
    memory_space_overhead_factor: float = 1
    compilation_space_overhead_factor: float = 1
    edge_color_depth: int = 4
    xy_pauli_rotations_per_edge: int = 2
    T_depth_per_arbitrary_rotation: int = 10
    trotter_step_Jt: float = math.pi / 2
    T_factory_patch_equivalents: int = 8
    candidate_distances: Tuple[int, ...] = tuple(range(3, 82, 2))
    Lambda_values: Tuple[int, ...] = (4, 6)
    min_H: float = 1e-3
    max_H: float = -math.log1p(-0.9999999)
    t_cycle: float = 1


@dataclass(frozen=True)
class STARFitConfig:
    """Fitted STAR logical-round coefficients from the reference model."""

    C_Z: float = 0.0679
    p_th_Z: float = 0.00385
    C_X: float = 0.0819
    p_th_X: float = 0.00416


@dataclass(frozen=True)
class STARConfig:
    """STAR partial-FTQC reference assumptions."""

    rotation_latency_clocks: int = 18
    distances: Tuple[int, ...] = (3, 5, 7, 9)
    physical_error_rates: Tuple[float, ...] = (5e-5, 1e-4, 5e-4)
    clifford_fit: STARFitConfig = field(default_factory=STARFitConfig)


@dataclass(frozen=True)
class ObservableTaskConfig:
    """Sampling task layered on top of one simulated time-evolution circuit."""

    enabled: bool = True
    observable_set: str = "final XY energy density and radial transverse correlations"
    measurement_bases: Tuple[str, ...] = ("global X", "global Y")
    target_standard_error: float = 1e-2
    single_shot_variance_bound: float = 1
    shots_per_basis: Optional[int] = None
    include_success_retry_overhead: bool = False

    def __post_init__(self) -> None:
        if len(self.measurement_bases) == 0:
            raise ValueError("measurement_bases must contain at least one basis")
        if self.target_standard_error <= 0:
            raise ValueError("target_standard_error must be positive")
        if self.single_shot_variance_bound < 0:
            raise ValueError("single_shot_variance_bound must be non-negative")
        if self.shots_per_basis is not None and self.shots_per_basis < 1:
            raise ValueError("shots_per_basis must be positive when provided")

    @property
    def computed_shots_per_basis(self) -> int:
        if self.single_shot_variance_bound == 0:
            return 1
        shots = self.single_shot_variance_bound / self.target_standard_error**2
        return max(1, int(math.ceil(shots - 1e-12)))

    @property
    def effective_shots_per_basis(self) -> int:
        return self.shots_per_basis or self.computed_shots_per_basis

    @property
    def total_measurement_shots(self) -> int:
        if not self.enabled:
            return 1
        return len(self.measurement_bases) * self.effective_shots_per_basis

    @property
    def effective_standard_error_bound(self) -> float:
        return math.sqrt(
            self.single_shot_variance_bound / self.effective_shots_per_basis
        )


@dataclass(frozen=True)
class PhenomenologicalResourceEstimateConfig:
    """Complete configuration for building the resource-estimate point set."""

    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    raw: RawConfig = field(default_factory=RawConfig)
    eps: EPSConfig = field(default_factory=EPSConfig)
    surface: SurfaceCodeConfig = field(default_factory=SurfaceCodeConfig)
    star: STARConfig = field(default_factory=STARConfig)
    observable_task: ObservableTaskConfig = field(default_factory=ObservableTaskConfig)


@dataclass(frozen=True)
class PlotConfig:
    """Presentation defaults for the resource-estimate plot."""

    palette: Tuple[str, ...] = (
        "#04CB93",
        "#E79F00",
        "#FE6F93",
        "#0072B3",
        "#C3C3C3",
        "#000000",
    )
    notebook_figure_size: Tuple[float, float] = (10, 6)
    figure_size: Tuple[float, float] = (6.2, 5.0)
    figure_dpi: int = 180
    savefig_dpi: int = 300
    line_width: float = 2.6
    marker_size: float = 10
    xlim: Tuple[float, float] = (-math.log1p(-0.0002), 70)
    ylim: Tuple[float, float] = (2, 5e11)
    annotation_fontsize: int = 8
    raw_color: str = "#000000"
    eps_color: str = "#04CB93"
    raw_marker: str = "^"
    eps_marker: str = "o"
    surface_marker: str = "s"
    star_marker: str = "D"
    surface_colors: Dict[int, str] = field(
        default_factory=lambda: {2: "#0072B3", 4: "#4A90C2", 6: "#8EC1DD"}
    )
    surface_line_styles: Dict[int, str] = field(
        default_factory=lambda: {2: "-", 4: "-", 6: "-"}
    )
    star_colors: Dict[float, str] = field(
        default_factory=lambda: {5e-5: "#F0A15A", 1e-4: "#E6812A", 5e-4: "#D55E00"}
    )
    star_line_styles: Dict[float, str] = field(
        default_factory=lambda: {5e-5: "-.", 1e-4: "-", 5e-4: "--"}
    )
    eps_annotation_offsets: Dict[str, Tuple[int, int]] = field(
        default_factory=lambda: {
            "EPS T1=50us": (-5, -10),
            "EPS T1=100us": (-5, 8),
            "EPS T1=500us": (-10, 8),
        }
    )
    raw_annotation_offsets: Dict[str, Tuple[int, int]] = field(
        default_factory=lambda: {
            r"Raw $T_\phi=5\,\mu\mathrm{s}$": (10, 8),
            r"Raw $T_\phi=10\,\mu\mathrm{s}$": (0, -10),
            r"Raw $T_\phi=50\,\mu\mathrm{s}$": (10, 8),
        }
    )
    lambda_label_distance: int = 3
    star_annotation_offsets: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {3: (5, -2), 5: (5, -2), 7: (5, -2), 9: (5, -2)}
    )
    star_annotation_offsets_by_p: Dict[float, Dict[int, Tuple[int, int]]] = field(
        default_factory=lambda: {
            5e-5: {3: (-5, -2), 5: (-5, -2), 7: (-5, -2), 9: (-5, -0.5)},
            1e-4: {3: (5, -2), 5: (5, -2), 7: (5, -2), 9: (5, -0.5)},
            5e-4: {3: (5, -2), 5: (5, -2), 7: (5, -2), 9: (5, -2)},
        }
    )
    star_p_labels: Dict[float, str] = field(
        default_factory=lambda: {
            5e-5: r"$p=5\times10^{-5}$",
            1e-4: r"$p=10^{-4}$",
            5e-4: r"$p=5\times10^{-4}$",
        }
    )
    star_p_label_offsets: Dict[float, Tuple[int, int]] = field(
        default_factory=lambda: {5e-5: (0, -50), 1e-4: (40, -50), 5e-4: (45, -50)}
    )
    star_p_label_offsets_by_metric: Dict[str, Dict[float, Tuple[int, int]]] = field(
        default_factory=lambda: {
            "space": {5e-5: (0, -64), 1e-4: (40, -64), 5e-4: (45, -64)},
            "time": {5e-5: (0, -24), 1e-4: (40, -24), 5e-4: (45, -24)},
        }
    )
    surface_distance_label_offsets: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {2: (4, 2), 4: (3, 3), 6: (0, -5)}
    )
    surface_distance_label_offsets_by_metric: Dict[
        str, Dict[int, Tuple[int, int]]
    ] = field(
        default_factory=lambda: {
            "space": {2: (4, 2), 4: (3, 3), 6: (0, -5)},
            "time": {2: (4, 1), 4: (4, 4), 6: (0, -5)},
        }
    )
    label_bbox: Dict[str, object] = field(
        default_factory=lambda: {
            "facecolor": "white",
            "edgecolor": "none",
            "alpha": 0.72,
            "pad": 0.15,
        }
    )
    lambda_label_offsets: Dict[int, Tuple[int, int]] = field(
        default_factory=lambda: {2: (30, 0), 4: (30, 1), 6: (30, 5)}
    )
    lambda_label_offsets_by_metric: Dict[str, Dict[int, Tuple[int, int]]] = field(
        default_factory=lambda: {
            "space": {2: (30, 0), 4: (30, 1), 6: (30, 5)},
            "time": {2: (30, 0), 4: (30, 7), 6: (30, 3)},
        }
    )
    top_axis_failure_ticks: Tuple[float, ...] = (1e-3, 1e-2, 1e-1, 0.5, 0.9, 0.99)


def default_phenomenological_resource_estimate_config() -> PhenomenologicalResourceEstimateConfig:
    """Return a fresh copy of the paper-figure resource-estimate defaults."""

    return PhenomenologicalResourceEstimateConfig()


def default_plot_config() -> PlotConfig:
    """Return a fresh copy of the paper-figure plotting defaults."""

    return PlotConfig()
