"""
Unit conversions for the GC-01.

The device only ever measures one physical thing, ionization events in the
GM tube, which become counts. Everything else on the display (the five dose
units in the photos: uSv/h, uGy/h, mR/h, CPS, CPM) is a conversion applied to
that count rate. So we keep counts as the source of truth and convert outward.

The conversion from count rate to dose rate uses the tube sensitivity, which
Rad Pro reports in cpm per uSv/h. Always read it off the device with
get_tube_sensitivity rather than hardcoding, because the value depends on the
tube and on the calibration source. The Amazon listing quotes 80 cpm/uSv/h
for Co-60, while the Rad Pro GC-01 default is often around 153.8 cpm/uSv/h.
These are not interchangeable, so pull the live value.
"""


def cpm_to_cps(cpm):
    """Counts per minute to counts per second."""
    return cpm / 60.0


def cps_to_cpm(cps):
    """Counts per second to counts per minute."""
    return cps * 60.0


def cpm_to_usv_h(cpm, sensitivity_cpm_per_usv_h):
    """
    Count rate to microsievert per hour.

    sensitivity is cpm per uSv/h, so dividing count rate by it gives uSv/h.
    """
    if sensitivity_cpm_per_usv_h <= 0:
        raise ValueError("Sensitivity must be positive")
    return cpm / sensitivity_cpm_per_usv_h


def usv_h_to_cpm(usv_h, sensitivity_cpm_per_usv_h):
    """Microsievert per hour back to count rate."""
    return usv_h * sensitivity_cpm_per_usv_h


def usv_h_to_ugy_h(usv_h):
    """
    Microsievert per hour to microgray per hour.

    For gamma and x-rays the radiation weighting factor is 1, so for this
    device sievert and gray track one to one. This is an approximation that
    holds for the photon energies the GC-01 is meant for.
    """
    return usv_h


def usv_h_to_mr_h(usv_h):
    """
    Microsievert per hour to milliroentgen per hour.

    Using the common conversion 1 R is about 10 mSv (10000 uSv) for air,
    which gives 1 mR equal to 10 uSv, so mR/h equals uSv/h divided by 10.
    This is the standard rough conversion used by these consumer meters.
    """
    return usv_h / 10.0


def all_units(cpm, sensitivity_cpm_per_usv_h):
    """
    Convert a single count rate into every unit the GC-01 display can show.

    Returns a dict so a logger or dashboard can render whichever the user wants.
    """
    usv_h = cpm_to_usv_h(cpm, sensitivity_cpm_per_usv_h)
    return {
        "cpm": cpm,
        "cps": cpm_to_cps(cpm),
        "usv_h": usv_h,
        "ugy_h": usv_h_to_ugy_h(usv_h),
        "mr_h": usv_h_to_mr_h(usv_h),
    }
