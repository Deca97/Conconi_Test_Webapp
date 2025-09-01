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

import numpy as np
import pwlf
from scipy.signal import savgol_filter

def smooth_data(data, window=11, polyorder=3):
    """Applica filtro Savitzky-Golay ai dati."""
    if len(data) < window:
        return np.array(data)
    if window % 2 == 0:
        window += 1
    return savgol_filter(np.array(data), window_length=window, polyorder=polyorder)

def remove_outliers_pair(hr, sp):
    """Rimuove coppie HR/Speed che sono outlier basati sull'IQR."""
    hr = np.array(hr)
    sp = np.array(sp)

    def iqr_filter(x):
        q1, q3 = np.percentile(x, [25, 75])
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return (x >= lower) & (x <= upper)

    hr_mask = iqr_filter(hr)
    sp_mask = iqr_filter(sp)
    mask = hr_mask & sp_mask  # mantiene solo coppie valide
    return hr[mask], sp[mask]

def calculate_anaerobic_threshold(hr, sp, window=11, polyorder=3):
    """
    Calcola la soglia anaerobica da serie HR e velocità (Speed).
    Restituisce: hr_threshold, speed_threshold, idx, ci_low, ci_high, warning
    """
    warning = None

    # 1️⃣ Controllo lunghezza dati
    if len(hr) < 10 or len(sp) < 10:
        return None, None, None, None, None, "Dati troppo corti per calcolare la soglia."

    # 2️⃣ Rimozione outlier
    hr_filtered, sp_filtered = remove_outliers_pair(hr, sp)
    if len(hr_filtered) < 10:
        return None, None, None, None, None, "Troppi outlier, dati insufficienti."

    # 3️⃣ Smoothing
    hr_smooth = smooth_data(hr_filtered, window=window, polyorder=polyorder)
    sp_smooth = smooth_data(sp_filtered, window=window, polyorder=polyorder)

    # 4️⃣ Controllo correlazione preliminare
    corr = np.corrcoef(sp_smooth, hr_smooth)[0, 1]
    if abs(corr) < 0.5:
        return None, None, None, None, None, "Scarsa correlazione tra HR e velocità, test non valido."

    # 5️⃣ Fit piecewise lineare (PWLF)
    try:
        pwlf_model = pwlf.PiecewiseLinFit(sp_smooth, hr_smooth)
        breaks = pwlf_model.fit(2)
        hr_fit = pwlf_model.predict(sp_smooth)
    except Exception as e:
        return None, None, None, None, None, f"Errore nel fit PWLF: {e}"

    threshold_speed = breaks[1]
    threshold_hr = pwlf_model.predict([threshold_speed])[0]
    idx = int(np.argmin(np.abs(sp_smooth - threshold_speed)))

    # 6️⃣ Calcolo intervallo di confidenza con bootstrap (funzione esterna)
    residuals = hr_smooth - hr_fit
    try:
        ci_low, ci_high = bootstrap_threshold(sp_smooth, hr_fit, residuals)
    except:
        ci_low, ci_high = None, None

    # 7️⃣ Controllo stabilità soglia
    if ci_low and ci_high:
        if abs(ci_high - ci_low) / threshold_speed > 0.2:
            warning = "Intervallo di confidenza molto ampio, soglia poco stabile."

    return threshold_hr, threshold_speed, idx, ci_low, ci_high, warning



# ===============================
#   BOOTSTRAP CI
# ===============================
def bootstrap_threshold(sp, hr_fit, residuals, n_bootstrap=50, alpha=0.05):
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
    import io, tempfile, os

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
    heart_rates = heart_rates[20:-10]
    speeds = speeds[20:-10]

    hr_threshold, speed_threshold, idx, ci_low, ci_high, warning = calculate_anaerobic_threshold(heart_rates, speeds)
    if hr_threshold is None:
        msg = "Impossibile calcolare la soglia anaerobica."
        if warning:
            msg += f" ({warning})"
        return {"error": msg}

    pace = speed_to_pace(speed_threshold)

    return {
        "heartRate": heart_rates,
        "speed": speeds,
        "heart_rate": hr_threshold,
        "speed_threshold": speed_threshold,
        "pace": pace,
        "threshold_idx": idx,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "warning": warning
    }
