"""Plotting helpers for the phenomenological resource estimate."""

from __future__ import annotations

from typing import Iterable, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

from analog_qec.phenomenological_resource_estimate.config import (
    PlotConfig,
    default_plot_config,
)
from analog_qec.phenomenological_resource_estimate.schemes import ComparisonPoint

MICROSECONDS_TO_SECONDS = 1e-6


def apply_plot_style(plot_config: Optional[PlotConfig] = None) -> None:
    """Apply the notebook-wide Matplotlib style used by the figure."""

    plot_config = plot_config or default_plot_config()
    plt.rcParams["figure.figsize"] = plot_config.notebook_figure_size
    plt.rcParams["figure.dpi"] = plot_config.figure_dpi
    plt.rcParams["savefig.dpi"] = plot_config.savefig_dpi
    plt.rcParams["axes.prop_cycle"] = cycler(color=plot_config.palette)
    plt.rcParams["lines.linewidth"] = plot_config.line_width
    plt.rcParams["lines.markersize"] = plot_config.marker_size


def plot_phenomenological_resource_estimate(
    points: Iterable[ComparisonPoint],
    plot_config: Optional[PlotConfig] = None,
    ax: Optional[plt.Axes] = None,
    y_metric: str = "space_time",
):
    """Plot the resource estimate and return ``(fig, ax)``."""

    plot_config = plot_config or default_plot_config()
    points = list(points)
    y_metric = _normalize_y_metric(y_metric)

    if ax is None:
        fig, ax = plt.subplots(figsize=plot_config.figure_size)
    else:
        fig = ax.figure

    _plot_resource_estimate_on_axis(ax, points, plot_config, y_metric)
    _format_axes(fig, ax, plot_config, points, y_metric)

    return fig, ax


def plot_stacked_phenomenological_resource_estimate(
    points: Iterable[ComparisonPoint],
    plot_config: Optional[PlotConfig] = None,
    y_metrics: Iterable[str] = ("space_time", "space", "time"),
    axes: Optional[Iterable[plt.Axes]] = None,
):
    """Plot selected resource metrics in a shared-x vertical stack."""

    plot_config = plot_config or default_plot_config()
    points = list(points)
    y_metrics = _normalize_y_metrics(y_metrics)

    if axes is None:
        fig, axes = plt.subplots(
            len(y_metrics),
            1,
            figsize=_stacked_figure_size(plot_config, len(y_metrics)),
            sharex=True,
            squeeze=False,
        )
        axes = [axis for axis in axes[:, 0]]
    else:
        axes = _axes_list(axes)
        if len(axes) != len(y_metrics):
            raise ValueError(
                f"Expected {len(y_metrics)} axes for y_metrics={y_metrics!r}; "
                f"got {len(axes)}"
            )
        fig = axes[0].figure
        if any(axis.figure is not fig for axis in axes):
            raise ValueError("All stacked axes must belong to the same figure")

    for index, (axis, y_metric) in enumerate(zip(axes, y_metrics)):
        is_bottom_axis = index == len(y_metrics) - 1
        _plot_resource_estimate_on_axis(axis, points, plot_config, y_metric)
        _format_axes(
            fig,
            axis,
            plot_config,
            points,
            y_metric,
            show_xlabel=is_bottom_axis,
            show_xticklabels=is_bottom_axis,
            show_legend=index == 0,
            apply_tight_layout=False,
        )

    fig.align_ylabels(axes)
    fig.tight_layout()

    return fig, axes


def _plot_resource_estimate_on_axis(
    ax: plt.Axes,
    points: List[ComparisonPoint],
    plot_config: PlotConfig,
    y_metric: str,
) -> None:
    _plot_raw_trace(ax, points, plot_config, y_metric)
    _plot_eps_trace(ax, points, plot_config, y_metric)
    _plot_star_traces(ax, points, plot_config, y_metric)
    _plot_surface_code_traces(ax, points, plot_config, y_metric)


def _plot_raw_trace(
    ax: plt.Axes,
    points: List[ComparisonPoint],
    config: PlotConfig,
    y_metric: str,
) -> None:
    raw_points = [point for point in points if point.scheme == "Raw"]
    ax.plot(
        [point.H for point in raw_points],
        [_y_value(point, y_metric) for point in raw_points],
        "-",
        color=config.raw_color,
        alpha=0.45,
        linewidth=1.4,
    )
    for point_index, point in enumerate(raw_points):
        ax.plot(
            point.H,
            _y_value(point, y_metric),
            config.raw_marker,
            color=config.raw_color,
            markersize=10,
            label="Raw" if point_index == 0 else None,
        )
        raw_offset = config.raw_annotation_offsets[point.label]
        ax.annotate(
            point.label.replace("Raw ", ""),
            (point.H, _y_value(point, y_metric)),
            textcoords="offset points",
            xytext=raw_offset,
            ha="center",
            va="bottom" if raw_offset[1] > 0 else "top",
            fontsize=config.annotation_fontsize,
            color=config.raw_color,
        )


def _plot_eps_trace(
    ax: plt.Axes,
    points: List[ComparisonPoint],
    config: PlotConfig,
    y_metric: str,
) -> None:
    eps_points = [point for point in points if point.scheme == "EPS"]
    ax.plot(
        [point.H for point in eps_points],
        [_y_value(point, y_metric) for point in eps_points],
        "-",
        color=config.eps_color,
        alpha=0.35,
        linewidth=1.5,
    )
    for point_index, point in enumerate(eps_points):
        ax.plot(
            point.H,
            _y_value(point, y_metric),
            config.eps_marker,
            color=config.eps_color,
            markersize=10,
            label="EPS" if point_index == 0 else None,
        )
        offset = config.eps_annotation_offsets[point.label]
        ax.annotate(
            point.label.replace("EPS ", ""),
            (point.H, _y_value(point, y_metric)),
            textcoords="offset points",
            xytext=offset,
            ha="center",
            va="bottom" if offset[1] > 0 else "top",
            fontsize=config.annotation_fontsize,
            color=config.eps_color,
        )


def _plot_star_traces(
    ax: plt.Axes,
    points: List[ComparisonPoint],
    config: PlotConfig,
    y_metric: str,
) -> None:
    for p_phys in _ordered_metadata_values(points, "STAR", "p_phys"):
        star_points = [
            point for point in points if point.group == f"STAR p={p_phys:g}"
        ]
        ax.plot(
            [point.H for point in star_points],
            [_y_value(point, y_metric) for point in star_points],
            linestyle=config.star_line_styles[p_phys],
            color=config.star_colors[p_phys],
            alpha=0.5,
            linewidth=1.4,
        )
        for point_index, point in enumerate(star_points):
            ax.plot(
                point.H,
                _y_value(point, y_metric),
                config.star_marker,
                color=config.star_colors[p_phys],
                markersize=9,
                label="STAR" if p_phys == 1e-4 and point_index == 0 else None,
            )
            if _annotate_star_distance(point, y_metric):
                offset = _star_annotation_offset(point, config)
                ax.annotate(
                    point.label,
                    (point.H, _y_value(point, y_metric)),
                    textcoords="offset points",
                    xytext=offset,
                    ha="right" if offset[0] < 0 else "left",
                    va="bottom" if offset[1] >= 0 else "top",
                    fontsize=config.annotation_fontsize,
                    color=config.star_colors[p_phys],
                    bbox=config.label_bbox,
                )
        label_point = star_points[-1]
        p_offset = _star_p_label_offset(p_phys, config, y_metric)
        ax.annotate(
            config.star_p_labels[p_phys],
            (label_point.H, _y_value(label_point, y_metric)),
            textcoords="offset points",
            xytext=p_offset,
            ha="right" if p_offset[0] < 0 else "left",
            va="bottom" if p_offset[1] >= 0 else "top",
            fontsize=config.annotation_fontsize,
            color=config.star_colors[p_phys],
            bbox=config.label_bbox,
        )


def _plot_surface_code_traces(
    ax: plt.Axes,
    points: List[ComparisonPoint],
    config: PlotConfig,
    y_metric: str,
) -> None:
    for Lambda_surface in _ordered_metadata_values(points, "Surface code", "Lambda"):
        surface_points = [
            point
            for point in points
            if point.group == f"Surface code Lambda={Lambda_surface}"
        ]
        ax.plot(
            [point.H for point in surface_points],
            [_y_value(point, y_metric) for point in surface_points],
            linestyle=config.surface_line_styles[Lambda_surface],
            color=config.surface_colors[Lambda_surface],
            alpha=0.55,
            linewidth=1.6,
        )
        for point_index, point in enumerate(surface_points):
            ax.plot(
                point.H,
                _y_value(point, y_metric),
                config.surface_marker,
                color=config.surface_colors[Lambda_surface],
                alpha=1.0,
                markersize=9,
                label="Surface code" if Lambda_surface == 4 and point_index == 0 else None,
            )
            if config.xlim[0] <= point.H <= config.xlim[1]:
                distance_offset = _surface_distance_label_offset(
                    Lambda_surface,
                    config,
                    y_metric,
                )
                ax.annotate(
                    point.label,
                    (point.H, _y_value(point, y_metric)),
                    textcoords="offset points",
                    xytext=distance_offset,
                    ha="left" if distance_offset[0] >= 0 else "right",
                    va="bottom" if distance_offset[1] >= 0 else "top",
                    fontsize=config.annotation_fontsize,
                    color=config.surface_colors[Lambda_surface],
                    bbox=config.label_bbox,
                )

        visible_lambda_points = [
            point
            for point in surface_points
            if config.xlim[0] <= point.H <= config.xlim[1]
        ]
        lambda_label_point = next(
            (
                point
                for point in visible_lambda_points
                if point.metadata["d"] == config.lambda_label_distance
            ),
            visible_lambda_points[0] if visible_lambda_points else surface_points[0],
        )
        ax.annotate(
            rf"$\Lambda={Lambda_surface}$",
            (lambda_label_point.H, _y_value(lambda_label_point, y_metric)),
            textcoords="offset points",
            xytext=_lambda_label_offset(Lambda_surface, config, y_metric),
            ha="right",
            va="top",
            fontsize=config.annotation_fontsize,
            color=config.surface_colors[Lambda_surface],
            bbox=config.label_bbox,
        )


def _format_axes(
    fig: plt.Figure,
    ax: plt.Axes,
    config: PlotConfig,
    points: List[ComparisonPoint],
    y_metric: str,
    show_xlabel: bool = True,
    show_xticklabels: bool = True,
    show_legend: bool = True,
    apply_tight_layout: bool = True,
) -> None:
    ylim = _metric_ylim(points, config, y_metric)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*config.xlim)
    ax.set_ylim(*ylim)
    ax.margins(x=0.04, y=0.08)
    failure_tick_positions, failure_tick_labels = _failure_probability_ticks(
        ax.get_xlim(),
        config,
    )
    ax.set_xticks(failure_tick_positions)
    ax.set_xticklabels(failure_tick_labels)
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.tick_params(
        axis="x",
        top=False,
        labeltop=False,
        bottom=True,
        labelbottom=show_xticklabels,
    )
    if show_xlabel:
        ax.set_xlabel(r"Error proxy probability $P_\mathrm{err}=1-e^{-H}$")
    else:
        ax.set_xlabel("")
    ax.set_ylabel(_y_axis_label(y_metric))
    ax.annotate(
        "Low error,\nLow overhead",
        xy=(4e-4, _log_lerp(ylim, 0.10)),
        xytext=(0.5e-3, _log_lerp(ylim, 0.25)),
        arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0),
        color="k",
        fontsize=9,
        ha="left",
        va="center",
    )
    if show_legend:
        ax.legend(loc="center left", frameon=True)

    if apply_tight_layout:
        fig.tight_layout()


def _normalize_y_metric(y_metric: str) -> str:
    y_metric = {"spacetime": "space_time"}.get(y_metric, y_metric)
    if y_metric not in {"space_time", "space", "time"}:
        raise ValueError(
            "y_metric must be one of 'space_time', 'spacetime', 'space', or 'time'; "
            f"got {y_metric!r}"
        )
    return y_metric


def _normalize_y_metrics(y_metrics: Iterable[str]) -> list[str]:
    if isinstance(y_metrics, str):
        y_metrics = (y_metrics,)
    normalized_metrics = [_normalize_y_metric(y_metric) for y_metric in y_metrics]
    if not normalized_metrics:
        raise ValueError("y_metrics must contain at least one metric")
    if len(set(normalized_metrics)) != len(normalized_metrics):
        raise ValueError(f"y_metrics must not contain duplicates; got {y_metrics!r}")
    return normalized_metrics


def _axes_list(axes: Iterable[plt.Axes]) -> list[plt.Axes]:
    if isinstance(axes, plt.Axes):
        return [axes]
    return list(np.ravel(list(axes)))


def _stacked_figure_size(
    plot_config: PlotConfig,
    n_metrics: int,
) -> tuple[float, float]:
    width, height = plot_config.figure_size
    return width, max(height, height * 0.72 * n_metrics)


def _y_value(point: ComparisonPoint, y_metric: str) -> float:
    attr_by_metric = {
        "space_time": "nT",
        "space": "n",
        "time": "T",
    }
    attr = attr_by_metric[y_metric]
    value = getattr(point, attr)
    if value is None:
        raise ValueError(
            f"Comparison point {point.label!r} does not define {attr!r}, "
            f"which is required for y_metric={y_metric!r}"
        )
    value = float(value)
    if y_metric in {"space_time", "time"}:
        return value * MICROSECONDS_TO_SECONDS
    return value


def _y_axis_label(y_metric: str) -> str:
    labels = {
        "space_time": "Task Space-Time Cost (qubit-s)",
        "space": "Space Cost (qubits)",
        "time": "Task Time Cost (s)",
    }
    return labels[y_metric]


def _star_annotation_offset(
    point: ComparisonPoint,
    config: PlotConfig,
) -> tuple[int, int]:
    p_phys = point.metadata["p_phys"]
    return config.star_annotation_offsets_by_p.get(
        p_phys,
        config.star_annotation_offsets,
    )[point.metadata["d"]]


def _annotate_star_distance(point: ComparisonPoint, y_metric: str) -> bool:
    return y_metric == "space"


def _star_p_label_offset(
    p_phys: float,
    config: PlotConfig,
    y_metric: str,
) -> tuple[int, int]:
    metric_offsets = config.star_p_label_offsets_by_metric.get(y_metric, {})
    return metric_offsets.get(p_phys, config.star_p_label_offsets[p_phys])


def _surface_distance_label_offset(
    Lambda_surface: int,
    config: PlotConfig,
    y_metric: str,
) -> tuple[int, int]:
    metric_offsets = config.surface_distance_label_offsets_by_metric.get(y_metric, {})
    return metric_offsets.get(
        Lambda_surface,
        config.surface_distance_label_offsets[Lambda_surface],
    )


def _lambda_label_offset(
    Lambda_surface: int,
    config: PlotConfig,
    y_metric: str,
) -> tuple[int, int]:
    metric_offsets = config.lambda_label_offsets_by_metric.get(y_metric, {})
    return metric_offsets.get(
        Lambda_surface,
        config.lambda_label_offsets[Lambda_surface],
    )


def _metric_ylim(
    points: List[ComparisonPoint],
    config: PlotConfig,
    y_metric: str,
) -> tuple[float, float]:
    y_values = np.array([_y_value(point, y_metric) for point in points], dtype=float)
    positive_y_values = y_values[np.isfinite(y_values) & (y_values > 0)]
    if positive_y_values.size == 0:
        raise ValueError(f"No positive y values available for y_metric={y_metric!r}")

    log_min = np.log10(positive_y_values.min())
    log_max = np.log10(positive_y_values.max())
    log_span = log_max - log_min
    lower_padding = max(0.12 * log_span, 0.30)
    upper_padding = max(0.10 * log_span, 0.25)
    return 10 ** (log_min - lower_padding), 10 ** (log_max + upper_padding)


def _log_lerp(bounds: tuple[float, float], fraction: float) -> float:
    log_bounds = np.log10(bounds)
    return float(10 ** (log_bounds[0] + fraction * (log_bounds[1] - log_bounds[0])))


def _failure_probability_ticks(
    xlim: tuple[float, float],
    config: PlotConfig,
) -> tuple[list[float], list[str]]:
    pfail_ticks = np.array(config.top_axis_failure_ticks)
    H_ticks = -np.log1p(-pfail_ticks)
    visible = (H_ticks >= xlim[0]) & (H_ticks <= xlim[1])
    tick_positions = list(H_ticks[visible])
    tick_labels = [f"{tick:g}" for tick in pfail_ticks[visible]]
    if tick_positions and tick_positions[-1] < xlim[1]:
        tick_positions.append(xlim[1])
        tick_labels.append(r"$\to 1$")
    return tick_positions, tick_labels


def _ordered_metadata_values(
    points: List[ComparisonPoint],
    scheme: str,
    key: str,
) -> List[object]:
    values = []
    for point in points:
        if point.scheme == scheme and key in point.metadata and point.metadata[key] not in values:
            values.append(point.metadata[key])
    return values
