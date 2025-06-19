import fitdecode
import numpy as np
import tempfile
import os

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

def calculate_anaerobic_threshold(hr, sp):
    if not hr or not sp:
        return None, None
    window_size = 10
    smooth_hr = np.convolve(hr, np.ones(window_size)/window_size, mode='valid')
    smooth_sp = np.convolve(sp, np.ones(window_size)/window_size, mode='valid')
    min_len = min(len(smooth_hr), len(smooth_sp))
    smooth_hr = smooth_hr[:min_len]
    smooth_sp = smooth_sp[:min_len]
    diffs = np.diff(smooth_hr) / np.diff(smooth_sp)
    lookback = 20
    for i in range(lookback, len(diffs)):
        avg_prev = np.mean(diffs[i-lookback:i])
        current_slope = diffs[i]
        if current_slope < 0.8 * avg_prev:
            idx = i + window_size // 2
            if idx < len(hr) and idx < len(sp):
                return hr[idx], sp[idx]
    return None, None

def speed_to_pace(speed):
    if speed == 0:
        return "N/A"
    sec_per_km = 1000 / speed
    minutes = int(sec_per_km // 60)
    seconds = int(sec_per_km % 60)
    return f"{minutes}:{seconds:02d}"

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

    heart_rates = heart_rates[10:-10]
    speeds = speeds[10:-10]

    hr_threshold, speed_threshold = calculate_anaerobic_threshold(heart_rates, speeds)

    if hr_threshold is not None and speed_threshold is not None:
        pace = speed_to_pace(speed_threshold)
        return {
            "heartRate": heart_rates,
            "speed": speeds,
            "heart_rate": hr_threshold,
            "speed_threshold": speed_threshold,
            "pace": pace
        }
    else:
        return {"error": "Impossibile calcolare la soglia anaerobica."}
    

