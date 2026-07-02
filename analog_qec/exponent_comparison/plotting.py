"""Plotting helpers for the exponent-based resource comparison."""

from __future__ import annotations

from typing import Iterable, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler

from analog_qec.exponent_comparison.config import PlotConfig, default_plot_config
from analog_qec.exponent_comparison.schemes import ComparisonPoint


def apply_plot_style(plot_config: Optional[PlotConfig] = None) -> None:
    """Apply the notebook-wide Matplotlib style used by the figure."""

    plot_config = plot_config or default_plot_config()
    plt.rcParams["figure.figsize"] = plot_config.notebook_figure_size
    plt.rcParams["figure.dpi"] = plot_config.figure_dpi
    plt.rcParams["savefig.dpi"] = plot_config.savefig_dpi
    plt.rcParams["axes.prop_cycle"] = cycler(color=plot_config.palette)
    plt.rcParams["lines.linewidth"] = plot_config.line_width
    plt.rcParams["lines.markersize"] = plot_config.marker_size


def plot_exponent_comparison(
    points: Iterable[ComparisonPoint],
    plot_config: Optional[PlotConfig] = None,
    ax: Optional[plt.Axes] = None,
):
    """Plot the exponent comparison and return ``(fig, ax)``."""

    plot_config = plot_config or default_plot_config()
    points = list(points)

    if ax is None:
        fig, ax = plt.subplots(figsize=plot_config.figure_size)
    else:
        fig = ax.figure

    _plot_raw_trace(ax, points, plot_config)
    _plot_eps_trace(ax, points, plot_config)
    _plot_star_traces(ax, points, plot_config)
    _plot_surface_code_traces(ax, points, plot_config)
    _format_axes(fig, ax, plot_config)

    return fig, ax


def _plot_raw_trace(ax: plt.Axes, points: List[ComparisonPoint], config: PlotConfig) -> None:
    raw_points = [point for point in points if point.scheme == "Raw"]
    ax.plot(
        [point.H for point in raw_points],
        [point.nT for point in raw_points],
        "-",
        color=config.raw_color,
        alpha=0.45,
        linewidth=1.4,
    )
    for point_index, point in enumerate(raw_points):
        ax.plot(
            point.H,
            point.nT,
            config.raw_marker,
            color=config.raw_color,
            markersize=10,
            label="Raw" if point_index == 0 else None,
        )
        raw_offset = config.raw_annotation_offsets[point.label]
        ax.annotate(
            point.label.replace("Raw ", ""),
            (point.H, point.nT),
            textcoords="offset points",
            xytext=raw_offset,
            ha="center",
            va="bottom" if raw_offset[1] > 0 else "top",
            fontsize=config.annotation_fontsize,
            color=config.raw_color,
        )


def _plot_eps_trace(ax: plt.Axes, points: List[ComparisonPoint], config: PlotConfig) -> None:
    eps_points = [point for point in points if point.scheme == "EPS"]
    ax.plot(
        [point.H for point in eps_points],
        [point.nT for point in eps_points],
        "-",
        color=config.eps_color,
        alpha=0.35,
        linewidth=1.5,
    )
    for point_index, point in enumerate(eps_points):
        ax.plot(
            point.H,
            point.nT,
            config.eps_marker,
            color=config.eps_color,
            markersize=10,
            label="EPS" if point_index == 0 else None,
        )
        offset = config.eps_annotation_offsets[point.label]
        ax.annotate(
            point.label.replace("EPS ", ""),
            (point.H, point.nT),
            textcoords="offset points",
            xytext=offset,
            ha="center",
            va="bottom" if offset[1] > 0 else "top",
            fontsize=config.annotation_fontsize,
            color=config.eps_color,
        )


def _plot_star_traces(ax: plt.Axes, points: List[ComparisonPoint], config: PlotConfig) -> None:
    for p_phys in _ordered_metadata_values(points, "STAR", "p_phys"):
        star_points = [
            point for point in points if point.group == f"STAR p={p_phys:g}"
        ]
        ax.plot(
            [point.H for point in star_points],
            [point.nT for point in star_points],
            linestyle=config.star_line_styles[p_phys],
            color=config.star_colors[p_phys],
            alpha=0.5,
            linewidth=1.4,
        )
        for point_index, point in enumerate(star_points):
            ax.plot(
                point.H,
                point.nT,
                config.star_marker,
                color=config.star_colors[p_phys],
                markersize=9,
                label="STAR" if p_phys == 1e-4 and point_index == 0 else None,
            )
            offset = config.star_annotation_offsets_by_p.get(
                p_phys,
                config.star_annotation_offsets,
            )[point.metadata["d"]]
            ax.annotate(
                point.label,
                (point.H, point.nT),
                textcoords="offset points",
                xytext=offset,
                ha="right" if offset[0] < 0 else "left",
                va="bottom" if offset[1] >= 0 else "top",
                fontsize=config.annotation_fontsize,
                color=config.star_colors[p_phys],
                bbox=config.label_bbox,
            )
        label_point = star_points[-1]
        p_offset = config.star_p_label_offsets[p_phys]
        ax.annotate(
            config.star_p_labels[p_phys],
            (label_point.H, label_point.nT),
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
) -> None:
    for Lambda_surface in _ordered_metadata_values(points, "Surface code", "Lambda"):
        surface_points = [
            point
            for point in points
            if point.group == f"Surface code Lambda={Lambda_surface}"
        ]
        ax.plot(
            [point.H for point in surface_points],
            [point.nT for point in surface_points],
            linestyle=config.surface_line_styles[Lambda_surface],
            color=config.surface_colors[Lambda_surface],
            alpha=0.55,
            linewidth=1.6,
        )
        for point_index, point in enumerate(surface_points):
            ax.plot(
                point.H,
                point.nT,
                config.surface_marker,
                color=config.surface_colors[Lambda_surface],
                alpha=1.0,
                markersize=9,
                label="Surface code" if Lambda_surface == 4 and point_index == 0 else None,
            )
            if config.xlim[0] <= point.H <= config.xlim[1]:
                distance_offset = config.surface_distance_label_offsets[Lambda_surface]
                ax.annotate(
                    point.label,
                    (point.H, point.nT),
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
            (lambda_label_point.H, lambda_label_point.nT),
            textcoords="offset points",
            xytext=config.lambda_label_offsets[Lambda_surface],
            ha="right",
            va="top",
            fontsize=config.annotation_fontsize,
            color=config.surface_colors[Lambda_surface],
            bbox=config.label_bbox,
        )


def _format_axes(fig: plt.Figure, ax: plt.Axes, config: PlotConfig) -> None:
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*config.xlim)
    ax.set_ylim(*config.ylim)
    ax.margins(x=0.04, y=0.08)
    ax.set_xlabel(r"Cumulative register error exponent $H$")
    ax.set_ylabel("Space-Time Overhead (qubits x circuit depth)")
    ax.annotate(
        "Low error,\nLow overhead",
        xy=(4e-4, 0.2e2),
        xytext=(0.5e-3, 1.4e3),
        arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0),
        color="k",
        fontsize=9,
        ha="left",
        va="center",
    )
    ax.legend(loc="center left", frameon=True)

    ax_top = ax.twiny()
    ax_top.set_xscale("log")
    ax_top.set_xlim(ax.get_xlim())
    pfail_ticks = np.array(config.top_axis_failure_ticks)
    H_ticks = -np.log1p(-pfail_ticks)
    visible = (H_ticks >= ax.get_xlim()[0]) & (H_ticks <= ax.get_xlim()[1])
    top_tick_positions = list(H_ticks[visible])
    top_tick_labels = [f"{tick:g}" for tick in pfail_ticks[visible]]
    if top_tick_positions[-1] < ax.get_xlim()[1]:
        top_tick_positions.append(ax.get_xlim()[1])
        top_tick_labels.append(r"$\to 1$")
    ax_top.set_xticks(top_tick_positions)
    ax_top.set_xticklabels(top_tick_labels)
    ax_top.xaxis.set_minor_formatter(plt.NullFormatter())
    ax_top.set_xlabel(r"Register failure probability $P_\mathrm{fail}=1-e^{-H}$")

    fig.tight_layout()


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
