
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ACCURACY IMPROVEMENT: Probability Calibration
# Fix overconfidence — model probabilities match real historical frequency
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import numpy as np
from sklearn.isotonic import IsotonicRegression
import pickle
import os

CALIBRATOR_FILE = "calibrator_model.pkl"

def calibrate_probability(raw_prob: float, calibrator=None) -> float:
    """
    Map raw model probability to real-world frequency.
    Example: model says 75% → actually happens 65% of the time → returns 0.65
    """
    if calibrator is None:
        if os.path.exists(CALIBRATOR_FILE):
            with open(CALIBRATOR_FILE, "rb") as f:
                calibrator = pickle.load(f)
        else:
            return max(0.01, min(0.99, raw_prob))
    
    calibrated = calibrator.transform(np.array([[raw_prob]]))[0]
    return float(max(0.01, min(0.99, calibrated)))

def fit_calibrator(historical_model_probs, actual_outcomes):
    """
    Train calibrator on settled historical data.
    probs: list of model probabilities (0-1)
    actuals: list of 0 or 1 (did outcome happen?)
    """
    ir = IsotonicRegression(out_of_bounds="clip")
    ir.fit(np.array(historical_model_probs), np.array(actual_outcomes))
    
    with open(CALIBRATOR_FILE, "wb") as f:
        pickle.dump(ir, f)
    
    return ir
