"""Phenomenological resource estimate used by the paper figure notebook."""

from analog_qec.phenomenological_resource_estimate.config import (
    BenchmarkConfig,
    CrosstalkConfig,
    EPSConfig,
    ObservableTaskConfig,
    PhenomenologicalResourceEstimateConfig,
    PlotConfig,
    RawConfig,
    STARConfig,
    STARFitConfig,
    SurfaceCodeConfig,
    default_phenomenological_resource_estimate_config,
    default_plot_config,
)
from analog_qec.phenomenological_resource_estimate.metrics import (
    crosstalk_angle,
    crosstalk_error_exponent,
    nominal_coupling_angular_frequency,
    twirled_gaussian_envelope_error,
)
from analog_qec.phenomenological_resource_estimate.plotting import (
    apply_plot_style,
    plot_phenomenological_resource_estimate,
    plot_stacked_phenomenological_resource_estimate,
)
from analog_qec.phenomenological_resource_estimate.schemes import (
    ComparisonPoint,
    build_comparison_points,
)

__all__ = [
    "BenchmarkConfig",
    "ComparisonPoint",
    "CrosstalkConfig",
    "EPSConfig",
    "ObservableTaskConfig",
    "PhenomenologicalResourceEstimateConfig",
    "PlotConfig",
    "RawConfig",
    "STARConfig",
    "STARFitConfig",
    "SurfaceCodeConfig",
    "apply_plot_style",
    "build_comparison_points",
    "crosstalk_angle",
    "crosstalk_error_exponent",
    "default_phenomenological_resource_estimate_config",
    "default_plot_config",
    "nominal_coupling_angular_frequency",
    "plot_phenomenological_resource_estimate",
    "plot_stacked_phenomenological_resource_estimate",
    "twirled_gaussian_envelope_error",
]
