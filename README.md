# 🏃‍♂️ Conconi Test Analyzer

---

## ⚡ Cos’è il Test di Conconi

Il **Test di Conconi**, ideato da Francesco Conconi nel 1982, è un test incrementale utilizzato per stimare la **soglia anaerobica** di un atleta, basandosi sull’analisi della frequenza cardiaca rispetto alla velocità.

- Durante il test, l’atleta corre con incrementi regolari di velocità.  
- La frequenza cardiaca viene monitorata ad ogni intervallo.  
- Il punto in cui la curva frequenza cardiaca – velocità smette di essere lineare identifica la **soglia anaerobica**, utile per programmare allenamenti di endurance e interval training.

> ⚠️ Nota: la stima della soglia tramite frequenza cardiaca è indicativa. Studi recenti mostrano che la relazione HR–velocità può variare molto tra individui, quindi i risultati devono essere interpretati con cautela.

---

## 📊 Protocollo del Test di Conconi

Il test deve essere eseguito in condizioni controllate per garantire risultati affidabili:

1. **Riscaldamento**: 10–15 minuti a bassa intensità.  
2. **Incrementi di velocità**: correre 200 m a una velocità iniziale, aumentando di **0,5–1 km/h ogni 200 m** successivi.  
3. **Rilevazione frequenza cardiaca**: monitorare continuamente la frequenza cardiaca.  
4. **Identificazione della soglia**: la soglia anaerobica corrisponde al punto in cui la curva frequenza cardiaca – velocità smette di essere lineare.

> Consigliato: test su superficie piana, con cardiofrequenzimetro affidabile, preferibilmente all’aperto o su pista.

---

## 📈 Tabella di riferimento incrementi velocità

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

> **Nota:** ogni incremento di 200 m serve a ottenere un aumento graduale della velocità e permettere di osservare il punto di deflessione della frequenza cardiaca.

---

## 🚀 Come usare l’app

1. **Carica il file FIT** della tua sessione di corsa tramite il pulsante “Carica file FIT”.  
2. L’app estrarrà automaticamente **frequenza cardiaca** e **velocità**.  
3. Calcolerà la **soglia anaerobica** e mostrerà il risultato:  
   - Frequenza cardiaca alla soglia  
   - Velocità corrispondente  
   - Intervallo di confidenza  

> ⚠️ Attenzione: se il test non è stato eseguito correttamente o i dati sono insufficienti, l’app restituirà un errore.

---

## ⚠️ Avvertenze

- Il Test di Conconi fornisce **stime indicative**, non valori assoluti.  
- I risultati possono variare in base al livello di allenamento, condizioni ambientali e qualità dei dati.  
- Per una stima più precisa della soglia anaerobica, si consiglia di integrare misurazioni di **lattato** o **analisi del gas respiratorio**.  
- I valori calcolati vanno interpretati **come indicazioni di allenamento**, non come diagnosi cliniche.  
- L’**HR Deflection Point (HRDP)** o la curva di Conconi sono strumenti utili soprattutto per monitorare **trend individuali nel tempo**, piuttosto che determinare valori assoluti della soglia anaerobica.

---

## ℹ️ Utilità dell’App

Il **Conconi Test Analyzer** è pensato per runner e atleti che vogliono monitorare i propri progressi in modo semplice e non invasivo:

- **Monitoraggio individuale nel tempo**: confrontando più test dello stesso atleta, è possibile osservare miglioramenti o regressioni nella condizione aerobica.  
- **Supporto alla pianificazione dell’allenamento**: fornisce indicazioni relative sull’intensità degli allenamenti e permette di strutturare sessioni progressive basate sulla soglia stimata.  
- **Educazione e consapevolezza**: aiuta a comprendere come la frequenza cardiaca varia con la velocità e come interpretare i dati di allenamento.

> ⚠️ Nota: i valori della soglia anaerobica calcolati dall’app sono **indicativi**. Non sostituiscono test di laboratorio basati su lattato o analisi del gas respiratorio.

---

## 📂 File supportati

- File **FIT** (da dispositivi Garmin o simili).  

---

## 📚 Riferimenti Scientifici

- Conconi F., et al., *Determination of the anaerobic threshold by a noninvasive field test in runners*, Journal of Applied Physiology, 1982.  
- Ferri-Marini C., et al., *Assessment of the Heart Rate Deflection Point in Athletes for a Non-Invasive Determination of the Anaerobic Threshold: A Systematic Review*, Journal of Science in Sport and Exercise, 2025.
