 - Aggiornamento Calendario Dal/Al
[ ] - Sistemare printLog()
[X] - Sistemare CustomTimeDialog
[X] - Reverse engineering di come viene calcolata (sd...) perché è negativo
[X] - Conversione in UTM 32N/33N (auto-detect dalla longitudine, non 44 ma 12...). Metti coordinate rappresentazione e coordinate convertite in utm in un file "aggiornato"

[ ] - Integrazione della stazione base (OK, ma manca il .pos della stazione base!)

[X] - ppp-kinematic come position mode va bene quando sei in movimento. Quando sei fermo risente del filtro di Kalman e quindi vacilla (in quel caso occorre usare ppp-static). Mettere un campo in cui fare lo switch, altrimenti di default usare ppp-kinematic.
[X] - Controlla se effettivamente prende il broadcast quando non selezioni il .nav o questo non esiste!
[ ] - Controlla che i files selezionati siano giusti (stazione base)
[ ] - nascondere i POS in roverTab

[ ] - rappresentazione dinamica delle grandezze nel tempo e altezza

https://gis.stackexchange.com/questions/78838/converting-projected-coordinates-to-lat-lon-using-python
https://www.google.com/search?q=pyqt+status+bar+message&sca_esv=573962864

pyuic5 input.ui -o output.py