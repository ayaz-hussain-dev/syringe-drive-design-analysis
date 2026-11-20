# Evidence index

The figures below document the assembly, base revision, material, boundary conditions and mesh results. File names have been made consistent for this repository.

Full-screen captures have only the Windows taskbar border cropped away. All retained pixels are unchanged; native plot exports are unchanged files. [image_processing.csv](image_processing.csv) records original names, dimensions, crop rectangles and SHA-256 hashes. No labels, contours, application branding or result values have been retouched.

## Assembly and CAD

| View | Evidence |
|---|---|
| Assembly layout | [Isometric](screenshots/cad_assembly_isometric.png), [reverse](screenshots/cad_assembly_reverse.png), [side](screenshots/cad_assembly_side.png), [named isometric](screenshots/cad_named_isometric.png) |
| Constraint record | [Tree](screenshots/cad_constraints_tree.png), [display](screenshots/cad_constraints_display.png) |
| Carriage offsets | [54 mm](screenshots/cad_travel_54mm.png), [84 mm](screenshots/cad_travel_84mm.png), [114 mm](screenshots/cad_travel_114mm.png) |
| Base underside | [Baseline](screenshots/cad_baseline_underside.png), [revised](screenshots/cad_revised_underside.png) |
| Central thickness | [Baseline 10 mm](screenshots/cad_baseline_thickness.png), [revised 8 mm](screenshots/cad_revised_thickness.png) |
| Pocket definition | [2 mm depth](screenshots/cad_pocket_definition.png), [170 x 74 mm sketch](screenshots/cad_pocket_sketch.png) |
| Orthographic assembly views | [Front](screenshots/cad_front.png), [back](screenshots/cad_back.png), [left](screenshots/cad_left.png), [right](screenshots/cad_right.png), [top](screenshots/cad_top.png), [bottom](screenshots/cad_bottom.png) |

The assembly is the reference configuration. The revised base is documented as a separate analysis part. Travel images are manual position checks across a 60 mm offset range.

## Material and selected FEA cases

[PLA material definition](screenshots/pla_material_definition.png)

| Record | Baseline, 3 mm | Revised, 2 mm |
|---|---|---|
| Material assignment and mass | [Geometry properties](screenshots/baseline_3mm_material_mass.png) | [Geometry properties](screenshots/revised_2mm_material_mass.png) |
| Fixed support | [Scope](screenshots/baseline_3mm_fixed_support.png) | [Scope](screenshots/revised_2mm_fixed_support.png) |
| Applied force | [Components and scope](screenshots/baseline_3mm_force.png) | [Components and scope](screenshots/revised_2mm_force.png) |
| Mesh settings | [Settings](screenshots/baseline_3mm_mesh_settings.png), [statistics](screenshots/baseline_3mm_mesh_record.png) | [Settings and quality](screenshots/revised_2mm_mesh_settings.png) |
| Total deformation | [Application view](screenshots/baseline_3mm_deformation.png), [plot export](screenshots/baseline_3mm_deformation_export.png) | [Application view](screenshots/revised_2mm_deformation.png), [plot export](screenshots/revised_2mm_deformation_export.png) |
| Averaged equivalent stress | [Mesh view](screenshots/baseline_3mm_stress.png), [contour](screenshots/baseline_3mm_stress_contour.png), [detail](screenshots/baseline_3mm_stress_detail.png), [plot export](screenshots/baseline_3mm_stress_export.png) | [Mesh view](screenshots/revised_2mm_stress.png), [contour](screenshots/revised_2mm_stress_contour.png), [detail](screenshots/revised_2mm_stress_detail.png), [plot export](screenshots/revised_2mm_stress_export.png) |
| Support reaction | [Components and table](screenshots/baseline_3mm_reaction.png), [graphic export](screenshots/baseline_3mm_reaction_export.png) | [Components and table](screenshots/revised_2mm_reaction.png), [graphic export](screenshots/revised_2mm_reaction_export.png) |
| Results summary | See the individual result views above | [Summary](screenshots/revised_2mm_results_summary.png) |

The revised 2 mm mesh counts are cross-checked against its native solver input and log; a separate statistics screenshot was not supplied. The baseline 3 mm maxima are shown in the individual result views. Each contour retains its own legend, which should be used when comparing images.

## Other mesh cases

| Case | Mesh statistics and quality | Results |
|---|---|---|
| Baseline 5 mm | [Mesh record](screenshots/baseline_5mm_mesh_record.png) | [Summary](screenshots/baseline_5mm_results_summary.png) |
| Baseline 4 mm | [Mesh record](screenshots/baseline_4mm_mesh_record.png) | [Summary](screenshots/baseline_4mm_results_summary.png) |
| Revised 5 mm | [Mesh record](screenshots/revised_5mm_mesh_record.png) | [Summary](screenshots/revised_5mm_results_summary.png) |
| Revised 4 mm | [Mesh record](screenshots/revised_4mm_mesh_record.png) | [Summary](screenshots/revised_4mm_results_summary.png) |
| Revised 3 mm | [Mesh record](screenshots/revised_3mm_mesh_record.png) | [Summary](screenshots/revised_3mm_results_summary.png) |

The revised 3 mm stress maximum of 0.12822 MPa is also recorded in the separately supplied Mechanical stress views and archive-reopening check. Its summary capture truncates that particular display field.

## Numerical record

[All seven mesh cases](../analysis/fea_results.csv) include the solid-mesh counts, quality statistics, maxima, reaction, native solver total and warning count. [verification_record.json](../analysis/verification_record.json) describes the archive and native-input review. The original CAD files, STEP files, Workbench archives and binary result databases are retained separately from this screenshot-based portfolio repository.
