"""Independent unit/consistency checks for the sizing model and study records."""
from __future__ import annotations

import copy
import csv
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("syringe_sizing", ROOT / "calculations/syringe_sizing.py")
sizing = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(sizing)


class SizingChecks(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "calculations/inputs.json").read_text())
        self.result = sizing.calculate(self.data)

    def test_force_against_SI_pressure_area(self):
        bore_m = self.data["geometry"]["barrel_bore_mm"] / 1000
        area_m2 = math.pi * bore_m**2 / 4
        pressure_pa = self.data["study_assumptions"]["back_pressure_kpa"] * 1000
        expected = pressure_pa * area_m2 + 2 + .5
        self.assertAlmostEqual(self.result["total_axial_force_n"], expected, places=11)
        self.assertAlmostEqual(expected, 5.83456341154022, places=11)

    def test_stroke_and_step_volume_conserve_volume(self):
        full_stroke_from_steps = (
            self.result["ideal_volume_per_full_step_ul"]
            * self.result["full_steps_for_full_stroke"] / 1000
        )
        self.assertAlmostEqual(full_stroke_from_steps, self.result["active_reference_volume_ml"], places=11)
        self.assertAlmostEqual(self.result["full_steps_for_full_stroke"], 15000)
        self.assertAlmostEqual(self.result["active_reference_volume_ml"], 10.00369023462066, places=11)

    def test_step_rate_reconstructs_flow(self):
        ml_per_min = self.result["ideal_full_step_rate_hz"] * self.result["ideal_volume_per_full_step_ul"] * 60 / 1000
        self.assertAlmostEqual(ml_per_min, self.data["study_assumptions"]["reference_flow_ml_per_min"], places=11)

    def test_screw_power_balance(self):
        omega = self.result["screw_speed_rpm"] * 2 * math.pi / 60
        mechanical_output = self.result["total_axial_force_n"] * self.result["plunger_speed_mm_per_s"] / 1000
        motor_input = self.result["nominal_quasi_static_torque_nm"] * omega
        eta = self.data["study_assumptions"]["nominal_screw_efficiency"]
        self.assertAlmostEqual(motor_input * eta, mechanical_output, places=12)

    def test_multiplier_scales_torque_without_scaling_force(self):
        other = copy.deepcopy(self.data)
        other["study_assumptions"]["torque_sizing_multiplier"] = 1
        reference = sizing.calculate(other)
        self.assertAlmostEqual(reference["total_axial_force_n"], self.result["total_axial_force_n"])
        self.assertAlmostEqual(self.result["multiplied_torque_target_nm"], 2 * reference["multiplied_torque_target_nm"])

    def test_holding_rating_is_not_substituted_for_running_torque(self):
        self.assertIsNone(self.result["running_torque_margin_to_multiplied_target"])
        self.assertFalse(self.result["holding_torque_used_as_running_torque"])
        other = copy.deepcopy(self.data)
        other["manufacturer_data"]["motor_holding_torque_nm"] = 100
        self.assertIsNone(sizing.calculate(other)["running_torque_margin_to_multiplied_target"])

    def test_axial_screen_threshold_and_sweep_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            sizing.create_outputs(self.data, Path(folder))
            with (Path(folder) / "force_torque_sensitivity.csv").open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            at_limit = [r for r in rows if float(r["total_axial_force_n"]) == 10]
            above_limit = [r for r in rows if float(r["total_axial_force_n"]) == 10.25]
            self.assertEqual(len(at_limit), 3)
            self.assertTrue(all(r["exceeds_motor_axial_limit"] == "False" for r in at_limit))
            self.assertTrue(all(r["exceeds_motor_axial_limit"] == "True" for r in above_limit))

    def test_invalid_geometric_and_efficiency_inputs(self):
        for section, key, value in [
                ("geometry", "barrel_bore_mm", 0),
                ("geometry", "screw_lead_mm_per_rev", -1),
                ("study_assumptions", "nominal_screw_efficiency", 0),
                ("study_assumptions", "nominal_screw_efficiency", 1.1)]:
            with self.subTest(key=key, value=value):
                other = copy.deepcopy(self.data)
                other[section][key] = value
                with self.assertRaises(ValueError):
                    sizing.calculate(other)


class StudyRecordChecks(unittest.TestCase):
    def test_mesh_and_equilibrium_records(self):
        with (ROOT / "analysis/fea_results.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 7)
        for row in rows:
            with self.subTest(design=row["design"], size=row["nominal_element_size_mm"]):
                self.assertAlmostEqual(float(row["reaction_x_N"]) + float(row["applied_force_x_N"]), 0, places=10)
                self.assertEqual(int(row["solver_total_elements"]), int(row["mesh_solid_elements"]) + 102)
                self.assertEqual(int(row["solver_error_count"]), 0)
                self.assertEqual(int(row["solver_warning_count"]), 2)
                self.assertGreater(float(row["element_quality_min"]), 0)

    def test_mass_consistent_with_displayed_volume_and_density(self):
        with (ROOT / "analysis/design_comparison.csv").open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        for row in rows:
            expected_kg = float(row["solid_model_volume_mm3"]) * 1.24e-6
            self.assertAlmostEqual(float(row["solid_model_mass_kg"]), expected_kg, delta=1e-5)
        difference_g = 1000 * (float(rows[0]["solid_model_mass_kg"]) - float(rows[1]["solid_model_mass_kg"]))
        self.assertAlmostEqual(difference_g, 16.19, places=8)

    def test_final_mesh_change_uses_previous_result_as_denominator(self):
        metrics = json.loads((ROOT / "analysis/comparison_metrics.json").read_text())
        self.assertAlmostEqual(metrics["revised_last_refinement_peak_stress_change_percent"],
                               100 * (.12521 - .12822) / .12822, places=10)


if __name__ == "__main__":
    unittest.main()
