"""Exponent-based resource comparison used by the paper figure notebook."""

from analog_qec.exponent_comparison.config import (
    BenchmarkConfig,
    EPSConfig,
    ExponentComparisonConfig,
    PlotConfig,
    RawConfig,
    STARConfig,
    STARFitConfig,
    SurfaceCodeConfig,
    default_exponent_comparison_config,
    default_plot_config,
)
from analog_qec.exponent_comparison.plotting import (
    apply_plot_style,
    plot_exponent_comparison,
)
from analog_qec.exponent_comparison.schemes import (
    ComparisonPoint,
    build_comparison_points,
)

__all__ = [
    "BenchmarkConfig",
    "ComparisonPoint",
    "EPSConfig",
    "ExponentComparisonConfig",
    "PlotConfig",
    "RawConfig",
    "STARConfig",
    "STARFitConfig",
    "SurfaceCodeConfig",
    "apply_plot_style",
    "build_comparison_points",
    "default_exponent_comparison_config",
    "default_plot_config",
    "plot_exponent_comparison",
]
