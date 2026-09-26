"""Native Fusion lofts from explicit cross sections (centimetres).

No fallback primitives: a failed loft aborts before replacement of the robot.
"""
import math
import adsk.core
import adsk.fusion


def section_curves(x, y, rx, ry):
    """Four straight edges and four exact circular quarters; no fitted splines."""
    radius = min(rx, ry) * .25
    q = radius / math.sqrt(2)
    a = (x-rx+radius, y+ry)
    b = (x+rx-radius, y+ry)
    c = (x+rx, y+ry-radius)
    d = (x+rx, y-ry+radius)
    e = (x+rx-radius, y-ry)
    f = (x-rx+radius, y-ry)
    g = (x-rx, y-ry+radius)
    h = (x-rx, y+ry-radius)
    return (
        (a, b), (b, (x+rx-radius+q, y+ry-radius+q), c),
        (c, d), (d, (x+rx-radius+q, y-ry+radius-q), e),
        (e, f), (f, (x-rx+radius-q, y-ry+radius-q), g),
        (g, h), (h, (x-rx+radius-q, y+ry-radius+q), a),
    )


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
            for curve in section_curves(x, y, rx, ry):
                points = [adsk.core.Point3D.create(px,py,0) for px,py in curve]
                if len(points) == 2:
                    entity = sketch.sketchCurves.sketchLines.addByTwoPoints(*points)
                else:
                    entity = sketch.sketchCurves.sketchArcs.addByThreePoints(*points)
                if not entity:
                    raise RuntimeError("Could not create straight/rounded section")
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
