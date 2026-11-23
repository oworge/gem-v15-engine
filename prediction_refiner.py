# === GEM V15-DC-13.0 PREDICTION REFINER (npxG + LINEUP DELTA + MARKET CALIBRATION) ===
import math

# Market-specific shrinkage/calibration parameters learned from empirical football Brier scores
_MARKET_CALIBRATION = {
    "1": (0.94, 0.015), "X": (0.90, 0.028), "2": (0.94, 0.015),
    "1X": (0.95, 0.025), "X2": (0.95, 0.025), "12": (0.95, 0.025), "ESN": (0.95, 0.025),
    "DNB1": (0.94, 0.020), "DNB2": (0.94, 0.020),
    "O15": (0.93, 0.042), "U15": (0.92, 0.020),
    "O25": (0.93, 0.028), "U25": (0.93, 0.028),
    "O35": (0.91, 0.018), "U35": (0.92, 0.045),
    "BTTS_Y": (0.93, 0.028), "BTTS_N": (0.93, 0.028),
    "HT_X": (0.91, 0.036),
}

def refine_expected_goals(
    base_lh,
    base_la,
    npxg_for_h=None,
    npxg_against_h=None,
    npxg_for_a=None,
    npxg_against_a=None,
    sot_ratio_h=1.0,
    sot_ratio_a=1.0,
    missing_key_att_h=0,
    missing_key_def_h=0,
    missing_key_att_a=0,
    missing_key_def_a=0,
):
    lh = float(base_lh)
    la = float(base_la)

    # 1. Blend npxG & Shots-on-Target quality when available (65% npxG / 35% baseline goals)
    if npxg_for_h is not None and npxg_against_a is not None:
        xg_h = 0.5 * (float(npxg_for_h) + float(npxg_against_a))
        lh = (0.35 * lh) + (0.65 * xg_h)
    if npxg_for_a is not None and npxg_against_h is not None:
        xg_a = 0.5 * (float(npxg_for_a) + float(npxg_against_h))
        la = (0.35 * la) + (0.65 * xg_a)

    # Shot-on-target efficiency dampening (clamped +/- 8%)
    lh *= max(0.92, min(1.08, float(sot_ratio_h)))
    la *= max(0.92, min(1.08, float(sot_ratio_a)))

    # 2. Automated Key-Player Injury / Suspension Lambda Delta
    # Each missing key attacker reduces team xG by ~7.5%; each missing key defender raises opponent xG by ~6.5%
    lh *= max(0.75, 1.0 - (0.075 * int(missing_key_att_h)) + (0.065 * int(missing_key_def_a)))
    la *= max(0.75, 1.0 - (0.075 * int(missing_key_att_a)) + (0.065 * int(missing_key_def_h)))

    return round(max(0.30, min(3.80, lh)), 3), round(max(0.25, min(3.50, la)), 3)

def calibrate_market_probability(market_code, raw_prob):
    p = max(0.01, min(0.96, float(raw_prob)))
    code = str(market_code or "").upper().strip()
    if code.startswith("CS_"):
        return round(min(0.22, p * 0.96), 4)
    if code.startswith("HTFT_"):
        return round(min(0.65, (0.92 * p) + 0.015), 4)
    slope, intercept = _MARKET_CALIBRATION.get(code, (0.94, 0.022))
    cal = (slope * p) + intercept
    return round(max(0.03, min(0.90, cal)), 4)
