# Actuator sizing and sensitivity

This calculation links syringe geometry and flow rate to axial force, screw speed and quasi-static torque. All study assumptions are in [inputs.json](inputs.json); the implementation is [syringe_sizing.py](syringe_sizing.py).

## Run

From the repository root:

```bash
python calculations/syringe_sizing.py
```

The numerical calculation uses only the Python standard library. Add `--plot` after installing the plotting requirements to regenerate the sensitivity figure.

## Inputs

| Quantity | Value | Basis |
|---|---:|---|
| Reference bore | 14.57 mm | Generic syringe-envelope model |
| Active stroke | 60 mm | Reference geometry and carriage-position range |
| Screw lead | 0.8 mm/rev | M5 × 0.8 single-start study specification |
| Full-step angle | 1.8° | Motor drawing |
| Flow rate | 1 mL/min | Study assumption |
| Back pressure | 20 kPa | Study assumption |
| Seal friction | 2 N | Study assumption |
| Guide drag | 0.5 N | Study assumption |
| Nominal efficiency | 0.20 | Study assumption |
| Efficiency sweep | 0.10 / 0.20 / 0.30 | Sensitivity inputs |
| Torque sizing multiplier | 2.0 | Torque-demand allowance |

A 10 N dynamic axial-load reference and 0.45 N·m holding rating are recorded for the motor model. The holding rating is not used as available running torque. The drawing is the [STEPPERONLINE 17HS16-2004S1 full datasheet](https://files.omc-stepperonline.com/17HS16-2004S1_Full_Datasheet.pdf).

## Equations

With `A` in mm², `d` in mm, pressure in kPa and screw lead in mm/rev:

```text
A = pi d² / 4
V [mL] = A × stroke / 1000
Fhydraulic [N] = pressure × A / 1000
Ftotal [N] = Fhydraulic + seal friction + guide drag
T [N m] = Ftotal × lead / (2000 pi efficiency) + added drag torque
Ttarget = torque sizing multiplier × T
speed [mm/min] = flow [mL/min] × 1000 / A
screw speed [rpm] = speed / lead
```

The nominal force is 5.834563 N, rounded to 5.835 N in FEA. Quasi-static torque is 0.003714398 N·m and the multiplied target is 0.007428797 N·m.

The 60 mm stroke gives 10.003690 mL. There are 200 full steps per revolution, 15,000 over the reference stroke, and an ideal 0.666913 µL displacement volume per full step.

## Interpretation

Pressure, drag and efficiency are assumptions, so their sweeps are retained alongside the nominal case. The 2× multiplier scales torque demand only. Starting resistance and acceleration require their own inputs when operating conditions are established.

The motor axial-load screen assumes that all axial force reaches the motor shaft. A nominal result below the drawing's 10 N reference is only a load-path screen; coupling retention and the actual thrust restraint still matter.

The available-running-torque input is empty. Use the [torque-speed curve](https://www.omc-stepperonline.com/download/17HS16-2004S1_Torque_Curve.pdf) with matching driver conditions before interpreting a torque margin.

## Outputs

- [Nominal summary](results/summary.json)
- [Force/efficiency sweep](results/force_torque_sensitivity.csv)
- [Pressure sweep](results/pressure_force_sensitivity.csv)
- [Sensitivity figure](results/force_torque_sensitivity.png)

The torque relation follows the load × lead / (2 pi × efficiency) relation in the [Thomson Precision Screws catalogue](https://www.thomsonlinear.com/downloads/screws/Precision_Screws_ctuk.pdf). Its catalogue efficiencies are not treated as measured values for the M5 screw/nut pair.
