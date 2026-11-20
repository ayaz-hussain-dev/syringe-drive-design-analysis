"""Syringe-drive quasi-static sizing and sensitivity study.

Run: python syringe_sizing.py
Optional plot: python syringe_sizing.py --plot
Standard-library calculations; only --plot requires matplotlib.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def positive(name, value):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def nonnegative(name, value):
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")
    return value


def efficiency(value):
    value = positive("Efficiency", value)
    if value > 1:
        raise ValueError("Efficiency must be a fraction between 0 and 1")
    return value


def torque_nm(force_n, lead_mm, eta, drag_nm=0.0):
    force_n = nonnegative("Force", force_n)
    lead_mm = positive("Lead", lead_mm)
    eta = efficiency(eta)
    drag_nm = nonnegative("Additional drag torque", drag_nm)
    return force_n * (lead_mm / 1000.0) / (2.0 * math.pi * eta) + drag_nm


def calculate(data):
    g = data["geometry"]
    a = data["study_assumptions"]
    m = data["manufacturer_data"]
    bore = positive("Barrel bore", g["barrel_bore_mm"])
    stroke = positive("Active stroke", g["active_stroke_mm"])
    lead = positive("Screw lead", g["screw_lead_mm_per_rev"])
    step_angle = positive("Motor full step", g["motor_full_step_deg"])
    eta = efficiency(a["nominal_screw_efficiency"])
    flow = positive("Reference flow", a["reference_flow_ml_per_min"])
    pressure = nonnegative("Back pressure", a["back_pressure_kpa"])
    seal = nonnegative("Seal friction", a["seal_friction_n"])
    guide = nonnegative("Guide drag", a["guide_drag_n"])
    drag = nonnegative("Additional drag torque", a["additional_drag_torque_nm"])
    multiplier = positive("Torque sizing multiplier", a["torque_sizing_multiplier"])
    reaction_fraction = nonnegative("Motor axial reaction fraction", a["motor_shaft_axial_reaction_fraction"])
    if reaction_fraction > 1:
        raise ValueError("Motor axial reaction fraction must be between 0 and 1")
    axial_limit = positive("Motor axial limit", m["motor_dynamic_axial_load_max_n"])
    for e in a["efficiency_sweep"]:
        efficiency(e)
    area = math.pi * bore**2 / 4.0
    # kPa = 0.001 N/mm^2; mm^3 = 0.001 mL.
    hydraulic_force = pressure * area / 1000.0
    total_force = hydraulic_force + seal + guide
    speed_mm_min = flow * 1000.0 / area
    rpm = speed_mm_min / lead
    steps_rev = 360.0 / step_angle
    axis_offset = abs(float(g["plunger_axis_y_mm"]) - float(g["screw_axis_y_mm"]))
    required = torque_nm(total_force, lead, eta, drag)
    shaft_reaction = total_force * reaction_fraction
    available = m["available_running_torque_nm"]
    if available is not None:
        available = positive("Available running torque", available)
    summary = {
        "status": data["status"],
        "barrel_area_mm2": area,
        "active_reference_volume_ml": area * stroke / 1000.0,
        "screw_revolutions_for_full_stroke": stroke / lead,
        "full_steps_per_revolution": steps_rev,
        "full_steps_for_full_stroke": stroke / lead * steps_rev,
        "travel_per_full_step_mm": lead / steps_rev,
        "ideal_volume_per_full_step_ul": area * lead / steps_rev,
        "reference_flow_ml_per_min": flow,
        "plunger_speed_mm_per_s": speed_mm_min / 60.0,
        "screw_speed_rpm": rpm,
        "ideal_full_step_rate_hz": rpm * steps_rev / 60.0,
        "reference_full_stroke_time_min": area * stroke / 1000.0 / flow,
        "assumed_back_pressure_kpa": pressure,
        "hydraulic_force_n": hydraulic_force,
        "assumed_seal_friction_n": seal,
        "assumed_guide_drag_n": guide,
        "total_axial_force_n": total_force,
        "assumed_nominal_screw_efficiency": eta,
        "nominal_quasi_static_torque_nm": required,
        "torque_sizing_multiplier": multiplier,
        "multiplied_torque_target_nm": required * multiplier,
        "plunger_to_screw_axis_offset_mm": axis_offset,
        "assumed_motor_axial_reaction_fraction": reaction_fraction,
        "screened_motor_axial_reaction_n": shaft_reaction,
        "manufacturer_motor_dynamic_axial_limit_n": axial_limit,
        "motor_axial_limit_exceeded_at_nominal_case": shaft_reaction > axial_limit,
        "motor_axial_limit_utilisation": shaft_reaction / axial_limit,
        "running_torque_margin_to_multiplied_target": None if available is None or required == 0 else available / (required * multiplier),
        "running_torque_check": "Not evaluated: no available running torque entered at the calculated RPM and chosen driver conditions" if available is None else "Screening only: input running torque must be justified at the calculated RPM and driver conditions",
        "holding_torque_used_as_running_torque": False,
        "limit_note": "Below the axial limit is a screening result, not validation of the coupling, thrust load path, operating margin or complete mechanism",
        "scope_note": "Assumed pressure/friction/efficiency; horizontal and quasi-static. Starting drag, breakaway variation and acceleration need separate checks. Ideal step volume is not demonstrated dispensing accuracy."
    }
    return summary


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def create_outputs(data, outdir, make_plot=False):
    result = calculate(data)
    outdir.mkdir(parents=True, exist_ok=True)
    a, g, m = data["study_assumptions"], data["geometry"], data["manufacturer_data"]
    start = nonnegative("Force sweep start", a["force_sweep_start_n"])
    stop = nonnegative("Force sweep stop", a["force_sweep_stop_n"])
    increment = positive("Force sweep step", a["force_sweep_step_n"])
    if stop < start:
        raise ValueError("Force sweep stop must not be below start")
    count = int(math.floor((stop-start)/increment+1e-9))+1
    if count > 100001:
        raise ValueError("Force sweep is too large")
    forces = [start + i*increment for i in range(count)]
    rows = []
    for eta in a["efficiency_sweep"]:
        for force in forces:
            torque = torque_nm(force, g["screw_lead_mm_per_rev"], eta, a["additional_drag_torque_nm"])
            reaction = force*a["motor_shaft_axial_reaction_fraction"]
            rows.append({"total_axial_force_n": force, "assumed_efficiency": eta,
                         "quasi_static_torque_nm": torque,
                         "multiplied_torque_target_nm": torque*a["torque_sizing_multiplier"],
                         "screened_motor_axial_reaction_n": reaction,
                         "exceeds_motor_axial_limit": reaction > m["motor_dynamic_axial_load_max_n"]})
    pressure_rows = []
    for pressure in a["pressure_sweep_kpa"]:
        pressure = nonnegative("Pressure sweep value", pressure)
        force = pressure*result["barrel_area_mm2"]/1000.0+a["seal_friction_n"]+a["guide_drag_n"]
        reaction = force*a["motor_shaft_axial_reaction_fraction"]
        pressure_rows.append({"assumed_pressure_kpa": pressure,
                              "assumed_seal_plus_guide_drag_n": a["seal_friction_n"]+a["guide_drag_n"],
                              "total_axial_force_n": force,
                              "nominal_efficiency": a["nominal_screw_efficiency"],
                              "quasi_static_torque_nm": torque_nm(force, g["screw_lead_mm_per_rev"], a["nominal_screw_efficiency"], a["additional_drag_torque_nm"]),
                              "screened_motor_axial_reaction_n": reaction,
                              "exceeds_motor_axial_limit": reaction > m["motor_dynamic_axial_load_max_n"]})
    (outdir/"summary.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    write_csv(outdir/"force_torque_sensitivity.csv", rows)
    write_csv(outdir/"pressure_force_sensitivity.csv", pressure_rows)
    if make_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError as exc:
            raise RuntimeError("Calculation results were saved. Install matplotlib to use --plot, or run without --plot.") from exc
        fig, ax = plt.subplots(figsize=(9.0, 5.6), layout="constrained")
        colours = ["#2878a8", "#dc9b2d", "#28865c"]
        for index, eta in enumerate(a["efficiency_sweep"]):
            values = [1000.0*torque_nm(f, g["screw_lead_mm_per_rev"], eta, a["additional_drag_torque_nm"]) for f in forces]
            ax.plot(forces, values, label=f"Assumed efficiency = {eta:.2f}", color=colours[index % len(colours)], linewidth=2.2)
        fraction = a["motor_shaft_axial_reaction_fraction"]
        if fraction > 0:
            threshold = m["motor_dynamic_axial_load_max_n"]/fraction
            if start <= threshold <= stop:
                ax.axvline(threshold, color="#a04444", linestyle="--", linewidth=1.6, label="Motor axial-load limit screen")
                if threshold < stop:
                    ax.axvspan(threshold, stop, facecolor="#b95d5d", alpha=.10)
        ax.scatter([result["total_axial_force_n"]], [1000.0*result["nominal_quasi_static_torque_nm"]], s=55, color="#343b43", zorder=5, label="Illustrative study point")
        ax.set(xlabel="Total axial force (N)", ylabel="Quasi-static drive torque (N mm)", xlim=(start, stop), ylim=(0, None))
        ax.set_title("M5 × 0.8 screw: force-to-torque sensitivity", loc="left", fontweight="bold", fontsize=14, pad=15)
        ax.text(0, 1.015, "Assumed efficiencies; no added startup drag or acceleration torque", transform=ax.transAxes, fontsize=9, color="#4d5660")
        ax.grid(alpha=.20)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(loc="upper left", frameon=True, fontsize=8.5)
        fig.savefig(outdir/"force_torque_sensitivity.png", dpi=180)
        plt.close(fig)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent
    parser.add_argument("--inputs", type=Path, default=root/"inputs.json")
    parser.add_argument("--output", type=Path, default=root/"results")
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.inputs.read_text(encoding="utf-8"))
    summary = create_outputs(data, args.output, args.plot)
    print("Syringe-drive sizing: preliminary assumptions, not measured requirements")
    for label, key, unit in [
        ("Reference volume", "active_reference_volume_ml", "mL"),
        ("Screw turns for full stroke", "screw_revolutions_for_full_stroke", "rev"),
        ("Axial force", "total_axial_force_n", "N"),
        ("Quasi-static torque", "nominal_quasi_static_torque_nm", "N m"),
        ("Multiplied torque target", "multiplied_torque_target_nm", "N m"),
        ("Screw speed", "screw_speed_rpm", "rpm"),
        ("Motor axial-limit utilisation", "motor_axial_limit_utilisation", "fraction")]:
        print(f"{label}: {summary[key]:.6g} {unit}")
    print(summary["running_torque_check"])
    print("Results:", args.output.resolve())


if __name__ == "__main__":
    main()
