from gnsspos.rover import Rover
import pandas as pd
import re
import os
import numpy as np
from tqdm import tqdm
import argparse

argparser = argparse.ArgumentParser(description="GNSS Positioning Algorithm")
# argparser.add_argument("-d", "--dataframe", action="store_true", default=False, help="Path to the working directory")
# argparser.add_argument("-p", "--plot", action="store_true", default=False, help="Plot the results")
# argparser.add_argument("-a", "--algorithm", action="store_true", default=False, help="Run the algorithm")
args = argparser.parse_args()

# Path della cartella di lavoro
workingDirectory = os.path.join(os.path.dirname(__file__), 'examples', 'working_directory_ferrara')

# L'algoritmo prende in input i file .pos dei rover e del base station, e un insieme di soglie
rovers = [
    Rover(name="Rover1", pos_file=f"{workingDirectory}/rover_1.pos"),
    Rover(name="Rover2", pos_file=f"{workingDirectory}/rover_2.pos"),
    Rover(name="Rover3", pos_file=f"{workingDirectory}/rover_3.pos"),
]

base = Rover(name="Base Station", pos_file=f"{workingDirectory}/base_station.pos")

thesholds = {
    (rovers[0], rovers[1]): 20.0,
    (rovers[1], rovers[2]): 20.0,
    (rovers[0], rovers[2]): 20.0,
    ('sdx', None): 10.0,
    ('sdy', None): 10.0,
    ('sdz', None): 10.0,
}

# il DataFrame dei file .pos e del file .pos finale ha le seguenti colonne:
columns = ['GPST','x-ecef(m)','y-ecef(m)','z-ecef(m)','Q','ns','sdx(m)','sdy(m)','sdz(m)','sdxy(m)','sdyz(m)','sdzx(m)','age(s)','ratio']

def create_dataframes():
    """
    Crea i DataFrame a partire dai file .pos dei rover e salva il pickle nella cartella di lavoro.
    """
    
    print("Start processing rover data...")
    for r in rovers:
        print(f"Processing {r.name}...")
        # crea un DataFrame vuoto con le colonne definite
        df = pd.DataFrame(columns=columns)
        # leggi il file saltando tutte le righe con commento (intestazione compresa)
        with open(r.getPosFile(), 'r') as file:
            while not file.readline().strip().startswith('%  GPST'):
                next(file)
            # legge il resto del file in un DataFrame
            for line in tqdm(file):
                data = re.split(r'\s+', line.strip())
                # accorpa data e orario in GPST
                data[0] = data[0] + ' ' + data[1]
                data.pop(1)
                # Aggiungi una riga al DataFrame
                df.loc[len(df)] = data
        # aggiusta il tipo di dato di ciascuna colonna
        for c in columns:
            if c == 'GPST':
                df[c] = pd.to_datetime(df[c], format='%Y/%m/%d %H:%M:%S.%f')
            elif c == 'Q' or c == 'ns':
                df[c] = df[c].astype(int)
            else:
                df[c] = df[c].astype(float)
        # indicizza il DataFrame per la colonna 'GPST' (così l'accesso è più veloce)
        df.set_index('GPST', inplace=True)
        # aggiungi una colonna con il nome del rover
        df['rover'] = r.name
        # salvo il DataFrame in un pickle
        df.to_pickle(f"{workingDirectory}/{r.name}.pkl")

# se nella working directory non ci sono i file .pkl o se lo richiedo esplicitamente, li creo
if (not all([f"{r.name}.pkl" in os.listdir(workingDirectory) for r in rovers])):
    print("(Re)creating dataframes...")
    create_dataframes()

################## fine creazione DataFrame ##################

# mi aspetto che le epoche non siano tutte uguali, quindi scorro una prima volta tutti i DataFrame per capire lo starting time e l'ending time. 
# Approfitto del momento per salvare in un array tutti i DataFrame
dataframes = []
min_gpst = 0
max_gpst = 0

for r in rovers:
    # carica il DataFrame dal pickle
    df = pd.read_pickle(f"{workingDirectory}/{r.name}.pkl")
    # calcola il GPST minimo e massimo
    if min_gpst == 0:
        min_gpst = df.index.min()
    if max_gpst == 0:
        max_gpst = df.index.max()
    # aggiorna il GPST minimo e massimo
    min_gpst = min(min_gpst, df.index.min())
    max_gpst = max(max_gpst, df.index.max())
    # aggiungi il DataFrame alla lista
    dataframes.append(df)
    print(f"Finished processing {r.name} ({min_gpst} - {max_gpst})")        

# stampa min_gpst e max_gpst
print("Min and Max GPST across all rovers:")
print(f"- min_gpst: {min_gpst}")
print(f"- max_gpst: {max_gpst}")
print()

def algorithm():
    for kDf, df in enumerate(dataframes):
        # filtra il DataFrame in base a min_gpst e max_gpst
        df = df[(df.index >= min_gpst) & (df.index <= max_gpst)]
        # stampa il DataFrame
        print(df)

    # in questo momento ho i DataFrame di ciascun rover, tutti che partono dallo stesso (min)GPST e terminano allo stesso (max)GPST
    # posso applicare l'algoritmo per la creazione di un file .pos finale
    # creo un DataFrame finale vuoto
    final_df = pd.DataFrame(columns=columns)

    # 1) per ogni epoca, faccio un primo check sui rover disponibili. In particolare, mi interessa che:
    # - vi sia l'epoca
    # - la distanza con gli altri rover non sia "eccessivamente" sbagliata
    # nel caso in cui uno dei due elementi non è rispettato, rimuovo l'epoca
    current_gpst = min_gpst
    while current_gpst < max_gpst:
        print(current_gpst)
        
        # metto i ricevitori non validi in un set
        invalid_rovers = set()
        
        for kI, vI in enumerate(rovers):
            # controlla se l'epoca è presente nel DataFrame
            if current_gpst not in dataframes[kI].index:
                # se non è presente, metti il rover in invalid_rovers
                invalid_rovers.add(vI)
                print(f"{' '*20}- {vI.name} not available")
            else:
                for kJ, vJ in enumerate(rovers):
                    # il confronto deve essere con gli altri rover
                    if kI < kJ:
                        if current_gpst not in dataframes[kJ].index:
                            # se non è presente l'epoca che mi interessa, metti il rover in invalid_rovers
                            invalid_rovers.add(vJ)
                            print(f"{' '*20}- {vJ.name} not available")
                        else:
                            # calcola la distanza tra i rover
                            xI = dataframes[kI].loc[current_gpst]['x-ecef(m)']
                            yI = dataframes[kI].loc[current_gpst]['y-ecef(m)']
                            zI = dataframes[kI].loc[current_gpst]['z-ecef(m)']
                            xJ = dataframes[kJ].loc[current_gpst]['x-ecef(m)']
                            yJ = dataframes[kJ].loc[current_gpst]['y-ecef(m)']
                            zJ = dataframes[kJ].loc[current_gpst]['z-ecef(m)']
                            dist = np.sqrt((xI - xJ) ** 2 + (yI - yJ) ** 2 + (zI - zJ) ** 2)
                            # se la distanza è maggiore della soglia, rimuovi l'epoca
                            if dist > thesholds[(vI, vJ)]:
                                print(f"{' '*20}- {vI.name}-{vJ.name} = {dist} > {thesholds[(vI, vJ)]} KO!")
                                # sia il rover I che il rover J non sono validi
                                invalid_rovers.add(vI)
                                invalid_rovers.add(vJ)
                            else:
                                print(f"{' '*20}- {vI.name}-{vJ.name} = {dist} <= {thesholds[(vI, vJ)]} OK!")

        # 2) se ci sono rover non validi, correggo usando l'elemento precedente e successivo della serie temporale:
        # - per le grandezze, faccio la media
        # - per le (co)varianze, prendo il valore più alto
        if len(invalid_rovers) > 0:
            print(f"\n{' '*20}Invalid rovers: {' '.join([r.name for r in invalid_rovers])}\n")
            # rimuovi i rover non validi
            for r in invalid_rovers:
                # TODO:
                # di sicuro la prima epoca di ciascun rover non è mai vuota, ma può comunque essere sbagliata...
                # se è la prima non posso fare interpolazione lineare con il valore dell'epoca precedente e dell'epoca successiva, per cui:
                # - la lascio invariata
                # - [scelta corrente] faccio interpolazione pesata con gli altri rover (ammesso che ci siano e siano validi)
                # - la copio da un altro rover... anche se all'inizio può capitare che tutti i rover siano sbagliati...
                if current_gpst == min_gpst and len(invalid_rovers) == 1: 
                    new_row = {}
                    # se c'è solo un rover non valido, prendo i dati da tutti gli altri rover. In particolare:
                    # - GPST: ce l'ho già
                    new_row['GPST'] = current_gpst
                    # - x-ecef(m), y-ecef(m), z-ecef(m): media tra i rover validi
                    new_row['x-ecef(m)'] = 0
                    new_row['y-ecef(m)'] = 0
                    new_row['z-ecef(m)'] = 0
                    # - sdx(m), sdy(m), sdz(m), sdxy(m), sdyz(m), sdzx(m): prendo il valore più alto
                    new_row['sdx(m)'] = 0
                    new_row['sdy(m)'] = 0
                    new_row['sdz(m)'] = 0
                    new_row['sdxy(m)'] = 0
                    new_row['sdyz(m)'] = 0
                    new_row['sdzx(m)'] = 0
                    new_row['Q'] = 0 
                    new_row['ns'] = 0 
                    new_row['age(s)'] = 0 
                    new_row['ratio'] = 0 
                    for kDf, df in enumerate(dataframes):
                        # se il rover è valido, prendo i dati
                        if rovers[kDf] not in invalid_rovers:
                            # inizialmente sommo x/y/z-ecef(m) (per poi fare la media)
                            new_row['x-ecef(m)'] += df.loc[current_gpst]['x-ecef(m)']
                            new_row['y-ecef(m)'] += df.loc[current_gpst]['y-ecef(m)']
                            new_row['z-ecef(m)'] += df.loc[current_gpst]['z-ecef(m)']
                            # prendo il valore più alto delle (co)varianze
                            new_row['sdx(m)'] = max(new_row['sdx(m)'], df.loc[current_gpst]['sdx(m)'])
                            new_row['sdy(m)'] = max(new_row['sdy(m)'], df.loc[current_gpst]['sdy(m)'])
                            new_row['sdz(m)'] = max(new_row['sdz(m)'], df.loc[current_gpst]['sdz(m)'])
                            new_row['sdxy(m)'] = max(new_row['sdxy(m)'], df.loc[current_gpst]['sdxy(m)'])
                            new_row['sdyz(m)'] = max(new_row['sdyz(m)'], df.loc[current_gpst]['sdyz(m)'])
                            new_row['sdzx(m)'] = max(new_row['sdzx(m)'], df.loc[current_gpst]['sdzx(m)'])
                            # Q, ns, age(s) e ratio: non mi interessano (li lascio invariati)
                            new_row['Q'] = min(new_row['Q'], df.loc[current_gpst]['Q'])
                            new_row['ns'] = max(new_row['ns'], df.loc[current_gpst]['ns'])
                            new_row['age(s)'] = max(new_row['age(s)'], df.loc[current_gpst]['age(s)'])
                            new_row['ratio'] = max(new_row['ratio'], df.loc[current_gpst]['ratio'])
                    # faccio la media
                    new_row['x-ecef(m)'] /= len(rovers) - len(invalid_rovers)
                    new_row['y-ecef(m)'] /= len(rovers) - len(invalid_rovers)
                    new_row['z-ecef(m)'] /= len(rovers) - len(invalid_rovers)
                                    
                    # aggiorno la riga al DataFrame
                    df = dataframes[rovers.index(r)]
                    df.loc[current_gpst] = new_row
                    # aggiorno il DataFrame
                    dataframes[rovers.index(r)] = df
                elif current_gpst > min_gpst:
                    # interpolazione lineare con la prima epoca precedente e la prima epoca successiva
                    df = dataframes[rovers.index(r)]
                    # prendo la prima epoca precedente
                    prev_gpst = df.index[df.index < current_gpst].max()
                    # prendo la prima epoca successiva
                    next_gpst = df.index[df.index > current_gpst].min()
                    # prendo i dati della prima epoca precedente
                    prev_row = df.loc[prev_gpst]
                    # prendo i dati della prima epoca successiva
                    next_row = df.loc[next_gpst]
                    
                    new_row = {}
                    # GPST: ce l'ho già
                    new_row['GPST'] = current_gpst
                    # x-ecef(m), y-ecef(m), z-ecef(m): media tra epoca precedente e successiva
                    new_row['x-ecef(m)'] = (prev_row['x-ecef(m)'] + next_row['x-ecef(m)']) / 2
                    new_row['y-ecef(m)'] = (prev_row['y-ecef(m)'] + next_row['y-ecef(m)']) / 2
                    new_row['z-ecef(m)'] = (prev_row['z-ecef(m)'] + next_row['z-ecef(m)']) / 2
                    # Q e ns: non mi interessa...
                    new_row['Q'] = min(prev_row['Q'], next_row['Q'])
                    new_row['ns'] = min(prev_row['ns'], next_row['ns'])                
                    # sdx(m), sdy(m), sdz(m), sdxy(m), sdyz(m), sdzx(m): prendo il valore più alto
                    new_row['sdx(m)'] = max(prev_row['sdx(m)'], next_row['sdx(m)'])
                    new_row['sdy(m)'] = max(prev_row['sdy(m)'], next_row['sdy(m)'])
                    new_row['sdz(m)'] = max(prev_row['sdz(m)'], next_row['sdz(m)'])
                    new_row['sdxy(m)'] = max(prev_row['sdxy(m)'], next_row['sdxy(m)'])
                    new_row['sdyz(m)'] = max(prev_row['sdyz(m)'], next_row['sdyz(m)'])
                    new_row['sdzx(m)'] = max(prev_row['sdzx(m)'], next_row['sdzx(m)'])
                    # age(s) e ratio: non mi interessa...
                    new_row['age(s)'] = 0 # max(prev_row['age(s)'], next_row['age(s)'])
                    new_row['ratio'] = max(prev_row['ratio'], next_row['ratio'])
                    
                    # aggiorno la riga al DataFrame
                    df.loc[current_gpst] = new_row
                    
                    # aggiorno il DataFrame
                    dataframes[rovers.index(r)] = df
        
        # prima di passare all'epoca successiva, aggiorno il DataFrame finale
        # 3) interpolazione pesata con l'inverso delle varianze
        # - GPST: ce l'ho già
        # - x-ecef(m), y-ecef(m), z-ecef(m): media pesata tra i rover validi. In particolare: sommatoria di (x_i / sdi^2) / sommatoria di (1 / sdi^2)
        new_row = {}
        new_row['GPST'] = current_gpst
        new_row['x-ecef(m)'] = 0
        new_row['y-ecef(m)'] = 0
        new_row['z-ecef(m)'] = 0
        # somma dei pesi
        weights = {
            'x-ecef(m)': 0,
            'y-ecef(m)': 0,
            'z-ecef(m)': 0,
        }
        for kDf, df in enumerate(dataframes):
            new_row['x-ecef(m)'] += df.loc[current_gpst]['x-ecef(m)'] * (df.loc[current_gpst]['sdx(m)'] ** -2)
            new_row['y-ecef(m)'] += df.loc[current_gpst]['y-ecef(m)'] * (df.loc[current_gpst]['sdy(m)'] ** -2)
            new_row['z-ecef(m)'] += df.loc[current_gpst]['z-ecef(m)'] * (df.loc[current_gpst]['sdz(m)'] ** -2)
            weights['x-ecef(m)'] += (df.loc[current_gpst]['sdx(m)'] ** -2)
            weights['y-ecef(m)'] += (df.loc[current_gpst]['sdy(m)'] ** -2)
            weights['z-ecef(m)'] += (df.loc[current_gpst]['sdz(m)'] ** -2)
        # faccio la media pesata
        new_row['x-ecef(m)'] /= weights['x-ecef(m)']
        new_row['y-ecef(m)'] /= weights['y-ecef(m)']
        new_row['z-ecef(m)'] /= weights['z-ecef(m)']
        # - Q e ns: non mi interessa...
        new_row['Q'] = 0
        new_row['ns'] = 0
        # - sdx(m), sdy(m), sdz(m): prendo il valore più alto
        new_row['sdx(m)'] = 0
        new_row['sdy(m)'] = 0
        new_row['sdz(m)'] = 0
        # - sdxy(m), sdyz(m), sdzx(m): prendo il valore più alto
        new_row['sdxy(m)'] = 0
        new_row['sdyz(m)'] = 0
        new_row['sdzx(m)'] = 0
        for kDf, df in enumerate(dataframes):
            new_row['sdx(m)'] = max(new_row['sdx(m)'], df.loc[current_gpst]['sdx(m)'])
            new_row['sdy(m)'] = max(new_row['sdy(m)'], df.loc[current_gpst]['sdy(m)'])
            new_row['sdz(m)'] = max(new_row['sdz(m)'], df.loc[current_gpst]['sdz(m)'])
            new_row['sdxy(m)'] = max(new_row['sdxy(m)'], df.loc[current_gpst]['sdxy(m)'])
            new_row['sdyz(m)'] = max(new_row['sdyz(m)'], df.loc[current_gpst]['sdyz(m)'])
            new_row['sdzx(m)'] = max(new_row['sdzx(m)'], df.loc[current_gpst]['sdzx(m)'])
        # - age(s) e ratio: non mi interessa...
        new_row['age(s)'] = 0
        new_row['ratio'] = 0
        
        # aggiungo la riga al DataFrame finale
        final_df.loc[current_gpst] = new_row
        
        # passo all'epoca successiva
        current_gpst += pd.Timedelta(seconds=1)
        
    # salvo il DataFrame finale in un pickle
    final_df.to_pickle(f"{workingDirectory}/final_df.pkl")
    # salvo il DataFrame finale in un file .pos
    final_df.to_csv(f"{workingDirectory}/final_df.pos", sep=' ', index=True, header=True)

    # stampo il DataFrame finale
    print("Final DataFrame:")
    print(final_df)

# algorithm()
    
# read from pickle
print("Reading final DataFrame from pickle...")
final_df = pd.read_pickle(f"{workingDirectory}/final_df.pkl")

import matplotlib.pyplot as plt

# Plot each DataFrame's x-ecef(m), y-ecef(m), and z-ecef(m) on separate line graphs (stacked vertically)
fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

# Plot x-ecef(m)
for kDf, df in enumerate(dataframes):
    axes[0].plot(df.index, df['x-ecef(m)'], label=f"{rovers[kDf].name}")
axes[0].plot(final_df.index, final_df['x-ecef(m)'], label="Final", linestyle='--', color='red')
axes[0].set_ylabel("x-ecef(m)")
axes[0].set_title("ECEF Coordinates Over Time")
axes[0].legend()
axes[0].grid()

# Plot y-ecef(m)
for kDf, df in enumerate(dataframes):
    axes[1].plot(df.index, df['y-ecef(m)'], label=f"{rovers[kDf].name}")
axes[1].plot(final_df.index, final_df['y-ecef(m)'], label="Final", linestyle='--', color='red')
axes[1].set_ylabel("y-ecef(m)")
axes[1].legend()
axes[1].grid()

# Plot z-ecef(m)
for kDf, df in enumerate(dataframes):
    axes[2].plot(df.index, df['z-ecef(m)'], label=f"{rovers[kDf].name}")
axes[2].plot(final_df.index, final_df['z-ecef(m)'], label="Final", linestyle='--', color='red')
axes[2].set_xlabel("GPST")
axes[2].set_ylabel("z-ecef(m)")
axes[2].legend()
axes[2].grid()

plt.tight_layout()
plt.show()