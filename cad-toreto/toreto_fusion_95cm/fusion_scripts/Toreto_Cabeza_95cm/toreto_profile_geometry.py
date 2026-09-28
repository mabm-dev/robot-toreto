"""Native Fusion lofts from explicit cross sections (centimetres).

No fallback primitives: a failed loft aborts before replacement of the robot.
"""
import math
import adsk.core
import adsk.fusion


def loft(manager, sections, label):
    """sections: ascending (z, centre_x, centre_y, radius_x, radius_y, exponent).

    Coordinates are model coordinates, not canvas pixels. Four spline arcs per
    section preserve vertex correspondence and allow independent width/depth.
    """
    if len(sections) < 2:
        raise ValueError("A loft needs at least two sections")
    previous = -math.inf
    for z, x, y, rx, ry, exponent in sections:
        if not all(math.isfinite(v) for v in (z, x, y, rx, ry, exponent)):
            raise ValueError("Non-finite profile")
        if z <= previous or min(rx, ry) <= 0 or exponent < 2:
            raise ValueError("Invalid or unordered profile")
        previous = z
    design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    occurrence = design.rootComponent.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    component = occurrence.component
    component.name = "TEMP_PERFILES_" + label
    try:
        profiles = []
        for index, (z, x, y, rx, ry, exponent) in enumerate(sections):
            plane_input = component.constructionPlanes.createInput()
            if not plane_input.setByOffset(component.xYConstructionPlane, adsk.core.ValueInput.createByReal(z)):
                raise RuntimeError("Could not define section plane")
            plane = component.constructionPlanes.add(plane_input)
            sketch = component.sketches.add(plane)
            sketch.name = label + "_" + str(index)
            for quadrant in range(4):
                points = adsk.core.ObjectCollection.create()
                for sample in range(9):
                    angle = (quadrant + sample / 8) * math.pi / 2
                    c, s = math.cos(angle), math.sin(angle)
                    px = x + rx * math.copysign(abs(c) ** (2 / exponent), c)
                    py = y + ry * math.copysign(abs(s) ** (2 / exponent), s)
                    # Snap quadrantal coordinates; fractional powers magnify
                    # floating point residue and would leave open profiles.
                    if abs(c) < 1e-12: px = x
                    if abs(s) < 1e-12: py = y
                    points.add(adsk.core.Point3D.create(px, py, 0))
                if not sketch.sketchCurves.sketchFittedSplines.add(points):
                    raise RuntimeError("Could not create profile spline")
            if sketch.profiles.count != 1:
                raise RuntimeError(f"{label}: section {index} is not a single closed profile")
            profiles.append(sketch.profiles.item(0))
        inp = component.features.loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        inp.isSolid = True
        inp.isClosed = False
        inp.isTangentEdgesMerged = True
        for profile in profiles:
            inp.loftSections.add(profile)
        feature = component.features.loftFeatures.add(inp)
        if not feature or feature.bodies.count != 1 or not feature.bodies.item(0).isSolid:
            raise RuntimeError(label + ": loft did not produce one solid")
        result = manager.copy(feature.bodies.item(0))
        if not result or not result.isSolid:
            raise RuntimeError(label + ": could not copy loft")
        return result
    finally:
        if occurrence.isValid and not occurrence.deleteMe():
            raise RuntimeError("Could not remove temporary construction: " + label)
