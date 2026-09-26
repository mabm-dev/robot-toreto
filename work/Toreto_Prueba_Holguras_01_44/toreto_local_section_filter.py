"""Select the longest loft-safe run of measured local sections.

Fusion folds a loft when a profile changes more than the distance to the next
profile.  The measured end sections are retained in the source JSON, while
this module isolates them from the first solid-volume validation.
"""
import math


def transition_ratio(first, second):
    """Return transverse change divided by longitudinal separation."""
    dz = second[0] - first[0]
    if dz <= 0:
        raise ValueError("Sections must be strictly ordered")
    centre_shift = math.hypot(second[1] - first[1], second[2] - first[2])
    radius_change = max(abs(second[3] - first[3]), abs(second[4] - first[4]))
    return (centre_shift + radius_change) / dz


def stable_run(sections, maximum_ratio=1.5, minimum_count=4):
    """Return the longest contiguous run without an abrupt transition.

    The returned dictionary makes every omitted measured section explicit.
    Ties prefer the run with the greatest longitudinal span.
    """
    if len(sections) < minimum_count:
        raise ValueError("Not enough measured sections")

    breaks = [
        index
        for index, pair in enumerate(zip(sections, sections[1:]))
        if transition_ratio(*pair) > maximum_ratio
    ]
    bounds = [-1] + breaks + [len(sections) - 1]
    candidates = []
    for left, right in zip(bounds, bounds[1:]):
        start = left + 1
        stop = right + 1
        if stop - start >= minimum_count:
            span = sections[stop - 1][0] - sections[start][0]
            candidates.append((stop - start, span, -start, start, stop))
    if not candidates:
        raise ValueError("No stable section run found")

    _, _, _, start, stop = max(candidates)
    return {
        "sections": sections[start:stop],
        "start": start,
        "stop": stop,
        "omitted_before": start,
        "omitted_after": len(sections) - stop,
        "breaks": breaks,
        "maximum_ratio": maximum_ratio,
    }
