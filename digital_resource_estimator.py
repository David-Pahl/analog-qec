"""
Digital Resource Estimation Module

This module provides the DigitalResourceEstimator class for calculating
space-time overhead for fault-tolerant quantum computation with error correction.

Includes calculations for:
- Physical qubits per logical qubit
- Magic state cultivation overhead
- Compilation overhead
- Total physical qubits required
- Space-time volume
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class DigitalResourceConfig:
    """Configuration for digital resource estimation."""
    
    # Core parameters
    logical_qubits: int  # Number of logical qubits needed
    target_runtime: float  # Target runtime in microseconds
    digital_error_rate: float  # Physical qubit error rate (per gate)
    
    # Error correction parameters
    target_logical_error_rate: float = 1e-10  # Target logical error rate
    code_distance: Optional[int] = None  # Surface code distance (auto-calculated if None)
    
    # Physical qubits per logical qubit
    # For surface codes: roughly 2 * d^2 where d is code distance
    qubits_per_logical: Optional[int] = None  # Auto-calculated if None
    
    # Magic state cultivation
    magic_state_error_threshold: float = 1e-3  # Threshold for magic states
    t_gate_count: int = 100  # Estimated number of T gates
    magic_state_overhead_factor: float = 2.0  # Overhead factor for magic state cultivation
    
    # Compilation overhead
    compilation_overhead_factor: float = 1.5  # Extra qubits for routing/compilation
    
    # Timing parameters
    physical_gate_time: float = 0.1  # Physical gate time in microseconds
    logical_gate_time: Optional[float] = None  # Auto-calculated based on code distance
    error_correction_cycle_time: Optional[float] = None  # Auto-calculated
    
    def __post_init__(self):
        """Calculate derived parameters."""
        if self.code_distance is None:
            self.code_distance = self._calculate_code_distance()
        
        if self.qubits_per_logical is None:
            self.qubits_per_logical = self._calculate_qubits_per_logical()
        
        if self.logical_gate_time is None:
            self.logical_gate_time = self.code_distance * self.physical_gate_time
        
        if self.error_correction_cycle_time is None:
            self.error_correction_cycle_time = self.code_distance * self.physical_gate_time
    
    def _calculate_code_distance(self) -> int:
        """
        Calculate required code distance based on error rates.
        
        The threshold theorem gives: p_L ≈ c * (p/p_th)^((d+1)/2)
        where p is physical error rate, p_L is logical error rate,
        p_th is threshold (~0.01 for surface codes), d is code distance.
        
        Returns:
            Code distance
        """
        # Simplified calculation: d ≈ 2 * log(1/p_L) / log(p_th/p)
        p = self.digital_error_rate
        p_L = self.target_logical_error_rate
        p_th = 0.01  # Surface code threshold
        
        if p >= p_th:
            raise ValueError(
                f"Physical error rate ({p}) must be below threshold ({p_th})"
            )
        
        # Calculate distance needed
        log_ratio = np.log(p_th / p)
        d = int(np.ceil(2 * np.log(1.0 / p_L) / log_ratio))
        
        # Ensure odd distance (required for surface codes)
        if d % 2 == 0:
            d += 1
        
        # Minimum distance
        d = max(d, 3)
        
        return d
    
    def _calculate_qubits_per_logical(self) -> int:
        """
        Calculate physical qubits needed per logical qubit.
        
        For surface codes: approximately 2 * d^2
        
        Returns:
            Physical qubits per logical qubit
        """
        return 2 * self.code_distance ** 2


class DigitalResourceEstimator:
    """
    Digital fault-tolerant quantum resource estimator.
    
    Calculates the resources needed for fault-tolerant quantum computation,
    including physical qubits, magic state cultivation, and compilation overhead.
    """
    
    def __init__(self, config: DigitalResourceConfig):
        """
        Initialize the digital resource estimator.
        
        Args:
            config: Configuration object with resource estimation parameters
        """
        self.config = config
        
        # Calculate resources
        self._data_qubits = None
        self._magic_state_qubits = None
        self._compilation_qubits = None
        self._total_physical_qubits = None
        self._space_time_volume = None
        self._logical_gate_count = None
        
        self._calculate_resources()
    
    def _calculate_resources(self):
        """Calculate all resource requirements."""
        # Data qubits (logical qubits encoded in physical qubits)
        self._data_qubits = (
            self.config.logical_qubits * self.config.qubits_per_logical
        )
        
        # Magic state cultivation qubits
        # Needed for implementing non-Clifford gates (T gates)
        self._magic_state_qubits = int(
            self.config.t_gate_count * 
            self.config.magic_state_overhead_factor *
            self.config.qubits_per_logical
        )
        
        # Compilation/routing overhead qubits
        self._compilation_qubits = int(
            self._data_qubits * 
            (self.config.compilation_overhead_factor - 1.0)
        )
        
        # Total physical qubits
        self._total_physical_qubits = (
            self._data_qubits + 
            self._magic_state_qubits + 
            self._compilation_qubits
        )
        
        # Logical gate count estimate
        # Based on runtime and logical gate time
        self._logical_gate_count = int(
            self.config.target_runtime / self.config.logical_gate_time
        )
        
        # Space-time volume (qubit-microseconds)
        self._space_time_volume = (
            self._total_physical_qubits * self.config.target_runtime
        )
    
    def get_logical_error_rate(self) -> float:
        """
        Calculate the actual logical error rate achieved.
        
        Returns:
            Logical error rate
        """
        p = self.config.digital_error_rate
        d = self.config.code_distance
        p_th = 0.01  # Surface code threshold
        
        # Simplified logical error rate: p_L ≈ 0.1 * (p/p_th)^((d+1)/2)
        exponent = (d + 1) / 2
        p_L = 0.1 * (p / p_th) ** exponent
        
        return p_L
    
    def get_algorithm_success_probability(self) -> float:
        """
        Calculate the probability of successful algorithm execution.
        
        Returns:
            Success probability
        """
        # Probability of no errors during logical gates
        p_L = self.get_logical_error_rate()
        p_success = (1.0 - p_L) ** self._logical_gate_count
        
        return p_success
    
    def get_physical_gate_count(self) -> int:
        """
        Estimate total physical gate operations.
        
        Returns:
            Total physical gate count
        """
        # Physical gates per logical gate ≈ O(d^3) for surface codes
        physical_per_logical = self.config.code_distance ** 3
        
        return self._logical_gate_count * physical_per_logical
    
    def get_wall_clock_time(self) -> float:
        """
        Calculate actual wall-clock time for computation with QEC overhead.
        
        ═════════════════════════════════════════════════════════════════════
        CRITICAL DISTINCTION:
        ═════════════════════════════════════════════════════════════════════
        
        target_runtime (LOGICAL TIME):
            Duration of the quantum algorithm/simulation you want to run.
            Example: You want 0.5 µs of system evolution
            
        wall_clock_time (REAL TIME):
            Actual time a physical QEC system takes to execute that algorithm.
            Includes all QEC overhead: syndrome extraction, magic states, routing.
            Example: 0.5 µs logical → 3.6 µs wall-clock with d=25
        
        ═════════════════════════════════════════════════════════════════════
        
        Formula:  wall_clock_time = target_runtime × QEC_overhead_factor
        
        QEC overhead breakdown:
        ─────────────────────────────────────────────────────────────────────
        1. STABILIZATION (syndrome extraction & decoding)
           - Measure parity checks every ~d cycles
           - Decode errors and apply corrections
           - factor ≈ 1 + d/10  →  ~3-4× for d=25-35
           
        2. MAGIC STATE OVERHEAD (non-Clifford gate prep)
           - T gates need pre-prepared magic states
           - State distillation adds latency
           - factor ≈ 1.2 (assumes 20% T-gate overhead)
           
        3. COMPILATION/TROTTER (routing + decomposition)
           - Map logical circuit to 2D qubit array
           - Trotter expand time-evolution circuits
           - factor ≈ 1.5 (well-optimized)
        
        ─────────────────────────────────────────────────────────────────────
        TOTAL OVERHEAD:  3.5 × 1.2 × 1.5 ≈ 6.3×  (d=25)
        ─────────────────────────────────────────────────────────────────────
        
        CONCRETE EXAMPLE:
          Algorithm:      Simulate 0.5 µs of Hamiltonian evolution
          Error target:   p_L ≲ 10⁻¹⁰ (requires d ≈ 25)
          
          Overhead calculation:
            Stabilization:  1 + 25/10 = 3.5×
            Magic states:   1 + 2.0 × 0.1 = 1.2×
            Compilation:    1.5×
            ────────────────────────
            Total:          3.5 × 1.2 × 1.5 ≈ 6.3×
          
          Wall-clock execution:  0.5 µs × 6.3 ≈ 3.15 µs real time
          
        KEY INSIGHT:
          Even a "short" 0.5 µs simulation takes multiple microseconds to
          execute on a QEC system because logical operations are inherently
          slow due to the need for continuous syndrome measurement and 
          error correction.
        
        Returns:
            Wall-clock time in microseconds
        """
        d = self.config.code_distance
        
        # 1. STABILIZATION OVERHEAD
        # Syndrome measurement requires rounds of measurement & decoding
        stabilization_overhead = 1.0 + (d / 10.0)
        
        # 2. MAGIC STATE OVERHEAD
        # Non-Clifford gate preparation (T gate magic states)
        magic_state_time_factor = 1.0 + (self.config.magic_state_overhead_factor * 0.1)
        
        # 3. COMPILATION/TROTTER OVERHEAD
        # Circuit routing on 2D array + decomposition overhead
        trotter_overhead_factor = 1.5
        
        # TOTAL QEC OVERHEAD MULTIPLIER
        qec_overhead_factor = (
            stabilization_overhead * 
            magic_state_time_factor * 
            trotter_overhead_factor
        )
        
        # Wall-clock time = logical/simulation time × QEC overhead
        wall_clock_us = self.config.target_runtime * qec_overhead_factor
        
        return wall_clock_us
    
    def get_wall_clock_time_seconds(self) -> float:
        """
        Calculate wall-clock time in seconds.
        
        Returns:
            Wall-clock time in seconds
        """
        return self.get_wall_clock_time() / 1e6
    
    def get_wall_clock_time_hours(self) -> float:
        """
        Calculate wall-clock time in hours.
        
        Returns:
            Wall-clock time in hours
        """
        return self.get_wall_clock_time_seconds() / 3600.0
    
    # Public property accessors
    @property
    def data_qubits(self) -> int:
        """Number of physical qubits used for data (encoded logical qubits)."""
        return self._data_qubits
    
    @property
    def magic_state_qubits(self) -> int:
        """Number of physical qubits used for magic state cultivation."""
        return self._magic_state_qubits
    
    @property
    def compilation_qubits(self) -> int:
        """Number of physical qubits used for compilation/routing overhead."""
        return self._compilation_qubits
    
    @property
    def total_physical_qubits(self) -> int:
        """Total number of physical qubits required."""
        return self._total_physical_qubits
    
    @property
    def space_time_volume(self) -> float:
        """Space-time volume in qubit-microseconds."""
        return self._space_time_volume
    
    @property
    def space_time_volume_qubit_seconds(self) -> float:
        """Space-time volume in qubit-seconds."""
        return self._space_time_volume / 1e6
    
    @property
    def logical_gate_count(self) -> int:
        """Number of logical gate operations."""
        return self._logical_gate_count
    
    @property
    def wall_clock_time_us(self) -> float:
        """Wall-clock time in microseconds."""
        return self.get_wall_clock_time()
    
    def summary(self) -> Dict:
        """
        Get a summary of the resource estimation.
        
        Returns:
            Dictionary containing key resource metrics
        """
        return {
            'logical_qubits': self.config.logical_qubits,
            'code_distance': self.config.code_distance,
            'qubits_per_logical': self.config.qubits_per_logical,
            'data_qubits': self._data_qubits,
            'magic_state_qubits': self._magic_state_qubits,
            'compilation_qubits': self._compilation_qubits,
            'total_physical_qubits': self._total_physical_qubits,
            'target_runtime_us': self.config.target_runtime,
            'target_runtime_s': self.config.target_runtime / 1e6,
            'wall_clock_time_hours': self.get_wall_clock_time_hours(),
            'wall_clock_time_seconds': self.get_wall_clock_time_seconds(),
            'wall_clock_time_us': self.get_wall_clock_time(),
            'logical_gate_count': self._logical_gate_count,
            'physical_gate_count': self.get_physical_gate_count(),
            'space_time_volume_qubit_us': self._space_time_volume,
            'space_time_volume_qubit_s': self.space_time_volume_qubit_seconds,
            'logical_error_rate': self.get_logical_error_rate(),
            'algorithm_success_probability': self.get_algorithm_success_probability(),
            'physical_error_rate': self.config.digital_error_rate,
        }
    
    def __repr__(self) -> str:
        """String representation of the estimator."""
        return (
            f"DigitalResourceEstimator(\n"
            f"  logical_qubits={self.config.logical_qubits},\n"
            f"  code_distance={self.config.code_distance},\n"
            f"  total_physical_qubits={self._total_physical_qubits:,},\n"
            f"  runtime={self.config.target_runtime:.2e} μs "
            f"({self.get_wall_clock_time_hours():.2f} hours),\n"
            f"  space_time_volume={self._space_time_volume:.2e} qubit-μs\n"
            f")"
        )
