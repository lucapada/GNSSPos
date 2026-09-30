# GNSSPos — Documentazione tecnica degli esperimenti

Campagna: **GPS_Sassuolo_Forlì, Volo_1** (2023-06-27, DOY 178, GPS week 2268).
Sistema di riferimento planimetrico: **UTM Zona 32N** (EPSG:32632), quota ellissoidica WGS84.

## 0. Strumentazione e schema generale

| Ruolo | Ricevitore | Esperimento |
|---|---|---|
| Base fissa a terra | Leica 1200 (geodetico) | fornisce le osservazioni di riferimento per tutti gli esperimenti RTK (A, C) |
| Rover alto costo | Leica 1200 | Esperimento A |
| Rover basso costo ×3 (a bordo velivolo) | uBlox EVK-M8T — COM23/COM24/COM25 | Esperimenti B, C, D, E |
| Rover di riferimento indipendente | ricevitore consumer (LocationAPI, solo NMEA) | Esperimento 0 |

Pipeline complessiva:

```
Base Leica (fissa) ─┐
                     ├─► RTK differenziale (Exp A: Leica rover, Exp C: 3× uBlox rover)
3× uBlox rover ──────┘
3× uBlox rover ──────────► posizionamento standalone (Exp B)
NMEA consumer ────────────► baseline indipendente (Exp 0)

Exp C (3 serie) ──► allineamento temporale ──┬─► fusione statica     (Exp D)
                                              └─► fusione dinamica KF (Exp E)

Ogni esperimento ──► metriche RMS/μ_d/σ_d vs baseline Exp 0
```

Tutti gli esperimenti RTK/SPP (A, B, C) usano lo stesso binario `rnx2rtkp` (RTKLIB EX 2.5.0, demo5) con prodotti IGS precisi condivisi (SP3 orbite, CLK orologi, BRDC nav broadcast per la correzione ionosferica).

---

## 1. Esperimento 0 — Baseline NMEA GGA

**File**: `experiment_0/run.py` · **Input**: `LocationAPI_230627_090521.ubx` (stream NMEA grezzo) · **Output**: 9954 epoche, Q=5 (single), 09:05:13–11:56:53.

Nessun post-processing: parsing diretto delle sentenze `$--GGA`.

**Conversione coordinate (gradi-minuti-decimali → gradi decimali)**

```
lat = D_lat + M_lat / 60          (D_lat = int(DDMM.mmmmm[:2]), M_lat = float(DDMM.mmmmm[2:]))
lon = D_lon + M_lon / 60          (D_lon = int(DDDMM.mmmmm[:3]), M_lon = float(DDDMM.mmmmm[3:]))
lat := -lat  se emisfero S
lon := -lon  se emisfero W
```

**Quota ellissoidica (HAE)**

```
h = alt_MSL + N_geoide
```

dove `alt_MSL` è la quota ortometrica trasmessa nel campo GGA e `N_geoide` la separazione geoide-ellissoide (anch'essa nel GGA).

**Incertezza stimata da HDOP** (nessuna covarianza reale disponibile da GGA):

```
σ_n = σ_e = 2·HDOP
σ_u = 3·HDOP
σ_ne = σ_eu = σ_un = 0
```

Mappatura qualità fix GGA → codice Q stile RTKLIB: `{1→5 single, 2→4 dgps, 4→1 fix, 5→2 float}`.

Questo esperimento è il **riferimento indipendente** (`ref_label`) usato per calcolare le metriche di tutti gli altri esperimenti.

---

## 2. Esperimento A — Leica 1200, RTK kinematic (rover alto costo)

**File**: `experiment_a/run.py` · **Config**: `leica_kinematic.conf` · **Input**: rover `45601780.23o`, base `BASE1780.23o` · **Output**: 308 epoche, Q=2 (limite dati, solo finestra 11:58).

Post-processing RTK differenziale via `rnx2rtkp`, modalità `kinematic`, effemeridi precise (`pos1-sateph=precise`).

**Equazione di osservazione, codice (pseudorange) e fase portante**, per il satellite *s* e ricevitore *r*:

```
P_r^s = ρ_r^s + c·(dt_r − dt^s) + I_r^s + T_r^s + ε_P
Φ_r^s = ρ_r^s + c·(dt_r − dt^s) − I_r^s + T_r^s + λ·N_r^s + ε_Φ
```

dove `ρ_r^s` è la distanza geometrica vero satellite-ricevitore, `dt_r`/`dt^s` gli errori di clock ricevitore/satellite, `I`/`T` i ritardi ionosferico/troposferico, `N_r^s` l'ambiguità intera di fase, `λ` la lunghezza d'onda della portante.

**Doppia differenza** (base *b*, rover *r*, satelliti *s*, satellite di riferimento *k*) — elimina gli errori di clock comuni:

```
∇Δρ_{rb}^{sk} = (ρ_r^s − ρ_b^s) − (ρ_r^k − ρ_b^k)
∇ΔΦ_{rb}^{sk} = ∇Δρ_{rb}^{sk} + λ·∇ΔN_{rb}^{sk} + ∇Δε
```

La baseline `r − b` (posizione base fissa nota, letta da RINEX header, `ant2-postype=rinexhead`) viene stimata via filtro di Kalman esteso di RTKLIB con risoluzione continua delle ambiguità intere (`pos2-armode=continuous`, algoritmo LAMBDA). Correzione ionosferica broadcast (`brdc`), troposferica Saastamoinen (`saas`).

**Output per epoca**: posizione LLH/UTM + matrice di covarianza NEU completa (`sdn_m, sde_m, sdu_m, sdne_m, sdeu_m, sdun_m`), stessa struttura usata da C/D/E.

---

## 3. Esperimento B — uBlox standalone con effemeridi precise

**File**: `experiment_b/run.py` · **Config**: `ublox_single.conf` · **Input**: solo rover, nessuna base · **Output**: ~10265 epoche, Q=5 (single).

Posizionamento singolo punto (SPP), nessuna doppia differenza (nessuna base). Equazione del codice risolta ai minimi quadrati pesati per ogni epoca:

```
P_r^s = ρ_r^s + c·dt_r − c·dt^s + I_r^s + T_r^s + ε_P
```

`dt^s`, orbita del satellite: presi da SP3/CLK precisi IGS invece che da effemeridi broadcast → errore orbitale/clock ridotto da metri a centimetri rispetto a Exp 0, ma **niente correzione differenziale**: l'errore di propagazione ionosferica/troposferica non cancellato resta dell'ordine del metro. Da qui Q=5 anche con prodotti precisi.

---

## 4. Esperimento C — uBlox RTK kinematic (3 rover vs base Leica)

**File**: `experiment_c/run.py` · **Config**: `ublox_kinematic.conf` · **Output**: ~2490 epoche/rover, Q=2 (float).

Stesso modello matematico dell'Esperimento A (doppia differenza + LAMBDA, §2), applicato **indipendentemente** ai tre rover COM23/COM24/COM25 contro la stessa base Leica:

```
rnx2rtkp -k ublox_kinematic.conf -o COMxx_rover.pos  COMxx_rover.obs  BASE1780.23o  nav  sp3  clk
```

Effemeridi e clock satellite da SP3/CLK precisi (`ephemeris.c: EPHOPT_PREC`); correzione ionosferica Klobuchar letta separatamente dal file NAV broadcast (`nav->ion_gps`) — due campi distinti di `nav_t`, nessun conflitto.

Risultato: **3 serie temporali indipendenti e non sincronizzate**, ciascuna con la propria posizione + matrice di covarianza NEU per epoca. Questo è l'input comune agli Esperimenti D ed E.

---

## 5. Allineamento temporale (pre-fusione)

**File**: `gnsspos/processing/time_alignment.py`, funzione `align_series()`, usata identicamente da D ed E.

**Finestra comune** (intersezione temporale tra le N serie):

```
t_start = max_i( min(index_i) )
t_end   = min_i( max(index_i) )
```

**Resample su griglia regolare** (Δt = 1 s), interpolazione lineare pesata per le epoche mancanti fra due epoche valide `t1 < t < t2`:

```
w2 = (t − t1) / (t2 − t1)
w1 = 1 − w2

posizione:    x(t) = w1·x(t1) + w2·x(t2)                     (lat, lon, height)
covarianza:   σ²(t) = w1²·σ²(t1) + w2²·σ²(t2)                 (propagazione della varianza)
qualità:      Q(t) = min(Q(t1), Q(t2)),   ns(t) = min(ns(t1), ns(t2))
```

Dopo l'interpolazione le coordinate UTM vengono ricalcolate da lat/lon (la funzione di allineamento interpola solo lat/lon/height).

---

## 6. Esperimento D — Fusione statica a varianza inversa

**File**: `experiment_d/run.py` · Combina le 3 serie allineate di Exp C, **epoca per epoca, senza modello temporale**.

**Peso per componente** (n=northing, e=easting, u=height), ricevitore *i* su N totali:

```
w_i,j = (1/σ_i,j²) / Σ_k (1/σ_k,j²)          j ∈ {n, e, u}
```

**Posizione combinata** (media pesata componente per componente):

```
x̂ = Σ_i W_i · x_i                             W_i = diag(w_i,n, w_i,e, w_i,u)
```

**Covarianza combinata**:

```
Ĉ = Σ_i W_i · C_i · W_iᵀ

C_i = ⎡ σ_n,i²   σ_ne,i   σ_un,i ⎤
      ⎢ σ_ne,i   σ_e,i²   σ_eu,i ⎥
      ⎣ σ_un,i   σ_eu,i   σ_u,i² ⎦
```

**Regolarizzazione PSD**: se `det(Ĉ) ≤ 0` (può accadere per via dei termini fuori diagonale), gli elementi fuori diagonale vengono scalati iterativamente `×0.9` finché `det(Ĉ) > 0` (max 2000 iterazioni).

Q ed ns combinati: `Q = min_i(Q_i)`, `ns = min_i(ns_i)` (approccio conservativo).

Risultato: 2489 epoche, Q=2, **σ ridotta di ~43%** rispetto al miglior rover singolo. Nessun parametro da tarare.

---

## 7. Esperimento E — Fusione dinamica, filtro di Kalman

**File**: `experiment_e/run.py` · Stesso input di Exp D (3 serie allineate di Exp C), ma sostituendo la media pesata istantanea con un **filtro di Kalman lineare a velocità costante (CV — constant velocity), a osservazioni multiple sequenziali**.

### 7.1 Formulazione stato-spazio

Sistema lineare-gaussiano tempo-discreto, tempo di campionamento fisso Δt = 1 s (coerente con la griglia di allineamento, §5):

```
x_k = F x_{k−1} + w_{k−1},        w_{k−1} ~ N(0, Q)          (equazione di stato)
z_k^{(i)} = H x_k + v_k^{(i)},    v_k^{(i)} ~ N(0, R_k^{(i)})  (equazione di misura, sensore i)
```

con `w` e `v^{(i)}` bianchi, mutuamente indipendenti, e le misure `v^{(i)}` indipendenti tra i diversi rover *i* (assunzione: i tre ricevitori uBlox non condividono errore correlato — multipath e rumore termico sono per-antenna; l'errore comune di orbita/clock satellite è già rimosso a monte dalla doppia differenza in Exp C).

### 7.2 Vettore di stato

Stato 6-dimensionale, posizione + velocità nel piano NEU locale (northing, easting, up — coerente col frame UTM32 usato da Exp C/D):

```
x_k = [ n_k  e_k  u_k  vn_k  ve_k  vu_k ]ᵀ  ∈ ℝ⁶
```

### 7.3 Modello di processo — moto a velocità costante

```
F = ⎡ I₃   Δt·I₃ ⎤ ∈ ℝ⁶ˣ⁶          (transizione: posizione integra la velocità)
    ⎣ 0    I₃    ⎦

Q = blockdiag(q_p·I₃, q_v·I₃)      (rumore di processo, diagonale a blocchi)

q_p = (σ_p·Δt)²    random walk di posizione,   σ_p = 0.05 m
q_v = (σ_v·Δt)²    random walk di velocità,    σ_v = 0.5 m/s
```

`F` è l'integrazione discreta esatta di un moto rettilineo uniforme (non un'approssimazione al prim'ordine): con accelerazione modellata come rumore bianco continuo, questa è la discretizzazione standard del modello Discrete Wiener Process Acceleration (DWPA/"nearly-constant-velocity"). `Q` non deriva dall'integrale rigoroso di Van Loan (che produrrebbe termini di accoppiamento posizione-velocità qₚᵥ ≠ 0); qui si usa la forma diagonale semplificata, valida a meno di termini O(Δt³) trascurabili per Δt = 1 s. `σ_p, σ_v` sono gli unici due iperparametri del filtro: controllano quanta "libertà" ha lo stato di scostarsi dal moto rettilineo tra un'epoca e l'altra.

### 7.4 Modello di osservazione — misure multiple per epoca

Ogni rover *i* fornisce, quando disponibile, una misura diretta di posizione (non di velocità):

```
H = [ I₃  0₃ ] ∈ ℝ³ˣ⁶                    (matrice di osservazione, comune a tutti i rover)
z_k^{(i)} = [ n_i  e_i  u_i ]ᵀ            misura di posizione del rover i all'epoca k
R_k^{(i)} = ⎡ σ_{n,i}²   σ_{ne,i}   σ_{un,i} ⎤     stessa costruzione NEU di Exp D, §6
            ⎢ σ_{ne,i}   σ_{e,i}²   σ_{eu,i} ⎥     (letta dalla riga .pos del rover i)
            ⎣ σ_{un,i}   σ_{eu,i}   σ_{u,i}² ⎦
```

La coppia (H, R) è identica per ogni rover nella forma, ma **R varia epoca per epoca ed è eteroschedastica tra rover** — riflette la qualità di fix RTK istantanea (Q/float, numero satelliti) di ciascun ricevitore.

### 7.5 Ciclo ricorsivo — predict + update sequenziale

Per ogni epoca k della griglia comune:

```
1. Predizione (una sola volta per epoca, indipendente dal numero di rover disponibili):

   x_{k|k-1} = F x_{k-1|k-1}
   P_{k|k-1} = F P_{k-1|k-1} Fᵀ + Q

2. Correzione, applicata in sequenza per ogni rover i con riga valida a k
   (stato e covarianza aggiornati "a cascata": l'output del rover i-esimo
   è l'input a priori per il rover i+1-esimo):

   Per i = 1 … m_k (rover disponibili all'epoca k):
       y_i  = z_k^{(i)} − H x^{(i-1)}                (innovazione / residuo)
       S_i  = H P^{(i-1)} Hᵀ + R_k^{(i)}             (covarianza dell'innovazione)
       K_i  = P^{(i-1)} Hᵀ S_i⁻¹                     (guadagno di Kalman)
       x^{(i)}  = x^{(i-1)} + K_i y_i
       P^{(i)}  = (I₆ − K_i H) P^{(i-1)}

   x_{k|k} = x^{(m_k)},   P_{k|k} = P^{(m_k)}

3. Se m_k = 0 (nessun rover valido a k) → x_{k|k} = x_{k|k-1}, P_{k|k} = P_{k|k-1}
   (passo di sola predizione: il filtro "naviga" sul solo modello di moto).
```

**Equivalenza con l'aggiornamento batch.** Poiché le `v^{(i)}` sono indipendenti tra loro, la likelihood congiunta delle m_k misure fattorizza:

```
p(z^{(1)},…,z^{(m_k)} | x) = Π_i p(z^{(i)} | x)
```

Per un modello lineare-gaussiano questo implica che l'aggiornamento sequenziale (una misura alla volta) e l'aggiornamento batch con osservazione impilata `z = [z^{(1)}ᵀ,…,z^{(m_k)}ᵀ]ᵀ`, `H_batch = [Hᵀ,…,Hᵀ]ᵀ`, `R_batch = blockdiag(R^{(1)},…,R^{(m_k)})` producono **esattamente lo stesso** `x_{k|k}, P_{k|k}` — indipendentemente dall'ordine con cui i rover vengono processati. Il codice sfrutta questa equivalenza per evitare l'inversione di una matrice `S_batch` di dimensione 3m_k×3m_k (fino a 9×9 con 3 rover): si invertono invece m_k matrici 3×3, con costo computazionale O(m_k) invece di O(m_k³).

### 7.6 Inizializzazione

Bootstrap alla prima epoca t₀ con almeno un rover valido (media pesata a varianza inversa, stessa formula di Exp D §6, applicata alla sola posizione):

```
x_0 = [ n̄  ē  ū  0  0  0 ]ᵀ
P_0 = diag(σ_p0² I₃, σ_v0² I₃),     σ_p0 = 1 m,  σ_v0 = 5 m/s
```

`P_0` è deliberatamente sovradimensionata rispetto all'incertezza reale di posizione (σ_p0 = 1 m ≫ σ tipica RTK float ~ cm-dm) e la velocità iniziale è ignota (`vn=ve=vu=0` con σ_v0 = 5 m/s copre l'intero range di velocità plausibili del velivolo). Questo garantisce che il guadagno K delle prime epoche sia prossimo a 1 (il filtro si fida quasi interamente della prima misura) e che il transitorio di convergenza — la finestra in cui P_{k|k} passa dal valore iniziale grezzo al regime stazionario dettato da Q e R — duri circa 10 epoche, dopo le quali il filtro opera in condizioni di quasi-stazionarietà (P_{k|k} oscilla entro un range stretto, determinato dal punto fisso dell'equazione di Riccati algebrica associata a F, Q, H, R̄, con R̄ = R media).

### 7.7 Nota implementativa: forma dell'aggiornamento di covarianza

Il codice usa la forma semplificata `P = (I − KH)P` invece della forma di Joseph `P = (I−KH)P(I−KH)ᵀ + KRKᵀ`. La forma semplificata è algebricamente equivalente solo se K è esattamente il guadagno ottimo di Kalman (come qui) ed è numericamente meno robusta alla perdita di simmetria/positività per errori di arrotondamento in floating point su orizzonti lunghi. Per un filtro con m_k ≤ 3 aggiornamenti per epoca e poche migliaia di epoche totali (~2500), il rischio di perdita di PSD è basso ma non nullo; la forma di Joseph sarebbe la scelta più robusta se il filtro venisse esteso a orizzonti più lunghi o a un numero maggiore di sensori.

### 7.8 Interpretazione dei parametri di tuning (σ_p, σ_v)

Il rapporto `Q` (rumore di processo, quanto ci fidiamo del modello di moto) vs `R` (rumore di misura, quanto ci fidiamo dei rover) determina il comportamento in frequenza del filtro — un KF lineare stazionario si comporta come un filtro passa-basso sulle misure, con banda passante crescente al crescere di `‖Q‖/‖R‖`:

- **σ_v basso** → `Q` piccolo → il filtro impone fortemente il modello a velocità costante → forte smoothing, varianza d'uscita bassa, ma **ritardo/bias in transitorio** durante accelerazioni o virate del velivolo (il modello CV è sistematicamente sbagliato quando l'accelerazione reale è ≠ 0 — errore di modello, non di misura).
- **σ_v alto** → `Q` grande → il filtro si affida quasi solo alle misure correnti → risposta rapida alle manovre, ma varianza d'uscita che tende a quella della fusione statica (Exp D), perdendo il vantaggio dello smoothing.
- **σ_p** gioca un ruolo minore: consente piccoli scostamenti di posizione indipendenti dalla velocità stimata (assorbe jitter residuo), tipicamente tenuto piccolo rispetto alle σ di misura RTK.

Non essendoci un ground truth ad alta precisione nella campagna, la taratura è stata fatta a occhio sul compromesso varianza-vs-ritardo osservato nei plot `time_series_e.png`, non per minimizzazione formale (es. cross-validation su NEES/innovazione).

### 7.8bis Round 2 — σ_v adattivo su curvatura (`run_adaptive.py`, `run_ablation.py`, `curvature.py`)

Il modello CV con σ_v costante (sopra) è tarato sui tratti dritti: stretto lì (buon smoothing), ma insufficiente nelle curve, dove il modello a velocità costante è strutturalmente sbagliato e il filtro "taglia" la curva. Alzare σ_v ovunque risolverebbe le curve ma renderebbe rumorosi i rettilinei; passare a un modello ad accelerazione costante (9 stati) introduce jitter anche nei rettilinei (il rumore di processo sull'accelerazione scambia rumore di misura per manovra reale). Soluzione adottata: **stesso modello CV, σ_v variabile per epoca**, in due round.

1. **Curvatura**: rate-of-turn a finestra (±5 s) calcolato sulla fusione statica di Exp D (non sulla velocità stimata da Exp E stesso, per evitare circolarità — quella velocità è già affetta dal ritardo che si vuole correggere): `Δθ(t) = atan2(v1×v2, v1·v2)`, `turn_rate = Δθ/(2w·Δt)`, con `v1,v2` vettori posizione prima/dopo la finestra. Epoche a velocità < 0.3 m/s → NaN (heading indefinito).
2. **Clustering**: k-means (scikit-learn) su `|turn_rate|`, k ∈ {2,3,4} scelto per silhouette massima (sul dataset Volo_1: k=2, non k=3 come ipotizzato inizialmente). Cluster riordinati per centroide crescente: rank 0 = dritto, rank k-1 = curva più stretta.
3. **σ_v adattivo**: `σ_v(rank) = σ_v_base · growth^rank`, un solo iperparametro (`growth`). `growth=1` riproduce esattamente il round 1 (verificato bit-a-bit); `growth=2` è la proposta originale del professore ("raddoppiare").
4. **Ablation**: sweep `growth ∈ {1, 1.5, 2, 3, 4}`, metriche vs Exp 0 tabulate in `experiment_e/outputs/ablation/ablation_results.csv`. Effetto presente ma piccolo rispetto al bias assoluto di Exp 0 (~100-200 m) — segnale direzionalmente coerente (σ_u, σ_d migliorano monotonicamente con growth) ma non abbastanza forte per l'articolo con questa baseline. Vedi `experiment_e/README.md` §8 per dettagli, limiti e alternativa proposta (consistenza inter-rover invece che offset assoluto vs Exp 0).

### 7.9 Assunzioni e limiti del modello

- **Indipendenza delle misure tra rover** (§7.1): ragionevole per rumore termico/multipath locale alle singole antenne, ma i tre uBlox condividono la stessa base Leica e lo stesso set di prodotti IGS — eventuali errori sistematici residui della doppia differenza (non completamente rimossi da orbita/clock precisi, es. multipath a banda larga sull'aereo) sarebbero **correlati tra i tre rover** e non modellati: il filtro tratterebbe come tre osservazioni indipendenti informazione che in parte non lo è, con conseguente **sottostima di P_{k|k}** (overconfidence).
- **R non stimata online**: `R_k^{(i)}` è presa così com'è dall'output RTKLIB (deriva dalla matrice di covarianza interna del filtro di Kalman esteso di `rnx2rtkp`, §2) — nessun fattore di scala o test di consistenza (es. NIS — Normalized Innovation Squared) applicato per validare che le σ dichiarate riflettano l'errore reale.
- **Modello CV rigido**: nessun termine di jerk o modello a velocità costante a tratti (jump Markov / IMM); adeguato per un velivolo in moto relativamente uniforme, meno per fasi di manovra brusca.
- **Q diagonale semplificata** (§7.3): trascura l'accoppiamento posizione-velocità del rumore di processo che la discretizzazione esatta di Van Loan produrrebbe; l'approssimazione è giustificata per Δt = 1 s ma andrebbe rivista per Δt più grandi.

**Confronto D vs E**:

| Aspetto | Exp D | Exp E |
|---|---|---|
| Modello temporale | nessuno | velocità costante |
| Stima velocità | no | sì (vn, ve, vu) |
| Sensibilità ai gap | riga scartata se un σ è NaN | passo di sola predizione |
| Parametri da tarare | nessuno | σ_p, σ_v |
| Comportamento | baseline statica, zero-knob | smoothing dinamico, minore σ ma introduce piccolo ritardo nelle manovre se σ_v troppo basso |

---

## 8. Metriche di valutazione

**File**: `gnsspos/processing/metrics.py`. Applicate confrontando ogni esperimento con la baseline Exp 0, dopo allineamento (`align_series`).

**RMS cumulativo per componente** (colonna `col` ∈ {easting_m, northing_m, height_m}), residuo `r_k = exp_k − ref_k`:

```
RMS_col(t_i) = sqrt( (1/i) · Σ_{k=1}^{i} r_k² )
```

**Distanza 3D per epoca**:

```
d_k = sqrt( Δeasting_k² + Δnorthing_k² + Δheight_k² )
```

**Media cumulativa della distanza 3D**:

```
μ_d(t_i) = (1/i) · Σ_{k=1}^{i} d_k
```

**Deviazione standard cumulativa della distanza 3D** (rispetto alla media corrente ad ogni passo):

```
σ_d(t_i) = sqrt( (1/i) · Σ_{k=1}^{i} (d_k − μ_d(t_k))² )
```

---

## 9. Riepilogo esperimenti

| Exp | Metodo | Ricevitori | Base | Epoche | Q tipico | Note |
|---|---|---|---|---|---|---|
| 0 | Parsing NMEA GGA | 1 (consumer) | — | 9954 | 5 (single) | baseline indipendente per le metriche |
| A | RTK kinematic (DD + LAMBDA) | 1 (Leica, alto costo) | Leica | 308 | 2 (float) | finestra dati limitata |
| B | SPP + effemeridi precise | 3 (uBlox) | — | ~10265 | 5 (single) | nessuna correzione differenziale |
| C | RTK kinematic (DD + LAMBDA) | 3 (uBlox) | Leica | ~2490/rover | 2 (float) | input di D ed E |
| D | Fusione statica varianza inversa | fonde 3× Exp C | — | 2489 | 2 | σ ↓~43%, zero-knob |
| E | Fusione dinamica, KF vel. costante | fonde 3× Exp C | — | ~2489 | 2 | σ ↓ ulteriore + stima velocità, richiede tuning σ_p/σ_v |
