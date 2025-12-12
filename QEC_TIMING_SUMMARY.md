# QEC Wall-Clock Time: From Literature to Your Model

## The Core Formula (From Literature)

For surface-code error correction, the total wall-clock time for fault-tolerant quantum computation is:

$$T_{\text{wall}} = N_T \times d \times t_{\text{cycle}}$$

Where:
- **$N_T$** = number of T gates (non-Clifford) in the circuit
- **$d$** = code distance (typically 25-35 for $p_L \lesssim 10^{-10}$)
- **$t_{\text{cycle}}$** ≈ 1 µs (syndrome measurement + decoding cycle time)

## Literature Parameters (Reference: Gidney & Ekera 2021, etc.)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| Logical T-gate latency | ~100 µs | Includes magic state distillation + feed-forward |
| QEC cycle time | ~1 µs | Syndrome extraction round |
| Code distance (for $p_L \sim 10^{-10}$) | 25-35 | Depends on physical error rate |
| Physical gate time | 10-100 ns | (varies by platform) |

## Concrete Example: 0.5 µs Simulation

**Scenario:** Simulate 0.5 µs of Hamiltonian evolution on 100 qubits

**Circuit analysis (with Trotter decomposition):**
- Evolution time: 0.5 µs
- Trotter steps: ~100-1000 (depending on accuracy)
- T gates per step: ~10 (typical)
- Total T gates: $N_T \sim 1000$

**QEC requirements:**
- Physical error rate: $p \sim 10^{-3}$
- Target logical error: $p_L \sim 10^{-10}$
- Required code distance: $d \sim 25-30$

**Wall-clock time:**
$$T_{\text{wall}} = 1000 \times 30 \times 1 \text{ µs} = 30,000 \text{ µs} = \boxed{30 \text{ ms}}$$

Compare to:
- **Analog simulation** (no QEC): 0.5 µs wall-clock
- **Digital + full QEC**: 30 ms wall-clock
- **Slowdown factor**: **60,000×**

## How Your Model Relates to Literature Formula

Your model uses:
$$T_{\text{wall}} = T_{\text{logical}} \times \text{QEC\_overhead\_factor}$$

Where:
$$\text{QEC\_overhead\_factor} = (1 + d/10) \times (1 + 0.2) \times 1.5 \approx 6-7 \text{ for } d \approx 25$$

**For short simulations (0.5 µs):**
- Model prediction: $T_{\text{wall}} = 0.5 \text{ µs} \times 6.3 \approx 3 \text{ µs}$
- Literature formula: $T_{\text{wall}} = 1000 \times 30 \times 1 = 30 \text{ ms}$

**Key difference:** Your model assumes a simple overhead multiplier, but the literature formula shows that wall-clock time actually scales with **circuit depth** (number of T gates), not just with simulation time.

## Why This Matters for Analog QEC

### The Opportunity

Analog quantum simulators have NO intrinsic T-gate latency (no discrete gates). If you could:

1. **Encode logical qubits** directly in analog simulation platform
2. **Apply weak/continuous error correction** instead of full surface codes
3. **Avoid the 100 µs T-gate latency** by working continuously

Then you could potentially execute complex simulations at **analog timescales** with **partial error correction**.

### The Challenge

To compete with digital FTQC, analog QEC must:
- Achieve logical error rates $p_L \lesssim 10^{-10}$ without discrete syndrome extraction
- Scale to 100+ logical qubits while maintaining coherence
- Reduce code distance requirements (continuous vs. discrete operations)

### The Timeline Comparison

| Scenario | Analog | Analog + Weak QEC | Digital + Full QEC |
|----------|--------|-------------------|-------------------|
| **0.5 µs sim** | 0.5 µs (coherence limited) | ?  (needs validation) | 30 ms |
| **1.0 µs sim** | 1.0 µs | ? | 60 ms |
| **10 µs sim** | Impossible (T1 ≲ 50 µs) | ? | 600 ms |
| **100 µs sim** | Impossible | ? | Hours |

## Validation Questions for Your Model

1. **Are you accounting for circuit depth?**
   - Your current model uses $T_{\text{wall}} = T_{\text{logical}} \times \text{overhead}$
   - Literature formula is $T_{\text{wall}} = N_T \times d \times t_{\text{cycle}}$
   - These differ significantly for variable-depth circuits

2. **What's the implicit assumption about T-gate density?**
   - If $N_T \sim 2000$ T gates per µs of evolution, then your overhead factor matches literature
   - Need to make this explicit

3. **For analog QEC, what error correction mechanism?**
   - Continuous monitoring (squeezed light, feedback)?
   - Periodically-reset syndrome extraction?
   - Something else?

## Next Steps

1. **Update your DigitalResourceEstimator** to accept T-gate count as input
2. **Calculate wall-clock time** using both formulas and compare
3. **For analog QEC**, specify what "weak" error correction means operationally
4. **Create benchmark scenarios** comparing all three approaches (analog, analog+QEC, digital+QEC)
