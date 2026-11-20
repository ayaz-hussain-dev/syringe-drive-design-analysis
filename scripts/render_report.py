"""Build the illustrated study report from the repository's records and images."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
    Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/Syringe_Drive_Study.pdf"
WIDTH = A4[0] - 108
NAVY = colors.HexColor("#243e52")
TEAL = colors.HexColor("#168273")
GREY = colors.HexColor("#52616c")
PALE = colors.HexColor("#f0f5f7")
RULE = colors.HexColor("#d5dfe5")

# Embed the fonts distributed with ReportLab so the PDF renders consistently.
FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
for name, filename in [("StudySans", "Vera.ttf"), ("StudySans-Bold", "VeraBd.ttf"),
                       ("StudySans-Italic", "VeraIt.ttf"), ("StudySans-BoldItalic", "VeraBI.ttf")]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / filename)))
pdfmetrics.registerFontFamily("StudySans", normal="StudySans", bold="StudySans-Bold",
                              italic="StudySans-Italic", boldItalic="StudySans-BoldItalic")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle("StudyTitle", fontName="StudySans-Bold", fontSize=27,
                          leading=31, textColor=NAVY, spaceAfter=13))
styles.add(ParagraphStyle("StudySection", fontName="StudySans-Bold", fontSize=20,
                          leading=25, textColor=NAVY, spaceAfter=12))
styles.add(ParagraphStyle("StudySubhead", fontName="StudySans-Bold", fontSize=11,
                          leading=14, textColor=TEAL, spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle("StudyBody", fontName="StudySans", fontSize=9.2,
                          leading=13.2, spaceAfter=8, textColor=colors.HexColor("#263744")))
styles.add(ParagraphStyle("StudySmall", parent=styles["StudyBody"], fontSize=8,
                          leading=11, textColor=GREY, spaceAfter=6))
styles.add(ParagraphStyle("StudyCell", parent=styles["StudyBody"], fontSize=8,
                          leading=10.4, spaceAfter=0))
styles.add(ParagraphStyle("StudyHeader", parent=styles["StudyCell"], fontName="StudySans-Bold",
                          textColor=colors.white))
styles.add(ParagraphStyle("StudyCaption", parent=styles["StudySmall"], fontSize=7.5,
                          leading=10, spaceAfter=6, alignment=TA_LEFT))
styles.add(ParagraphStyle("StudyMono", fontName="StudySans", fontSize=8.6,
                          leading=13, backColor=PALE, borderPadding=8, spaceBefore=3,
                          spaceAfter=11, textColor=NAVY))


def para(text, kind="StudyBody"):
    return Paragraph(text, styles[kind])


def table(rows, widths, compact=False):
    data = [[para(escape(str(cell)).replace("\n", "<br/>"), "StudyHeader" if i == 0 else "StudyCell")
             for cell in row] for i, row in enumerate(rows)]
    obj = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    obj.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5 if compact else 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5 if compact else 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, -1), (-1, -1), .45, RULE),
    ]))
    return obj


def picture(relative, width, max_height=1000):
    path = ROOT / relative
    with PILImage.open(path) as im:
        pixel_w, pixel_h = im.size
    scale = min(width / pixel_w, max_height / pixel_h)
    return Image(str(path), width=pixel_w * scale, height=pixel_h * scale)


def figure(relative, caption, width=WIDTH, max_height=1000):
    return KeepTogether([picture(relative, width, max_height), Spacer(1, 4),
                         para(caption, "StudyCaption")])


def pair(left, right, left_caption, right_caption, max_height=175):
    col = (WIDTH - 12) / 2
    cells = [[picture(left, col, max_height), picture(right, col, max_height)],
             [para(left_caption, "StudyCaption"), para(right_caption, "StudyCaption")]]
    obj = Table(cells, colWidths=[WIDTH / 2, WIDTH / 2], hAlign="LEFT")
    obj.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return KeepTogether([obj])


def heading(number, title, intro=None):
    result = [para("AYAZ HUSSAIN  /  SYRINGE DRIVE  /  " + number, "StudySmall"),
              para(title, "StudySection")]
    if intro:
        result.append(para(intro))
    return result


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(.5)
    canvas.line(48, 40, A4[0] - 48, 40)
    canvas.setFont("StudySans", 7.5)
    canvas.setFillColor(GREY)
    canvas.drawString(48, 27, "Syringe drive | CAD, actuator sizing and FEA | November 2026")
    canvas.drawRightString(A4[0] - 48, 27, str(doc.page))
    canvas.restoreState()


def main():
    with (ROOT / "analysis/fea_results.csv").open(newline="", encoding="utf-8") as file:
        mesh_rows = list(csv.DictReader(file))
    metrics = json.loads((ROOT / "analysis/comparison_metrics.json").read_text())
    sizing = json.loads((ROOT / "calculations/results/summary.json").read_text())
    story = []
    add = story.append

    # 1: Purpose, completed work and the principal comparison.
    add(para("AYAZ HUSSAIN  /  ENGINEERING PORTFOLIO  /  NOVEMBER 2026", "StudySmall"))
    add(para("Syringe drive", "StudyTitle"))
    add(para("CAD assembly, actuator sizing and base-frame FEA", "StudySubhead"))
    add(para("A local underside relief reduced the modelled base mass by <b>4.26%</b>. "
             "Under the same 5.835 N axial load, the selected simulation showed a "
             "<b>0.44% increase in maximum deformation</b>."))
    add(figure("evidence/screenshots/cad_assembly_isometric.png",
               "Reference CATIA assembly with syringe, carriage and simplified drive hardware.",
               max_height=255))
    add(table([
        ["Selected result", "Baseline", "Revised"],
        ["Central frame thickness", "10 mm", "8 mm"],
        ["Solid-model base mass", "379.88 g", "363.69 g"],
        ["Maximum total deformation", "0.0017878 mm", "0.0017957 mm"],
        ["Maximum averaged von Mises stress", "0.12476 MPa", "0.12521 MPa"],
        ["Selected nominal mesh size", "3 mm", "2 mm"],
    ], [WIDTH * .48, WIDTH * .26, WIDTH * .26], compact=True))
    add(Spacer(1, 8))
    add(para("Work completed", "StudySubhead"))
    add(para("CATIA assembly and constraints; reference hardware and carriage positions; "
             "a controlled base revision; parametric force, screw-torque and flow calculations; "
             "seven base-only structural mesh cases and reaction checks."))
    add(para("The mass reduction is 16.19 g. At the common 3 mm mesh setting, revised deformation "
             "is 0.36% higher than baseline. The comparison concerns a homogeneous solid model "
             "under one idealised load case.", "StudySmall"))
    add(PageBreak())

    # 2: CAD change and travel evidence.
    story.extend(heading("02", "CAD configuration and revision",
        "The assembly establishes the reference layout. The baseline and revised base were retained "
        "as separate analysis parts so that the geometry change could be compared directly."))
    add(pair("evidence/screenshots/cad_baseline_underside.png",
             "evidence/screenshots/cad_revised_underside.png",
             "Baseline underside: central frame retained at 10 mm.",
             "Revised underside: 2 mm relief, leaving the end regions in place.", max_height=155))
    add(table([
        ["Revision definition", "Value / check"],
        ["Pocket sketch envelope", "170 x 74 mm"],
        ["Pocket depth", "2 mm"],
        ["Measured remaining central thickness", "8 mm, from a 10 mm baseline"],
        ["Mechanical solid volume", "306,360 to 293,300 mm^3"],
        ["Mechanical solid mass at 1240 kg/m^3", "379.88 to 363.69 g"],
    ], [WIDTH * .51, WIDTH * .49], compact=True))
    add(Spacer(1, 8))
    add(para("The rectangular pocket crosses an existing lattice. Its sketch envelope therefore "
             "does not represent a solid rectangular volume of removed material."))
    add(para("Carriage position checks", "StudySubhead"))
    offsets = [54, 84, 114]
    col = WIDTH / 3
    travel = Table([
        [picture(f"evidence/screenshots/cad_travel_{x}mm.png", col - 8, 103) for x in offsets],
        [para(f"{x} mm offset", "StudyCaption") for x in offsets],
    ], colWidths=[col] * 3)
    travel.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 8)]))
    add(travel)
    add(para("The 54, 84 and 114 mm offsets span 60 mm of manual position checks. These images "
             "document the assembly arrangement; they are not a screw-motion simulation or a "
             "formal interference analysis."))
    add(para("Full-resolution pocket, thickness, constraint and orthographic views are indexed in "
             "evidence/README.md. Assembly images show the reference layout; the revised base is "
             "the separately evaluated structural variant.", "StudySmall"))
    add(PageBreak())

    # 3: The sizing model.
    story.extend(heading("03", "Actuator sizing",
        "The Python model links the reference syringe geometry and flow rate to axial force, "
        "screw speed and quasi-static torque. Pressure, friction and efficiency are exposed as inputs."))
    add(table([
        ["Input", "Study value", "Basis"],
        ["Reference bore / active stroke", "14.57 mm / 60 mm", "Reference geometry"],
        ["Screw lead / motor full-step angle", "0.8 mm/rev / 1.8 deg", "Single-start M5; motor drawing"],
        ["Back pressure / reference flow", "20 kPa / 1 mL/min", "Study assumptions"],
        ["Seal friction / guide drag", "2 N / 0.5 N", "Study assumptions"],
        ["Nominal screw efficiency", "0.20", "Sweep: 0.10 / 0.20 / 0.30"],
    ], [WIDTH * .40, WIDTH * .27, WIDTH * .33], compact=True))
    add(Spacer(1, 10))
    add(para("A = pi d^2 / 4<br/>F = p A + Fseal + Fguide<br/>"
             "T = F L / (2 pi eta) + Tdrag<br/>n = Q / (A L)", "StudyMono"))
    add(para("Use consistent units in these expressions. The implementation makes the mm, kPa, "
             "mL and SI conversions explicit; the torque multiplier is applied after calculating torque."))
    add(table([
        ["Calculated quantity", "Nominal result"],
        ["Reference swept volume", f"{sizing['active_reference_volume_ml']:.6f} mL"],
        ["Total axial force", f"{sizing['total_axial_force_n']:.6f} N; FEA uses 5.835 N"],
        ["Quasi-static torque / 2x torque target", "3.7144 / 7.4288 N mm"],
        ["Screw speed / full-step rate", "7.4972 rpm / 24.9908 Hz"],
        ["Ideal travel / volume per full step", "0.004 mm / 0.6669 microlitre"],
    ], [WIDTH * .52, WIDTH * .48], compact=True))
    add(Spacer(1, 7))
    add(figure("calculations/results/force_torque_sensitivity.png",
               "Force/efficiency sweep. The 2x factor scales torque demand; it does not double the structural load.",
               max_height=170))
    add(para("The 0.45 N m holding rating is not treated as available running torque. The 10 N "
             "manufacturer axial reference provides a load-path screen only. Operating torque, "
             "breakaway drag and delivered-volume accuracy require separate checks.", "StudySmall"))
    add(PageBreak())

    # 4: FEA model definition.
    story.extend(heading("04", "Structural model",
        "A static structural model isolates the base response to axial motor-mount thrust. "
        "The two designs use the same material and loading definition."))
    add(table([
        ["Model item", "Definition"],
        ["Body / behaviour", "One base solid; linear elastic"],
        ["Study material", "PLA_Study_Isotropic"],
        ["Elastic modulus / Poisson ratio / density", "3000 MPa / 0.35 / 1240 kg/m^3"],
        ["Structural mesh", "SOLID187 quadratic tetrahedra"],
        ["Total applied force", "Global X = -5.835 N; Y = Z = 0"],
        ["Force scope", "Four flat annular motor screw-head bearing seats"],
        ["Fixed support scope", "Four split cylindrical faces on two lower mounting bores"],
        ["Reported outputs", "Total deformation; averaged nodal von Mises stress; reaction"],
    ], [WIDTH * .39, WIDTH * .61], compact=True))
    add(Spacer(1, 12))
    add(pair("evidence/screenshots/revised_2mm_fixed_support.png",
             "evidence/screenshots/revised_2mm_force.png",
             "Fixed support on the lower mounting bores.",
             "One total force distributed across four seats.", max_height=165))
    add(para("The applied force is 5.835 N in total, rather than 5.835 N on each seat. "
             "The 1 s result is the static load-step endpoint, not a transient dispensing simulation."))
    add(para("Load path and restraint", "StudySubhead"))
    add(para("The fixed bores represent rigid attachment to an external fixture. Carriage contact, "
             "guide load sharing, screw torque, bolt preload and flexible fixture response are not "
             "resolved by this base-only idealisation."))
    add(para("All native inputs define the solid PLA material correctly. They also contain 102 "
             "SURF154 elements for the surface force. These auxiliary elements explain the difference "
             "between the Mechanical solid-mesh count and the solver element total.", "StudySmall"))
    add(PageBreak())

    # 5: Selected results, retaining each application's own contour scale.
    story.extend(heading("05", "Selected simulation results",
        "Baseline 3 mm and revised 2 mm are the selected cases. Each image retains its own "
        "displayed legend; colours should be read against that legend."))
    add(pair("evidence/screenshots/baseline_3mm_stress_export.png",
             "evidence/screenshots/revised_2mm_stress_export.png",
             "Baseline: maximum averaged von Mises stress 0.12476 MPa.",
             "Revised: maximum averaged von Mises stress 0.12521 MPa.", max_height=165))
    add(pair("evidence/screenshots/baseline_3mm_deformation_export.png",
             "evidence/screenshots/revised_2mm_deformation_export.png",
             "Baseline: maximum total deformation 0.0017878 mm.",
             "Revised: maximum total deformation 0.0017957 mm.", max_height=165))
    add(table([
        ["Comparison", "Result"],
        ["Base mass reduction", f"{metrics['mass_reduction_g']:.2f} g ({metrics['mass_reduction_percent']:.2f}%)"],
        ["Selected deformation increase", f"{metrics['selected_mesh_deformation_increase_percent']:.4f}%"],
        ["Common 3 mm deformation increase", f"{metrics['matched_3mm_deformation_increase_percent']:.4f}%"],
        ["Axial reaction, both selected cases", "+5.835 N; balances -5.835 N applied"],
        ["Transverse reactions", "Below 1.1 x 10^-9 N at displayed precision"],
    ], [WIDTH * .52, WIDTH * .48], compact=True))
    add(Spacer(1, 9))
    add(para("The mass saving is accompanied by a small change in the displacement response. "
             "Both selected peak stresses are about 0.125 MPa; the small difference is comparable "
             "with the mesh variation and does not establish a strength ranking."))
    add(para("These are solid-model comparative predictions. The predicted displacement is about "
             "1.8 micrometres, so real fixture compliance and measurement resolution would matter "
             "in a physical correlation exercise.", "StudySmall"))
    add(PageBreak())

    # 6: All mesh cases with the actual observed changes.
    story.extend(heading("06", "Mesh refinement study",
        "Nominal sizes were reduced through three baseline and four revised cases. Counts refer "
        "to the Mechanical structural mesh; each solver total adds 102 loading elements."))
    rows = [["Design", "Size\n(mm)", "Nodes", "Solid\nelements", "Min.\nquality", "Max. u\n(mm)", "Max. stress\n(MPa)"]]
    for r in mesh_rows:
        rows.append([r["design"].title(), r["nominal_element_size_mm"],
                     f"{int(r['mesh_nodes']):,}", f"{int(r['mesh_solid_elements']):,}",
                     f"{float(r['element_quality_min']):.5f}", r["maximum_total_deformation_mm"],
                     r["maximum_averaged_von_mises_MPa"]])
    add(table(rows, [61, 43, 71, 71, 64, 92, WIDTH - 402], compact=True))
    add(Spacer(1, 12))
    add(figure("docs/figures/mesh_sensitivity.png",
               "Independent remeshes: displacement is stable over the sampled range; peak stress is non-monotonic.",
               max_height=220))
    add(table([
        ["Last refinement", "Deformation change", "Peak stress change"],
        ["Baseline 4 to 3 mm", "+0.0336%", "-0.1121%"],
        ["Revised 3 to 2 mm", "+0.0780%", "-2.3475%"],
    ], [WIDTH * .4, WIDTH * .3, WIDTH * .3], compact=True))
    add(Spacer(1, 9))
    add(para("Changes use the preceding coarser result as the denominator. The 2.35% final stress "
             "change is observed sensitivity, not an absolute error bound. Global peaks can change "
             "location after remeshing; a fixed-location trace and targeted refinement would be "
             "needed for a stronger local stress-convergence claim."))
    add(para("The final revised minimum and mean element qualities are 0.15318 and 0.78875. "
             "Quality values are retained as mesh diagnostics, rather than a stand-alone accuracy criterion.", "StudySmall"))
    add(PageBreak())

    # 7: Audit, physical verification and references.
    story.extend(heading("07", "Review and next verification"))
    add(para("Archive and solver review", "StudySubhead"))
    add(para("All seven supplied archives pass ZIP CRC checks and contain non-empty result files. "
             "Their native inputs agree on the solid material, element types and applied force. "
             "Logs record zero solver errors and two recurring warnings per case:"))
    add(para("<b>Element-shape checking inactive:</b> the solver SHPP setting is off; Mechanical "
             "mesh-quality statistics are recorded separately. <b>Material 2 lacks MP/TB data:</b> "
             "the flagged element is the first SURF154 loading element in each case. The structural "
             "solid uses material 1 with the PLA properties. Material-energy output is not used here."))
    add(para("The warnings are retained in analysis/verification_record.json. This review uses "
             "the supplied inputs, logs, result records and images; it is not an independent solver rerun.", "StudySmall"))
    add(para("Physical verification priorities", "StudySubhead"))
    add(table([
        ["Check", "Measurement"],
        ["Travel and reversal", "Displacement per revolution; repeatability; lost motion"],
        ["Resistance", "Breakaway and running force across the stroke"],
        ["Base and fixture stiffness", "Known axial load versus measured displacement"],
        ["Delivered volume", "Collected mass over repeated timed runs under defined back pressure"],
        ["Drive behaviour", "Motion at documented driver voltage, current and step settings"],
    ], [WIDTH * .34, WIDTH * .66], compact=True))
    add(Spacer(1, 7))
    add(para("These are proposed checks, not experimental results. The homogeneous PLA model "
             "does not resolve print orientation, infill or process variation. Measured drag, "
             "material properties and fixture compliance would be needed to extend the comparison."))
    add(para("Technical references", "StudySubhead"))
    refs = [
        ("STEPPERONLINE - motor full datasheet", "https://files.omc-stepperonline.com/17HS16-2004S1_Full_Datasheet.pdf"),
        ("STEPPERONLINE - torque-speed curve", "https://www.omc-stepperonline.com/download/17HS16-2004S1_Torque_Curve.pdf"),
        ("Thomson - Precision Screws catalogue", "https://www.thomsonlinear.com/downloads/screws/Precision_Screws_ctuk.pdf"),
        ("NAFEMS - The Importance of Mesh Convergence", "https://www.nafems.org/publications/knowledge-base/the-importance-of-mesh-convergence-part-1/"),
        ("Ansys 2026 R1 - SURF154", "https://ansyshelp.ansys.com/public/views/secured/corp/v261/en/ans_elem/Hlp_E_SURF154.html"),
    ]
    for label, url in refs:
        add(para(f'<link href="{escape(url)}" color="#168273">{escape(label)}</link>', "StudySmall"))
    add(para("Evidence and design note", "StudySubhead"))
    add(para("Full-resolution evidence, calculation inputs, results CSVs and reproduction scripts "
             "accompany this report. Screenshots retain their original pixels; only desktop borders "
             "were cropped. Selected component geometry was adapted from an existing model. "
             "The work covers the assembly and reference hardware, base revision, sizing and FEA. "
             "Applicable notices are in THIRD_PARTY_NOTICES.md.", "StudySmall"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=48, leftMargin=48,
                            topMargin=45, bottomMargin=54, title="Syringe Drive - CAD, Actuator Sizing and FEA",
                            author="Ayaz Hussain", subject="Comparative base-frame structural study")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Saved report to", OUT)


if __name__ == "__main__":
    main()
