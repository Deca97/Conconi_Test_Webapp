# 🏃‍♂️ Guida all'uso del Conconi Test Analyzer

Questa sezione fornisce informazioni utili sull'utilizzo dell'app per l'analisi dei test Conconi, con riferimento al protocollo scientifico originale.  

---

## ⚡ Che cos'è il Test di Conconi

Il **Test di Conconi** è un test incrementale utilizzato per stimare la **soglia anaerobica** di un atleta, basandosi sull'analisi della frequenza cardiaca rispetto alla velocità. Durante il test, l'atleta corre con incrementi regolari di velocità e si registra la frequenza cardiaca.  

Il punto in cui la relazione tra frequenza cardiaca e velocità smette di essere lineare identifica la **soglia anaerobica**, utile per programmare allenamenti di endurance e interval training.

**Riferimenti scientifici principali:**

- Conconi F., et al., *Determination of the anaerobic threshold by a noninvasive field test in runners*, Journal of Applied Physiology, 1982.  

---

## 📊 Tabella di riferimento velocità/tempo

La tabella seguente mostra gli incrementi di velocità utilizzati nel test Conconi tipico: ogni **200 metri** la velocità aumenta di **1 km/h**, da **13 km/h a 22 km/h**. Include la conversione in metri al secondo, tempo necessario per percorrere 200 m, pace in min/km, distanza cumulativa e tempo cumulativo.

| Interval Distance (m) | Cumulative Distance (m) | Speed (km/h) | Speed (m/s) | Time for 200m (s) | Pace (min/km) | Cumulative Time (mm:ss) |
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

> **Nota:** Il tempo cumulativo è calcolato come somma dei tempi di ciascun intervallo di 200 m. La distanza cumulativa si somma ad ogni step di 200 m.

---

## ℹ️ Come usare la tabella nella web app

1. **Carica il file FIT** della tua sessione di corsa tramite il pulsante “Carica file FIT”.  
2. L’app estrarrà automaticamente frequenza cardiaca, velocità e calcolerà la soglia anaerobica.  
3. La tabella sopra serve come **riferimento per confrontare il tuo ritmo con incrementi standard**.  
4. Utilizza le informazioni della soglia per pianificare allenamenti mirati: ad esempio, correre leggermente sotto la soglia anaerobica per endurance o leggermente sopra per stimoli anaerobici.

---
