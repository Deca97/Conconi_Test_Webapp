import fitdecode
import numpy as np
import tempfile
import os
import pwlf
from scipy.signal import savgol_filter

# ===============================
#   ESTRAZIONE DATI DA FILE FIT
# ===============================
def get_conconi_data(file_path):
    heart_rates = []
    speeds = []
    try:
        with fitdecode.FitReader(file_path) as fit_file:
            for frame in fit_file:
                if frame.frame_type == fitdecode.FIT_FRAME_DATA and frame.name == "record":
                    hr = frame.get_value('heart_rate')
                    sp = frame.get_value('speed')
                    if hr is not None and sp is not None:
                        heart_rates.append(hr)
                        speeds.append(sp)
    except Exception as e:
        return [], [], str(e)
    return heart_rates, speeds, None

# ===============================
#   SMOOTHING CON SAVITZKY-GOLAY
# ===============================
def smooth_data(data, window=11, polyorder=3):
    if len(data) < window:
        return np.array(data)
    if window % 2 == 0:
        window += 1
    return savgol_filter(np.array(data), window_length=window, polyorder=polyorder)

# ===============================
#   CALCOLO SOGLIA ANAEROBICA + CI
# ===============================
def calculate_anaerobic_threshold(hr, sp):
    if len(hr) < 10 or len(sp) < 10:
        return None, None, None, None, None
    hr = np.array(hr)
    sp = np.array(sp)

    hr_smooth = smooth_data(hr)
    sp_smooth = smooth_data(sp)

    try:
        pwlf_model = pwlf.PiecewiseLinFit(sp_smooth, hr_smooth)
        breaks = pwlf_model.fit(2)
        hr_fit = pwlf_model.predict(sp_smooth)
    except:
        return None, None, None, None, None

    threshold_speed = breaks[1]
    threshold_hr = pwlf_model.predict([threshold_speed])[0]
    idx = np.argmin(np.abs(sp_smooth - threshold_speed))

    residuals = hr_smooth - hr_fit
    ci_low, ci_high = bootstrap_threshold(sp_smooth, hr_fit, residuals)

    return threshold_hr, threshold_speed, idx, ci_low, ci_high

# ===============================
#   BOOTSTRAP CI
# ===============================
def bootstrap_threshold(sp, hr_fit, residuals, n_bootstrap=20, alpha=0.05):
    thresholds = []
    sp = np.array(sp)
    for _ in range(n_bootstrap):
        resampled_resid = np.random.choice(residuals, size=len(residuals), replace=True)
        hr_boot = hr_fit + resampled_resid
        try:
            pwlf_boot = pwlf.PiecewiseLinFit(sp, hr_boot)
            breaks_boot = pwlf_boot.fit(2)
            thresholds.append(breaks_boot[1])
        except:
            continue
    if len(thresholds) == 0:
        return None, None
    lower = np.percentile(thresholds, alpha/2*100)
    upper = np.percentile(thresholds, (1-alpha/2)*100)
    return lower, upper

# ===============================
#   CONVERSIONE VELOCITÀ -> PASSO
# ===============================
def speed_to_pace(speed):
    if speed <= 0:
        return "N/A"
    sec_per_km = 1000 / speed
    minutes = int(sec_per_km // 60)
    seconds = int(sec_per_km % 60)
    return f"{minutes}:{seconds:02d}"

# ===============================
#   ANALISI FILE FIT
# ===============================
def analyze_fit_file(file_buffer):
    import io
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file_buffer.read())
        tmp_path = tmp.name

    heart_rates, speeds, error = get_conconi_data(tmp_path)
    os.remove(tmp_path)

    if error:
        return {"error": error}
    if len(heart_rates) < 30:
        return {"error": "File troppo corto o con dati insufficienti."}

    # Rimuovi valori iniziali/finali rumorosi
    heart_rates = heart_rates[10:-10]
    speeds = speeds[10:-10]

    hr_threshold, speed_threshold, idx, ci_low, ci_high = calculate_anaerobic_threshold(heart_rates, speeds)
    if hr_threshold is None:
        return {"error": "Impossibile calcolare la soglia anaerobica."}

    pace = speed_to_pace(speed_threshold)

    return {
        "heartRate": heart_rates,
        "speed": speeds,
        "heart_rate": hr_threshold,
        "speed_threshold": speed_threshold,
        "pace": pace,
        "threshold_idx": idx,
        "ci_low": ci_low,
        "ci_high": ci_high
    }
