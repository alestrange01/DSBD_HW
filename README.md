Sistema distribuito di ticker
# Sistema distribuito di ticker
Questo progetto implementa un sistema distribuito basato su un'architettura a servizi per la gestione di utenti e dei ticker di loro interesse.
L'applicazione è suddivisa in tre componenti principali
(`server`, `data_collector` e `data_cleaner`), sfruttando un approccio modulare per garantire scalabilità e resilienza.
---

---
## **Abstract**
Questo progetto realizza un sistema distribuito basato su un'architettura a microservizi per la gestione e l'elaborazione di dati relativi a titoli azionari. L'applicazione, suddivisa in tre componenti principali (server, data_collector e data_cleaner), utilizza un approccio modulare per garantire scalabilità e resilienza. Il sistema implementa un meccanismo di autenticazione che distingue tra utenti "user" e "admin", conferendo a quest'ultimo priorità operative come la registrazione, l'aggiornamento e la cancellazione di altri utenti ma anche la visualizzazione di tutte le informazioni presenti nel DB. 

La comunicazione tra client e server avviene tramite gRPC, garantendo efficienza e bassa latenza. Il server adotta la politica di at-most-once per assicurare che ogni richiesta sia processata al massimo una volta, per garantire l’idempotenza delle operazioni e migliorare l’efficienza del sistema. Gli altri microservizi operano autonomamente, attivati periodicamente da uno scheduler per raccogliere e pulire i dati.

La gestione dei dati è centralizzata in un database relazionale composto da tre tabelle principali. La tabella users gestisce le informazioni sugli utenti, tra cui email e il ticker azionario associato. La tabella shares registra i dati relativi ai titoli azionari (titolo, valore e un timestamp). Infine, la tabella ticker_management tiene traccia dell'utilizzo dei ticker azionari tramite un contatore, garantendo che i ticker non utilizzati vengano eliminati poi per ottimizzare lo spazio.

Il pattern Circuit Breaker gestisce le chiamate verso servizi esterni, come Yahoo Finance, proteggendo da guasti e fallimenti ripetuti. In caso di errori, il circuito si apre temporaneamente, impedendo nuove richieste, e passa successivamente a uno stato "half-open" per verificare il recupero del servizio. 

---
## **Diagramma architetturale**
---
## **Diagramma delle interazioni**
---
## **Schema del database**
1. Tabella **users**:  Memorizza le informazioni dell'utente, come l'e-mail e il ticker azionario associato.
 - Colonne: `id`, `email`, `password`, `ticker`.
2. Tabella **shares**: Registra i dati delle azioni, cioé ticker, valore e timestamp.
 - Colonne: `id`, `ticker`, `valore`, `timestamp`.
3. Tabella **gestione_ticker**: Tiene traccia dell'uso dei ticker da parte degli utenti e rimuove quelli inutilizzati per ottimizzare lo spazio.
 - Colonne: `ticker`, `conteggio_uso`.
---
## **Caratteristiche del sistema**
1. **Credenziali di default**:
 - **Admin**: `admin@gmail.com` / `admin`
 - **Utente**: `user1@gmail.com` / `user1`
2. **Funzionalità del client**:
 - Verifica delle funzionalità della piattaforma, login, registrazione/modifica/cancellazione utente, richiesta ticker value o ticker mean, inoltre é possibile testare la validitá della cache con l'apposita funzione: `Test cache`.
 - Per testare la funzionalità del circuit breaker in maniera automatica all'avvio del data_collector_cointainer bisogna decommentare riga 8 del file data_collector_main.py all'interno della directory data_collector.
---
## **Guida al build & deploy**
### **Prequisiti**
Assicurarsi che siano installati i seguenti elementi:
- **Docker**
- **Docker Compose**
### **Passi**
1. **Clonare il repository**
 ```bash
 git clone https://github.com/alestrange01/APL_prove.git
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
