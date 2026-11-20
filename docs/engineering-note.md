# Syringe-drive structural study

**Ayaz Hussain · November 2026**

## Objective and configuration

The study examines whether a local underside relief can reduce base-frame mass with little change in its displacement response to axial motor-mount loading.

The baseline central frame is 10 mm thick. The revised CATIA part uses a 2 mm pocket, leaving an 8 mm central frame and retaining the end regions around the existing mounting interfaces. The sketch spans 170 mm by 74 mm. This rectangle defines the cutter envelope; existing lattice openings mean the removed volume is smaller than the volume of a solid rectangular slab.

Assembly images document the reference configuration. The relief was evaluated in a separate revised base part. This keeps the assembly layout and the controlled structural variant identifiable.

[CAD definition and measurement evidence](cad-study.md)

## Sizing basis

The generic syringe reference uses a 14.57 mm bore and 60 mm active stroke. The drive reference is an M5 × 0.8 single-start screw and a 1.8° full-step motor.

For bore `d`, stroke `s`, pressure `p`, screw lead `L` and efficiency `η`:

```text
A = pi d² / 4
V [mL] = A [mm²] × s [mm] / 1000
F [N] = p [kPa] × A [mm²] / 1000 + Fseal + Fguide
T [N m] = F [N] × L [m/rev] / (2 pi η) + Tdrag
n [rpm] = Q [mL/min] × 1000 / (A [mm²] × L [mm/rev])
```

At the assumed 20 kPa pressure, 2 N seal friction and 0.5 N guide drag, the force is 5.834563 N. It is rounded to 5.835 N for the structural load case. With efficiency 0.20 and no added drag torque, the quasi-static torque is 3.714398 N·mm. A 2× sizing multiplier gives 7.428797 N·mm; it does not double the FEA load.

The calculated swept volume is 10.003690 mL. At 1 mL/min, the screw speed is 7.497233 rpm and the ideal full-step rate is 24.990778 Hz. A full step corresponds to 0.004 mm and 0.666913 µL under the rigid-displacement model.

The resistance and efficiency values are assumptions exposed in the input file. The code sweeps pressure and efficiency rather than treating the nominal point as a measured requirement. The 0.45 N·m motor holding rating is recorded as manufacturer reference data; available running torque remains unevaluated for the chosen driver and operating conditions.

## Finite-element idealisation

| Item | Definition |
|---|---|
| Analysis | Static structural, linear elastic base model |
| Body | One solid base; baseline and revised studied separately |
| Study material | PLA_Study_Isotropic |
| Young's modulus | 3000 MPa |
| Poisson's ratio | 0.35 |
| Density | 1240 kg/m³ |
| Structural elements | SOLID187, quadratic tetrahedra |
| Force application | SURF154 surface-effect elements |
| Applied total force | Global X = −5.835 N; Y = Z = 0 |
| Loaded geometry | Four flat annular screw-head bearing seats on the motor plate |
| Fixed geometry | Four split cylindrical faces on two lower mounting bores |
| Outputs | Total deformation, averaged nodal von Mises stress, support reaction |
| Reported result time | 1 s, the static load-step endpoint |

The force is the total distributed over all four selected seats. Each seat does not receive a separate 5.835 N force.

The fixed bores idealise rigid attachment to an external fixture. The case isolates the base response to motor-mount thrust. Carriage contact, guide load sharing, screw torque, fastener preload and flexible fixture behaviour are outside this structural idealisation.

The same material and load definition are present in all seven native solver inputs. The underlying solid uses material 1 with E = 3000 MPa, ν = 0.35 and density = 1.24 × 10⁻⁹ tonne/mm³. The latter is the solver's consistent tonne-mm unit representation of 1240 kg/m³.

## Mesh results

Counts below refer to the Mechanical solid mesh. Each solver model also contains 102 SURF154 elements used to apply the surface force.

| Design | Nominal size (mm) | Nodes | Solid elements | Minimum quality | Max deformation (mm) | Max averaged stress (MPa) |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 5 | 163,969 | 104,239 | 0.052929 | 0.0017866 | 0.12473 |
| Baseline | 4 | 180,618 | 115,101 | 0.090949 | 0.0017872 | 0.12490 |
| Baseline | 3 | 227,731 | 146,199 | 0.084755 | 0.0017878 | 0.12476 |
| Revised | 5 | 155,885 | 99,047 | 0.073882 | 0.0017931 | 0.12017 |
| Revised | 4 | 172,685 | 109,992 | 0.075351 | 0.0017936 | 0.12149 |
| Revised | 3 | 219,035 | 140,726 | 0.070517 | 0.0017943 | 0.12822 |
| Revised | 2 | 359,900 | 233,603 | 0.153180 | 0.0017957 | 0.12521 |

[Machine-readable results](../analysis/fea_results.csv)

Baseline 4→3 mm refinement changes the displacement maximum by +0.0336% and the stress maximum by −0.1121%. Revised 3→2 mm refinement changes them by +0.0780% and −2.3475%, respectively. Each change is normalised by the preceding coarser result.

The reported global stress maxima need not refer to an identical node or location after remeshing. Consequently, this is a global-maximum mesh-sensitivity study. A fixed-location stress trace, targeted refinement and a specified acceptance criterion would be needed for a stronger local stress-convergence claim. No absolute stress-error bound is inferred from the final percentage.

## Selected-case comparison

The selected output cases are baseline 3 mm and revised 2 mm. The baseline series is already stable at 3 mm, while the revised case received the additional 2 mm check.

| Quantity | Baseline 3 mm | Revised 2 mm |
|---|---:|---:|
| CAD volume imported to Mechanical | 306,360 mm³ | 293,300 mm³ |
| Solid-model base mass | 0.37988 kg | 0.36369 kg |
| Maximum total deformation | 1.7878 µm | 1.7957 µm |
| Maximum averaged von Mises stress | 0.12476 MPa | 0.12521 MPa |
| X support reaction | +5.835 N | +5.835 N |
| Total support reaction | 5.835 N | 5.835 N |

The mass saving is 16.19 g, or 4.2619%, using the displayed Mechanical mass values. The selected displacement increases by 0.4419%; the common 3 mm comparison gives an increase of 0.3636%.

The selected reaction components also support force balance. Baseline Y/Z reactions are approximately −8.0152 × 10⁻¹⁰ N and −1.0129 × 10⁻⁹ N; revised values are +7.4613 × 10⁻¹⁰ N and +8.3009 × 10⁻¹⁰ N. These are negligible relative to the applied axial force at the reported precision.

The small selected stress difference is comparable with the mesh variation. The useful design conclusion is the mass saving with a small displacement change under this idealised load case, rather than a demonstrated stress or strength advantage.

## Solver and evidence review

All seven supplied Workbench archives pass ZIP CRC checks and contain non-empty result files. Native logs record zero solver errors and two recurring warnings per case:

1. **Solver element-shape checking inactive.** This is the SHPP setting recorded by Mechanical APDL. Mechanical mesh-quality statistics are documented separately in the results CSV and screenshots.
2. **Material 2 has no MP/TB definition; material-energy output may be unavailable.** In each input, the element identified by the warning is the first SURF154 force-application element. The structural base uses material 1 with the PLA properties listed above. The study does not use material-energy output.

These warnings are retained in the review record; the cases are not described as warning-free.

The final revised mesh has minimum element quality 0.15318 and mean quality 0.78875. The native solver total is 233,705 elements, comprising 233,603 structural elements and 102 surface-effect elements. This explains the difference between the mesh count and solver total.

The revised 2 mm input/output files provide its node and element counts; its mesh-settings screenshot provides the quality statistic. Other mesh records and result-summary images support the remaining tabulated values. Displayed precision is retained.

Screenshots are preserved at their original pixel resolution. Full-screen captures have only the Windows taskbar border removed. Native plot exports are unchanged. No result label, contour, value or application branding has been retouched. Crop rectangles and file hashes are recorded in [image_processing.csv](../evidence/image_processing.csv).

## Interpretation and verification

The selected displacement response is stable over the sampled global meshes. The 2 mm relief is therefore a reasonable mass-saving candidate within this comparative model.

The material represents a homogeneous isotropic solid. Printed-part response depends on infill, orientation, process and specimen properties. Rigid supports also omit real fixture and fastener compliance. These factors limit transfer of the micrometre-scale prediction to a physical assembly.

The force, friction and efficiency assumptions set the load level. A physical verification programme should establish drag and force demand, carriage travel, fixture stiffness and delivered volume before making operating-performance claims. The [bench verification plan](verification-plan.md) defines the proposed checks.

## Technical references

- [STEPPERONLINE 17HS16-2004S1 full datasheet](https://files.omc-stepperonline.com/17HS16-2004S1_Full_Datasheet.pdf): step angle, dimensions, holding torque and dynamic axial-load screen.
- [STEPPERONLINE torque-speed curve](https://www.omc-stepperonline.com/download/17HS16-2004S1_Torque_Curve.pdf): operating-condition reference for a separate running-torque check.
- [Hamilton syringe dimensions](https://www.hamiltoncompany.com/knowledge-base/article/syringe-dimensions): nominal syringe-envelope reference.
- [Thomson Precision Screws catalogue](https://www.thomsonlinear.com/downloads/screws/Precision_Screws_ctuk.pdf): load/lead/efficiency torque relation.
- [NAFEMS: The Importance of Mesh Convergence](https://www.nafems.org/publications/knowledge-base/the-importance-of-mesh-convergence-part-1/): distinction between global refinement and convergence at a critical location.
- [Ansys 2026 R1: SURF154](https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/ans_elem/Hlp_E_SURF154.html): surface-force application and auxiliary surface-element behaviour.
