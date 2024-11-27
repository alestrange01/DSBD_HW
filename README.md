Sistema distribuito di ticker
# Sistema distribuito di ticker
Questo progetto implementa un sistema distribuito basato su un'architettura a servizi per la gestione di utenti e dei ticker di loro interesse.
L'applicazione è suddivisa in tre componenti principali
(`server`, `data_collector` e `data_cleaner`), sfruttando un approccio modulare per garantire scalabilità e resilienza.
---

---
## **Abstract**

Questo progetto realizza un sistema distribuito basato su un'architettura a microservizi per la gestione e l'elaborazione di dati relativi a titoli azionari. L'applicazione, suddivisa in tre componenti principali (server, data_collector e data_cleaner), utilizza un approccio modulare per garantire scalabilità e resilienza. Il sistema implementa un meccanismo di autenticazione che distingue tra utenti "user" e "admin", conferendo a quest'ultimo priorità operative come la registrazione, l'aggiornamento e la cancellazione di altri utenti ma anche la visualizzazione di tutte le informazioni presenti nel DB. 

La comunicazione tra client e server avviene tramite gRPC, garantendo trasparenza ed efficienza. Il server adotta la politica di at-most-once per assicurare che ogni richiesta sia processata al massimo una volta, per garantire l’idempotenza delle operazioni e migliorare l’efficienza del sistema. Gli altri microservizi operano autonomamente, attivati periodicamente da uno scheduler per raccogliere e pulire i dati.

La gestione dei dati è centralizzata in un database relazionale composto da tre tabelle principali. La tabella users gestisce le informazioni sugli utenti, tra cui email e il ticker azionario associato. La tabella shares registra i dati relativi ai titoli azionari (titolo, valore e un timestamp). Infine, la tabella ticker_management tiene traccia dell'utilizzo dei ticker azionari tramite un contatore, garantendo che i ticker non utilizzati vengano eliminati poi per ottimizzare lo spazio.

Il pattern Circuit Breaker gestisce le chiamate verso servizi esterni, come Yahoo Finance, proteggendo da guasti e fallimenti ripetuti. In caso di errori, il circuito si apre temporaneamente, impedendo nuove richieste, e passa successivamente a uno stato "half-open" per verificare il recupero del servizio. 

---
## **Scelte architetturali**
Abbiamo scelto di suddividere il sistema in tre microservizi distinti per garantire una chiara separazione delle responsabilità e una maggiore modularità. 

In particolare, abbiamo deciso di creare un terzo microservizio dedicato, il Data Cleaner, separato logicamente dal Data Collector, nonostante entrambi operino sui dati dei ticker azionari. Questa scelta è stata motivata dall'esigenza di distinguere nettamente le operazioni di raccolta e aggiornamento dei dati da quelle di pulizia e ottimizzazione del database.

Ogni microservizio ha un ruolo ben definito e indipendente, consentendo di isolare eventuali problematiche e facilitare la risoluzione dei guasti. Questo approccio offre diversi vantaggi:
- Scalabilità: Ogni componente può essere scalato indipendentemente in base al carico specifico, ottimizzando l'uso delle risorse senza dover aumentare inutilmente le capacità dell'intero sistema.
- Manutenibilità: Grazie alla suddivisione dei compiti, il codice di ciascun microservizio è più leggibile e modulare, facilitando sia lo sviluppo che l'introduzione di nuove funzionalità senza impattare sugli altri componenti.
- Resilienza: L'indipendenza tra i microservizi limita l'impatto di eventuali guasti, mantenendo operativo il resto del sistema. Inoltre, il Data Collector utilizza un pattern come il Circuit Breaker per isolare i problemi legati ai servizi esterni.
- Flessibilità nello sviluppo: Il team può lavorare su diversi microservizi in parallelo, scegliendo tecnologie e strumenti più adatti per ciascun componente.

---
## **Scelte implementative**
La politica di *at-most-once* è stata implementata utilizzando un meccanismo basato su un identificativo univoco della richiesta (`request_id`), generato dal client per ogni richiesta. Il server mantiene una cache strutturata organizzata come un dizionario annidato, in cui:

- Il primo livello di chiave rappresenta il tipo di operazione (`op_code`, come `GET`, `POST`, `PUT`, `DEL`).
- Il secondo livello utilizza una chiave unica costruita combinando l'email del client (`user_email`) e il `request_id` della richiesta. 

Questa combinazione, denominata `user_request_id`, garantisce che ogni richiesta venga identificata in modo univoco. 

Quando il server riceve una nuova richiesta, verifica nella cache se esiste già una risposta associata a quel `request_id`:
- **Se presente**, restituisce direttamente la risposta memorizzata, evitando di rielaborare la richiesta.
- **Se assente**, il server elabora la richiesta, genera una risposta e memorizza nella cache un oggetto che include:
  - La risposta generata.
  - Un `timestamp` che rappresenta il momento dell'elaborazione.

Il `timestamp` è utilizzato per gestire la pulizia periodica della cache, eliminando voci obsolete e garantendo che la memoria occupata dalla cache rimanga sotto controllo.

Questo approccio garantisce che ogni richiesta venga processata al massimo una volta, evitando computazioni ridondanti, anche in caso di retry da parte del client a causa di timeout o perdita della risposta. Il sistema è progettato per isolare le richieste dei diversi client e per rendere la gestione dei duplicati trasparente e affidabile.

---
## **Diagramma architetturale**
![Architettura](https://github.com/alestrange01/APL_prove/blob/main/img/Diagramma_architettura.png)
---
## **Diagramma delle interazioni**

**Registra Utente**

L'utente invia una richiesta per registrarsi al sistema. Il server verifica se la richiesta è già in cache. In caso contrario, tenta l’inserimento del nuovo record nella tabella users ed in caso aggiorna la tabella ticker_management per tracciare il ticker azionario associato all'utente.
![op1](https://github.com/alestrange01/APL_prove/blob/main/img/op1.png)

**Login**

Un utente o un amministratore invia una richiesta di login. Il server controlla la cache o legge dalla tabella users per autenticare l'utente. A seconda del ruolo, restituisce un oggetto user o admin.
![op2](https://github.com/alestrange01/APL_prove/blob/main/img/op2.png)

**Elimina Utente**

Un amministratore richiede la cancellazione di un utente o un utente del proprio account. Il server verifica prima in cache e poi elimina il record dalla tabella users. Successivamente, aggiorna la tabella ticker_management per decrementare il counter del tiker associato all’utente eleliminato.
![op3](https://github.com/alestrange01/APL_prove/blob/main/img/op3.png)

**Modifica Utente**

Un utente o un admin invia una richiesta per aggiornare i propri dati (o quelli di un altro utente). Il server verifica la cache e, in caso di assenza, aggiorna il record nella tabella users. Viene anche aggiornata la tabella ticker_management per riflettere eventuali cambiamenti.
![op4](https://github.com/alestrange01/APL_prove/blob/main/img/op4.png)

**Richiedi share value**

L'utente richiede il valore più recente di un titolo azionario specifico. Il server controlla la cache o esegue una query nella tabella shares per recuperare il valore associato al ticker specificato.
![op5](https://github.com/alestrange01/APL_prove/blob/main/img/op5.png)

**Richiedi share mean**

L'utente richiede il valore medio dei titoli azionari per un determinato nome di share. Il server esegue una query nella tabella shares per calcolare e restituire il valore medio.
![op6](https://github.com/alestrange01/APL_prove/blob/main/img/op6.png)

**Richiedi tutti gli utenti**

Un amministratore richiede la lista di tutti gli utenti registrati. Il server verifica se i dati sono già in cache, altrimenti esegue una query sulla tabella users e restituisce l'elenco degli utenti.
![op7](https://github.com/alestrange01/APL_prove/blob/main/img/op7.png)

**Richiedi tutti gli shares**

Un amministratore richiede la lista di tutti i titoli azionari. Il server controlla la cache o esegue una query sulla tabella shares per restituire i dati di tutti i titoli.
![op8](https://github.com/alestrange01/APL_prove/blob/main/img/op8.png)

**Richiedi tutti i ticker managements**

Un amministratore richiede i dati di gestione dei ticker. Il server verifica la cache o esegue una query sulla tabella ticker_management per restituire i dati relativi ai ticker.
![op9](https://github.com/alestrange01/APL_prove/blob/main/img/op9.png)

**Data collector**

Il DataCollector è un microservizio responsabile della raccolta e dell'aggiornamento dei dati relativi ai titoli azionari.
- Loop continuo: Il DataCollector esegue periodicamente un ciclo per raccogliere i dati sui titoli azionari.
- Selezione ticker attivi: Interroga la tabella ticker_management per recuperare i ticker con contatore diverso da zero, che rappresentano i ticker attivamente monitorati dagli utenti.
- Chiamate al Circuit Breaker: Per ogni ticker, utilizza il Circuit Breaker per effettuare richieste a Yahoo Finance. Il Circuit Breaker gestisce guasti e fallback in caso di errori temporanei.
- Recupero e inserimento dati: Dopo aver recuperato il valore del titolo, il servizio inserisce un nuovo record nella tabella shares con il valore recuperato.
![data_collector](https://github.com/alestrange01/APL_prove/blob/main/img/DataCollector.png)

**Data cleaner**

Il DataCleaner è un microservizio che opera autonomamente per garantire la pulizia dei dati non più rilevanti nel sistema, migliorando l'efficienza e l'utilizzo dello spazio nel database.
- Loop continuo: Il DataCleaner esegue periodicamente un ciclo per effettuare operazioni di pulizia.
- Eliminazione dati obsoleti: Vengono rimossi i record dalla tabella shares con un timestamp più vecchio di 14 giorni, assicurandosi che solo dati recenti siano mantenuti.
- Verifica e rimozione ticker inutilizzati: Seleziona i ticker dalla tabella ticker_management con contatore a zero (indicando che non sono associati ad alcun utente attivo) e ne rimuove i record.
![data_cleaner](https://github.com/alestrange01/APL_prove/blob/main/img/DataCleaner.png)

---
## **Schema del database**
1. Tabella **users**:  Memorizza le informazioni dell'utente, come l'e-mail e il ticker azionario associato.
 - Colonne: `id`, `email`, `password`, `ticker`.
2. Tabella **shares**: Registra i dati delle azioni, cioé ticker, valore e timestamp.
 - Colonne: `id`, `ticker`, `valore`, `timestamp`.
3. Tabella **gestione_ticker**: Tiene traccia dell'uso dei ticker da parte degli utenti e rimuove quelli inutilizzati per ottimizzare lo spazio.
 - Colonne: `ticker`, `counter`.
---
## **Caratteristiche del sistema**
1. **Credenziali di default**:
 - **Admin**: `admin@gmail.com` / `admin`
 - **Utente**: `user1@gmail.com` / `user1`
2. **Funzionalità del client**:
 - Verifica delle funzionalità della piattaforma, login, registrazione/modifica/cancellazione utente, richiesta ticker value o ticker mean. Inoltre, previa essersi loggati come admin, é possibile visualizzare le tabelle del DB e testare la validitá dell'implementazione di at-most-once con l'apposita funzione: `test_at_most_once_policy()`.
   - Il comportamento del codice verifica la politica "at-most-once" per garantire che ogni richiesta venga processata una sola volta. Al primo tentativo, il server introduce un ritardo di 10 secondi, ma il client, avendo un timeout di 8 secondi, registra un timeout e ritenta. Al secondo tentativo, il server risponde dopo 5 secondi e il client riceve con successo la risposta. Infine, al terzo tentativo, la risposta è già memorizzata nella cache del server, che la restituisce immediatamente, permettendo al client di completare rapidamente l'operazione. Il processo garantisce l'idempotenza, assicurando che ogni richiesta venga processata al massimo una volta, evitando duplicazioni e migliorando l'efficienza.
 - Per testare la funzionalità del circuit breaker in maniera automatica all'avvio del data_collector_cointainer bisogna decommentare riga 8 del file data_collector_main.py all'interno della directory data_collector la chiamata alla funzione: `test_circuit_breaker_behavior()`.
   - La funzione test_circuit_breaker_behavior simula il funzionamento di un Circuit Breaker e dimostra come gestisce le richieste passando tra i suoi stati principali: CLOSED, OPEN e HALF_OPEN. L'obiettivo è proteggere il sistema da guasti ripetuti e verificare la stabilità prima di tornare al normale funzionamento.
All'inizio, il Circuit Breaker è nello stato CLOSED, accettando tutte le richieste. Durante le prime chiamate, si verificano alcuni successi e fallimenti. Al quinto fallimento, indipendentemente dal fatto che siano consecutivi o meno, il Circuit Breaker raggiunge la soglia configurata e passa allo stato OPEN, bloccando tutte le chiamate successive. In questo stato, ogni nuova richiesta viene immediatamente rifiutata per evitare ulteriori problemi.
Dopo un timeout di recupero, il Circuit Breaker passa nello stato HALF_OPEN, in cui consente alcune richieste per testare se il sistema è tornato stabile. Le prime chiamate hanno successo, ma al terzo fallimento (poiché la soglia difference_failure_open_half_open è impostata a 2), il Circuit Breaker torna temporaneamente nello stato OPEN. Successivamente, dopo un altro periodo di timeout, torna in HALF_OPEN. Questa volta, un numero sufficiente di successi consecutivi consente al Circuit Breaker di tornare allo stato CLOSED, ripristinando il normale funzionamento.
Questo test dimostra come il Circuit Breaker gestisca i guasti in modo intelligente: blocca le richieste quando necessario, verifica la stabilità con richieste limitate e si ripristina completamente solo quando il sistema dimostra di essere stabile.
---
## **Guida al build & deploy**
### **Prequisiti**
Assicurarsi che siano installati i seguenti elementi:
- **Docker**
- **Docker Compose**
### **Passi**
1. **Clonare il repository**
 ```bash
 git clone https://github.com/alestrange01/DSBD_HW1.git
 cd root/project
 ```
2. **Costruire le immagini Docker**
 Eseguire il seguente comando per costruire tutti i servizi:
 ```bash
 docker compose build
 ```
3. **Avviare l'applicazione**
 Avviare tutti i microservizi e il database:
 ```bash
 docker compose up
 ```
4. **Eseguire il client**
 Navigare nella directory del server ed eseguire lo script del client:
 ```bash
 cd server/
 python client_main.py
 ```
---
## **Riassunto dell'architettura**
Il sistema comprende:
- **Server**: Gestisce le interazioni con gli utenti e le operazioni del database.
- **Data collector**: Recupera periodicamente i dati sugli shares.
- **Data Cleaner**: Ottimizza il database rimuovendo le informazioni obsolete.
- **Database**: Istanza PostgreSQL per la persistenza dei dati.

Tutti i componenti sono orchestrati utilizzando **Docker Compose** e la comunicazione tra client e server avviene tramite **gRPC**.
