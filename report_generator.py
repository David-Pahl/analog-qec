"""
Report Generation Module

This module provides functions to generate comprehensive reports comparing
analog and digital quantum computing resource requirements.
"""

from typing import Dict, Optional, Union
import json
from datetime import datetime
from analog_simulator import AnalogSimulator
from digital_resource_estimator import DigitalResourceEstimator


def generate_comparison_report(
    analog_sim: AnalogSimulator,
    digital_est: DigitalResourceEstimator,
    title: str = "Quantum Resource Estimation Report",
    include_metadata: bool = True
) -> Dict:
    """
    Generate a comprehensive comparison report between analog and digital approaches.
    
    Args:
        analog_sim: AnalogSimulator instance
        digital_est: DigitalResourceEstimator instance
        title: Report title
        include_metadata: Whether to include metadata (timestamp, etc.)
        
    Returns:
        Dictionary containing the full report
    """
    report = {
        'title': title,
    }
    
    if include_metadata:
        report['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    # Analog simulation section
    report['analog_simulation'] = {
        'circuit_configuration': {
            'width': analog_sim.config.circuit_width,
            'individual_t1_times_us': analog_sim.config.qubit_t1_times,
            'measurement_error_rate': analog_sim.config.measurement_error_rate,
        },
        'system_performance': {
            'system_t1_us': round(analog_sim.system_t1, 4),
            'feasible_runtime_us': round(analog_sim.feasible_runtime, 4),
            'feasible_runtime_ms': round(analog_sim.feasible_runtime_ms, 4),
            'feasible_runtime_s': round(analog_sim.feasible_runtime_seconds, 6),
        },
        'error_analysis': {
            'decoherence_error': round(analog_sim.get_decoherence_error(), 6),
            'total_error': round(analog_sim.get_total_error(), 6),
            'fidelity': round(analog_sim.get_fidelity(), 6),
        }
    }
    
    # Digital resource estimation section
    report['digital_fault_tolerant'] = {
        'logical_configuration': {
            'logical_qubits': digital_est.config.logical_qubits,
            'target_runtime_us': digital_est.config.target_runtime,
            'target_runtime_s': round(digital_est.config.target_runtime / 1e6, 6),
            'physical_error_rate': digital_est.config.digital_error_rate,
            'target_logical_error_rate': digital_est.config.target_logical_error_rate,
        },
        'error_correction': {
            'code_distance': digital_est.config.code_distance,
            'physical_qubits_per_logical': digital_est.config.qubits_per_logical,
            'logical_gate_time_us': digital_est.config.logical_gate_time,
            'achieved_logical_error_rate': f"{digital_est.get_logical_error_rate():.2e}",
        },
        'resource_breakdown': {
            'data_qubits': digital_est.data_qubits,
            'magic_state_qubits': digital_est.magic_state_qubits,
            'compilation_qubits': digital_est.compilation_qubits,
            'total_physical_qubits': digital_est.total_physical_qubits,
        },
        'performance_metrics': {
            'logical_gate_count': digital_est.logical_gate_count,
            'physical_gate_count': digital_est.get_physical_gate_count(),
            'target_runtime_us': digital_est.config.target_runtime,
            'wall_clock_time_us': round(digital_est.get_wall_clock_time(), 2),
            'wall_clock_time_seconds': round(digital_est.get_wall_clock_time_seconds(), 6),
            'wall_clock_time_hours': round(digital_est.get_wall_clock_time_hours(), 4),
            'space_time_volume_qubit_us': f"{digital_est.space_time_volume:.2e}",
            'space_time_volume_qubit_s': f"{digital_est.space_time_volume_qubit_seconds:.2e}",
            'algorithm_success_probability': round(
                digital_est.get_algorithm_success_probability(), 6
            ),
        }
    }
    
    # Comparison section
    runtime_ratio = (
        digital_est.config.target_runtime / analog_sim.feasible_runtime
    )
    
    report['comparison'] = {
        'qubit_count_ratio': round(
            digital_est.total_physical_qubits / analog_sim.config.circuit_width, 2
        ),
        'runtime_ratio_digital_to_analog': round(runtime_ratio, 2),
        'analog_faster': runtime_ratio > 1,
        'space_time_advantage': {
            'analog_qubit_seconds': round(
                analog_sim.config.circuit_width * analog_sim.feasible_runtime_seconds, 2
            ),
            'digital_qubit_seconds': round(
                digital_est.space_time_volume_qubit_seconds, 2
            ),
            'ratio': round(
                digital_est.space_time_volume_qubit_seconds / 
                (analog_sim.config.circuit_width * analog_sim.feasible_runtime_seconds),
                2
            )
        }
    }
    
    return report


def format_report_table(report: Dict) -> str:
    """
    Format the report as a text table similar to the PDF format.
    
    Args:
        report: Report dictionary from generate_comparison_report()
        
    Returns:
        Formatted string table
    """
    analog = report['analog_simulation']
    digital = report['digital_fault_tolerant']
    comparison = report['comparison']
    
    lines = []
    lines.append("=" * 80)
    lines.append(f"{report['title']:^80}")
    lines.append("=" * 80)
    
    if 'metadata' in report:
        lines.append(f"Generated: {report['metadata']['generated_at']}")
        lines.append("-" * 80)
    
    lines.append("")
    lines.append("ANALOG SIMULATION")
    lines.append("-" * 80)
    lines.append(f"System Size:            {analog['circuit_configuration']['width']} qubits")
    lines.append(f"System T1:              {analog['system_performance']['system_t1_us']:.2f} μs")
    lines.append(f"Feasible Runtime:       {analog['system_performance']['feasible_runtime_ms']:.2f} ms")
    lines.append(f"                        ({analog['system_performance']['feasible_runtime_s']:.6f} s)")
    lines.append(f"Fidelity:               {analog['error_analysis']['fidelity']:.4f}")
    lines.append(f"Total Error:            {analog['error_analysis']['total_error']:.6f}")
    
    lines.append("")
    lines.append("DIGITAL FAULT-TOLERANT COMPUTATION")
    lines.append("-" * 80)
    lines.append(f"Logical Qubits:         {digital['logical_configuration']['logical_qubits']}")
    lines.append(f"Code Distance:          {digital['error_correction']['code_distance']}")
    lines.append(f"Physical Qubits/Logical:{digital['error_correction']['physical_qubits_per_logical']}")
    lines.append("")
    lines.append("Resource Breakdown:")
    lines.append(f"  Data Qubits:          {digital['resource_breakdown']['data_qubits']:,}")
    lines.append(f"  Magic State  Qubits:  {digital['resource_breakdown']['magic_state_qubits']:,}")
    lines.append(f"  Compilation Qubits:   {digital['resource_breakdown']['compilation_qubits']:,}")
    lines.append(f"  TOTAL Physical Qubits:{digital['resource_breakdown']['total_physical_qubits']:,}")
    lines.append("")
    lines.append(f"Target Runtime:         {digital['logical_configuration']['target_runtime_s']:.6f} s ({digital['logical_configuration']['target_runtime_us']:.2f} μs)")
    lines.append(f"Wall Clock Time:        {digital['performance_metrics']['wall_clock_time_us']:.2f} μs")
    lines.append(f"                        {digital['performance_metrics']['wall_clock_time_seconds']:.6f} s")
    lines.append(f"                        {digital['performance_metrics']['wall_clock_time_hours']:.4f} hours")
    lines.append(f"Logical Gates:          {digital['performance_metrics']['logical_gate_count']:,}")
    lines.append(f"Space-Time Volume:      {digital['performance_metrics']['space_time_volume_qubit_s']} qubit-s")
    lines.append(f"Success Probability:    {digital['performance_metrics']['algorithm_success_probability']:.4f}")
    
    lines.append("")
    lines.append("COMPARISON")
    lines.append("-" * 80)
    lines.append(f"Qubit Count Ratio (D/A):{comparison['qubit_count_ratio']:.2f}x")
    lines.append(f"Runtime Ratio (D/A):    {comparison['runtime_ratio_digital_to_analog']:.2f}x")
    
    if comparison['analog_faster']:
        lines.append(f"→ Analog simulation is {comparison['runtime_ratio_digital_to_analog']:.2f}x FASTER")
    else:
        lines.append(f"→ Digital computation is {1/comparison['runtime_ratio_digital_to_analog']:.2f}x FASTER")
    
    lines.append("")
    lines.append("Space-Time Resources:")
    lines.append(f"  Analog:  {comparison['space_time_advantage']['analog_qubit_seconds']:.2e} qubit-s")
    lines.append(f"  Digital: {comparison['space_time_advantage']['digital_qubit_seconds']:.2e} qubit-s")
    lines.append(f"  Ratio:   {comparison['space_time_advantage']['ratio']:.2e}x")
    
    lines.append("=" * 80)
    
    return "\n".join(lines)


def save_report_json(report: Dict, filename: str):
    """
    Save the report to a JSON file.
    
    Args:
        report: Report dictionary
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to {filename}")


def save_report_text(report: Dict, filename: str):
    """
    Save the formatted report to a text file.
    
    Args:
        report: Report dictionary
        filename: Output filename
    """
    table = format_report_table(report)
    
    with open(filename, 'w') as f:
        f.write(table)
    
    print(f"Report saved to {filename}")


def print_report(report: Dict):
    """
    Print the formatted report to console.
    
    Args:
        report: Report dictionary
    """
    print(format_report_table(report))
