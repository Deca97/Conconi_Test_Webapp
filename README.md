
# 🏃‍♂️ Conconi Test Analyzer

---

## ⚡ What is the Conconi Test

The **Conconi Test**, developed by Francesco Conconi in 1982, is an incremental test used to estimate an athlete’s **anaerobic threshold**, based on the analysis of heart rate relative to running speed.

- During the test, the athlete runs with regular speed increments.  
- Heart rate is monitored at each interval.  
- The point where the heart rate–speed curve stops being linear identifies the **anaerobic threshold**, which is useful for planning endurance and interval training.

> ⚠️ Note: Estimating the threshold from heart rate is indicative. Recent studies show that the HR–speed relationship can vary significantly between individuals, so results should be interpreted with caution.

---

## 📊 Conconi Test Protocol

The test should be performed under controlled conditions to ensure reliable results:

1. **Warm-up**: 10–15 minutes at low intensity.  
2. **Speed increments**: run 200 m at an initial speed, then increase by **0.5–1 km/h every 200 m**.  
3. **Heart rate monitoring**: monitor heart rate continuously.  
4. **Threshold identification**: the anaerobic threshold corresponds to the point where the HR–speed curve stops being linear.

> Recommended: perform the test on a flat surface, with a reliable heart rate monitor, preferably outdoors or on a track.

---

## 📈 Reference Table of Speed Increments

| Interval Distance (m) | Cumulative Distance (m) | Speed (km/h) | Speed (m/s) | Time for 200 m (s) | Pace (min/km) | Cumulative Time (mm:ss) |
|----------------------|------------------------|--------------|-------------|------------------|---------------|------------------------|
| 200                  | 200                    | 13           | 3.61        | 55.5             | 4:37          | 00:55                  |
| 200                  | 400                    | 14           | 3.89        | 51.4             | 4:17          | 01:46                  |
| 200                  | 600                    | 15           | 4.17        | 48.0             | 4:00          | 02:34                  |
| 200                  | 800                    | 16           | 4.44        | 45.0             | 3:45          | 03:19                  |
| 200                  | 1000                   | 17           | 4.72        | 42.4             | 3:34          | 04:01                  |
| 200                  | 1200                   | 18           | 5.00        | 40.0             | 3:20          | 04:41                  |
| 200                  | 1400                   | 19           | 5.28        | 37.9             | 3:10          | 05:19                  |
| 200                  | 1600                   | 20           | 5.56        | 36.0             | 3:00          | 05:55                  |
| 200                  | 1800                   | 21           | 5.83        | 34.3             | 2:53          | 06:29                  |
| 200                  | 2000                   | 22           | 6.11        | 32.7             | 2:45          | 07:02                  |

> **Note:** Each 200 m increment allows a gradual speed increase and helps observe the HR deflection point.

---

## 🚀 How to Use the App

1. **Upload the FIT file** of your running session via the “Upload FIT file” button.  
2. The app will automatically extract **heart rate** and **speed**.  
3. It will calculate the **anaerobic threshold** and display:  
   - Heart rate at threshold  
   - Corresponding speed  
   - Confidence interval  

> ⚠️ Warning: If the test was not executed correctly or data are insufficient, the app will return an error.

---

## ⚠️ Warnings

- The Conconi Test provides **indicative estimates**, not absolute values.  
- Results may vary depending on training level, environmental conditions, and data quality.  
- For a more precise determination of the anaerobic threshold, consider using **blood lactate measurements** or **respiratory gas analysis**.  
- Calculated values should be interpreted **as training guidelines**, not as clinical diagnostics.  
- The **HR Deflection Point (HRDP)** or Conconi curve is most useful for monitoring **individual trends over time**, rather than determining absolute threshold values.

---

## ℹ️ Usefulness of the App

The **Conconi Test Analyzer** is designed for runners and athletes who want to monitor progress in a simple, non-invasive way:

- **Individual monitoring over time**: by comparing multiple tests from the same athlete, one can observe improvements or regressions in aerobic condition.  
- **Support for training planning**: provides relative indications for training intensity and helps structure progressive sessions based on the estimated threshold.  
- **Education and awareness**: helps understand how heart rate varies with speed and how to interpret training data.

> ⚠️ Note: The threshold values calculated by the app are **indicative**. They do not replace lab-based tests with lactate or gas exchange analysis.

---

## 📂 Supported Files

- **FIT files** (from Garmin or similar devices).  

---

## 📚 Scientific References

- Conconi F., et al., *Determination of the anaerobic threshold by a noninvasive field test in runners*, Journal of Applied Physiology, 1982.  
- Donne, Bernard; Fleming, Neil; Campbell, Garry; Ward, Tomás; Crampton, David; Mahony, Nick. *Graded Incremental Test Data (Cycling, Running, Kayaking, Rowing): an open access dataset*. Zenodo, March 2022.
- Ferri-Marini C., et al., *Assessment of the Heart Rate Deflection Point in Athletes for a Non-Invasive Determination of the Anaerobic Threshold: A Systematic Review*, Journal of Science in Sport and Exercise, 2025.  
