"""
Analog Quantum Simulation Module

This module provides the AnalogSimulator class for calculating feasible runtime
of analog quantum simulations based on system size and T1 coherence times.

The system T1 time is calculated as: 1/T1_system = sum(1/T1_i) for all qubits.
This determines the maximum physical runtime before decoherence dominates.
"""

import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class AnalogSimulatorConfig:
    """Configuration for analog quantum simulator."""
    
    # Circuit parameters
    circuit_width: int  # Number of qubits
    
    # T1 times (in microseconds)
    qubit_t1_times: Optional[List[float]] = None  # Individual qubit T1 times
    default_t1: float = 100.0  # Default T1 time if not specified (μs)
    
    # Error rates (for analog operations)
    measurement_error_rate: float = 0.01  # Measurement error rate
    
    # Simulation parameters
    target_fidelity: float = 0.99  # Target simulation fidelity
    
    # Additional constraints
    max_runtime_multiplier: float = 1.0  # Safety factor for maximum runtime (fraction of T1)
    
    def __post_init__(self):
        """Initialize qubit T1 times if not provided."""
        if self.qubit_t1_times is None:
            self.qubit_t1_times = [self.default_t1] * self.circuit_width
        elif len(self.qubit_t1_times) != self.circuit_width:
            raise ValueError(
                f"Number of T1 times ({len(self.qubit_t1_times)}) must match "
                f"circuit width ({self.circuit_width})"
            )


class AnalogSimulator:
    """
    Analog Quantum Simulator with T1-constrained runtime calculations.
    
    The simulator calculates the effective system T1 time based on individual
    qubit T1 times and uses this to determine the maximum feasible physical runtime.
    
    Key constraint: 1/T1_system = sum(1/T1_i) for all qubits
    """
    
    def __init__(self, config: AnalogSimulatorConfig):
        """
        Initialize the analog simulator.
        
        Args:
            config: Configuration object with circuit and T1 parameters
        """
        self.config = config
        self._system_t1 = None
        self._feasible_runtime = None
        
        # Calculate derived quantities
        self._calculate_system_t1()
        self._calculate_feasible_runtime()
    
    def _calculate_system_t1(self) -> float:
        """
        Calculate the effective system T1 time.
        
        The system T1 is determined by the parallel decoherence of all qubits:
        1/T1_system = sum(1/T1_i)
        
        Returns:
            System T1 time in microseconds
        """
        # Sum of reciprocals
        reciprocal_sum = sum(1.0 / t1 for t1 in self.config.qubit_t1_times)
        
        # System T1 is reciprocal of the sum
        self._system_t1 = 1.0 / reciprocal_sum
        
        return self._system_t1
    
    def _calculate_feasible_runtime(self) -> float:
        """
        Calculate the feasible runtime for the analog simulation.
        
        The runtime is constrained by the system T1 time. For analog simulation,
        we use a fraction of T1 to maintain acceptable fidelity.
        
        Returns:
            Feasible runtime in microseconds
        """
        # Maximum usable time is a fraction of system T1
        # Typical choice: T1/2 to T1 depending on target fidelity
        self._feasible_runtime = self._system_t1 * self.config.max_runtime_multiplier
        
        return self._feasible_runtime
    
    def get_decoherence_error(self, runtime: Optional[float] = None) -> float:
        """
        Calculate the decoherence error for a given runtime.
        
        Args:
            runtime: Physical runtime in μs (uses feasible_runtime if not specified)
            
        Returns:
            Decoherence error probability
        """
        if runtime is None:
            runtime = self._feasible_runtime
        
        # Error due to decoherence: 1 - exp(-t/T1)
        decoherence_error = 1.0 - np.exp(-runtime / self._system_t1)
        
        return decoherence_error
    
    def get_total_error(self, runtime: Optional[float] = None) -> float:
        """
        Calculate total error for analog simulation.
        
        For analog simulation, the primary error source is decoherence.
        
        Args:
            runtime: Physical runtime in μs (uses feasible_runtime if not specified)
            
        Returns:
            Total error probability
        """
        return self.get_decoherence_error(runtime)
    
    def get_fidelity(self, runtime: Optional[float] = None) -> float:
        """
        Calculate the fidelity for a given runtime.
        
        Args:
            runtime: Physical runtime in μs (uses feasible_runtime if not specified)
            
        Returns:
            Simulation fidelity
        """
        return 1.0 - self.get_total_error(runtime)
    
    # Public property accessors
    @property
    def system_t1(self) -> float:
        """Get the effective system T1 time (μs)."""
        return self._system_t1
    
    @property
    def feasible_runtime(self) -> float:
        """Get the feasible runtime (μs)."""
        return self._feasible_runtime
    
    @property
    def feasible_runtime_ms(self) -> float:
        """Get the feasible runtime in milliseconds."""
        return self._feasible_runtime / 1000.0
    
    @property
    def feasible_runtime_seconds(self) -> float:
        """Get the feasible runtime in seconds."""
        return self._feasible_runtime / 1e6
    
    def summary(self) -> Dict:
        """
        Get a summary of the analog simulation parameters.
        
        Returns:
            Dictionary containing key simulation metrics
        """
        return {
            'circuit_width': self.config.circuit_width,
            'system_t1_us': self._system_t1,
            'feasible_runtime_us': self._feasible_runtime,
            'feasible_runtime_ms': self.feasible_runtime_ms,
            'feasible_runtime_s': self.feasible_runtime_seconds,
            'fidelity': self.get_fidelity(),
            'decoherence_error': self.get_decoherence_error(),
            'total_error': self.get_total_error(),
        }
    
    def __repr__(self) -> str:
        """String representation of the simulator."""
        return (
            f"AnalogSimulator(\n"
            f"  circuit_width={self.config.circuit_width},\n"
            f"  system_t1={self._system_t1:.2f} μs,\n"
            f"  feasible_runtime={self._feasible_runtime:.2f} μs "
            f"({self.feasible_runtime_ms:.2f} ms)\n"
            f")"
        )
