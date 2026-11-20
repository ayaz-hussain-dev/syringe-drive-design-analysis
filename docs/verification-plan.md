# Proposed bench verification

The following checks would connect the computational study to a physical mechanism. They are a proposed test programme, not completed experimental results.

| Check | Method | Record |
|---|---|---|
| Carriage travel | Measure displacement for commanded screw revolutions at several carriage positions; approach from both directions. | Travel per revolution, repeatability and reversal lost motion. |
| Breakaway and running resistance | Use an inline force measurement over the stroke, first without a syringe and then with the selected syringe. | Guide drag, seal force and position dependence. |
| Fixture and base stiffness | Apply known axial loads through the represented motor-mount load path and measure base and fixture displacement separately. | Load-displacement slope, fixture contribution and repeatability. |
| Delivered volume | Dispense through defined tubing/back-pressure conditions at the reference flow; measure collected mass over repeated timed runs and convert using liquid density. | Mean flow, repeatability, start/stop behaviour and uncertainty. |
| Drive behaviour | Observe motion and motor response at the required speed using documented driver current, voltage and stepping settings. | Missed motion, temperature, starting behaviour and operating conditions. |

## Comparison with the calculations

Use measured syringe bore and active travel in the volume model. Replace the assumed pressure, seal friction, guide drag and efficiency inputs where measured or justified values are available.

The predicted base deformation is approximately 1.8 µm at the present load. Measurement resolution and fixture compliance must be considered before setting a correlation target; an instrument or fixture with comparable uncertainty would not resolve this prediction reliably.

Keep the same mounting arrangement and force application geometry when comparing test stiffness with the finite-element model. If the real restraint differs from the idealised fixed bores, update the model definition before interpreting agreement.

The ideal 0.6669 µL full-step volume is a displacement calculation. Experimental volume checks should quantify the effects of backlash, compliance, friction and liquid delivery.

Acceptance limits should be set from the intended use and measurement capability before testing. The present study establishes a comparison and a test basis, rather than a measured operating specification.
