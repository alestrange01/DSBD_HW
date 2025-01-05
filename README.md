Sistema distribuito di ticker

# Sistema distribuito di ticker

Questo progetto implementa un sistema distribuito basato su un'architettura a microservizi per la gestione di utenti e dei ticker di loro interesse.
L'applicazione è composta da cinque componenti principali
(`server`, `data_collector`, `data_cleaner`, `alert_system` e `alert_notification_system`), che permette di sfruttare un approccio modulare per garantire scalabilità e resilienza, e da due componenti per la gestione del monitoraggio delle metriche (`prometheus` e `alert_manager`).
--------------------------------------------------------------------------------------

---

## **Abstract**

Questo progetto realizza un **sistema distribuito** basato su un'**architettura a microservizi** per la gestione e l'elaborazione di dati relativi a titoli azionari. L'applicazione, suddivisa in cinque componenti principali (server, data_collector, data_cleaner, alert_system e alert_notification_system), utilizza un approccio modulare per garantire scalabilità e resilienza. Il sistema implementa un meccanismo di autenticazione che distingue tra utenti "user" e "admin", conferendo a quest'ultimo priorità operative come la registrazione, l'aggiornamento e la cancellazione di altri utenti ma anche la visualizzazione di tutte le informazioni presenti nel DB.

La comunicazione tra client e server avviene tramite **gRPC**, garantendo trasparenza ed efficienza. Il server adotta la politica di **at-most-once** per assicurare che ogni richiesta sia processata al massimo una volta, per garantire l’idempotenza delle operazioni e migliorare l’efficienza del sistema. Gli altri microservizi operano autonomamente, attivati periodicamente da uno scheduler per raccogliere e pulire i dati.

La comunicazione tra `data_collector` e `alert_system` e tra `alert_system` e `alert_notification_system` avviente tramite **Apache Kafka**, un broker che permette di avere maggior robustezza, una maggiore resilienza del sistema e una migliore gestione dei picchi di traffico.

L'alert_system utilizza il topic Kafka `to-alert-system` per rilevare quando il data_collector completa la raccolta dei dati. Legge i dati più recenti dal database, elabora eventuali valori che superano soglie predefinite (come limiti massimi o minimi) e invia notifiche sul topic `to-notifier`. L'alert_notification_system consuma questi messaggi dal topic e notifica gli utenti via email, garantendo un flusso reattivo ed efficace per la gestione degli alert.

La gestione dei dati è centralizzata in un database relazionale composto da tre tabelle principali. La tabella users gestisce le informazioni sugli utenti, tra cui email e il ticker azionario associato. La tabella shares registra i dati relativi ai titoli azionari (titolo, valore e un timestamp). Infine, la tabella ticker_management tiene traccia dell'utilizzo dei ticker azionari tramite un contatore, garantendo che i ticker non utilizzati vengano eliminati poi per ottimizzare lo spazio.

Il pattern **Circuit Breaker** gestisce le chiamate verso servizi esterni, come Yahoo Finance, proteggendo da guasti e fallimenti ripetuti. In caso di errori, il circuito si apre temporaneamente, impedendo nuove richieste, e passa successivamente a uno stato "half-open" per verificare il recupero del servizio.

Per il monitoraggio del sistema, abbiamo integrato **Prometheus**, che raccoglie e analizza metriche chiave, offrendo una visione in tempo reale dello stato e delle prestazioni del sistema. Questa integrazione consente di identificare rapidamente eventuali anomalie, configurare alert basati su soglie critiche e ottimizzare i microservizi grazie a metriche come latenza, #richieste ed errori.

---

## **Scelte architetturali**

Abbiamo scelto di suddividere il sistema in cinque microservizi distinti per garantire una chiara separazione delle responsabilità e una maggiore modularità.

In particolare, abbiamo deciso di creare un microservizio dedicato, il Data Cleaner, separato logicamente dal Data Collector, nonostante entrambi operino sui dati dei ticker azionari. Questa scelta è stata motivata dall'esigenza di distinguere nettamente le operazioni di raccolta e aggiornamento dei dati da quelle di pulizia e ottimizzazione del database.

Ogni microservizio ha un ruolo ben definito e indipendente, consentendo di isolare eventuali problematiche e facilitare la risoluzione dei guasti. Questo approccio offre diversi vantaggi:

- **Scalabilità**: Ogni componente può essere scalato indipendentemente in base al carico specifico, ottimizzando l'uso delle risorse senza dover aumentare inutilmente le capacità dell'intero sistema.
- **Manutenibilità**: Grazie alla suddivisione dei compiti, il codice di ciascun microservizio è più leggibile e modulare, facilitando sia lo sviluppo che l'introduzione di nuove funzionalità senza impattare sugli altri componenti.
- **Resilienza**: L'indipendenza tra i microservizi limita l'impatto di eventuali guasti, mantenendo operativo il resto del sistema. Inoltre, il Data Collector utilizza un pattern come il Circuit Breaker per isolare i problemi legati ai servizi esterni.
- **Flessibilità nello sviluppo**: Il team può lavorare su diversi microservizi in parallelo, scegliendo tecnologie e strumenti più adatti per ciascun componente.

Abbiamo scelto di adottare il pattern **CQRS** (Command and Query Responsibility Segregation) sia nei service del server che nei repository di tutti i microservizi per i seguenti motivi:

- **Separazione delle responsabilità**:
  - CQRS separa le operazioni di lettura (Query) da quelle di scrittura (Command), semplificando ciascuna delle due. Questo approccio si traduce in codice più chiaro e più facile da mantenere.
- **Scalabilità**:
  - Con CQRS è possibile ottimizzare la lettura e la scrittura in modo indipendente.
- **Flessibilità evolutiva**:
  - CQRS facilita l'introduzione di nuove funzionalità, come cache dedicate per le query o pipeline di eventi per aggiornamenti asincroni dei dati.

Abbiamo utilizzato **Apache Kafka** come broker di messaggi per comunicare tra i microservizi per queste ragioni:

- **Alta affidabilità**:
  - Kafka garantisce durabilità e tolleranza ai guasti, essenziali in un sistema distribuito. Le opzioni di configurazione (es. acks=all) assicurano che i messaggi siano confermati solo quando sono stati scritti in tutte le partizioni.
- **Gestione del carico elevato**:
  - Kafka è ottimizzato per throughput elevati, gestendo milioni di messaggi al secondo, ideale per un ecosistema di microservizi.
- **Consistenza ed elaborazione garantita**:
  - Con configurazioni come enable.auto.commit=False, possiamo gestire manualmente il commit degli offset, garantendo che i messaggi vengano elaborati esattamente una volta, evitando duplicazioni o perdite.
- **Facilità di integrazione**:
  - Kafka offre un supporto nativo per le code di messaggi persistenti e distribuite, semplificando il coordinamento tra i microservizi.
 
Per il monitoraggio del sistema, abbiamo scelto di integrare **Prometheus**. Questa scelta ci consente di beneficiare dei seguenti vantaggi:

- **Visibilità in tempo reale**:
  - Prometheus raccoglie e visualizza metriche in tempo reale, permettendoci di monitorare lo stato di ogni microservizio e identificare rapidamente eventuali problemi.
- **Allarmi configurabili**:
  - Grazie alla sua capacità di definire regole di alerting, Prometheus ci notifica automaticamente in caso di anomalie o soglie critiche, migliorando la resilienza del sistema.
- **Flessibilità nella definizione delle metriche**:
  - Possiamo definire metriche personalizzate per ogni microservizio, monitorando aspetti specifici come il numero di messaggi elaborati, il tempo di risposta ed il numero di errori.
- **Scalabilità**:
  - Prometheus è ottimizzato per sistemi distribuiti, rendendolo ideale per l'integrazione in un'architettura basata su microservizi.


---

## **Scelte implementative**

- La politica di *at-most-once* è stata implementata utilizzando un meccanismo basato su un identificativo univoco della richiesta (`request_id`), generato dal client per ogni richiesta. Il server mantiene una cache strutturata organizzata come un dizionario annidato, in cui:

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
- Il pattern CQRS è stato implementato:

  - nel server gRPC andando a dividere le operazioni di scrittura da quelle di lettura creando lo `UserReaderService` e `UserWriterService`.
  - nei repository creando per ogni entity un repository di lettura(reader) e uno di scrittura(writer).
- Abbiamo configurato i producer ed i consumer all'interno della nostra applicazione adattandoli alle nostre esigenze:

  - **Data Collector Producer**

    ```
    'bootstrap.servers': 'kafka-broker:9092',  
    'acks': 'all',  
    'batch.size': 500,  
    'linger.ms': 500,
    'max.in.flight.requests.per.connection': 1,  
    'retries': 3 
    ```

    Il producer del **Data Collector** è responsabile di inviare messaggi al topic `to-alert-system`. La configurazione del producer include i seguenti parametri:

    - **`bootstrap.servers`**: Specifica il broker Kafka a cui connettersi (`kafka-broker:9092`).
    - **`acks: 'all'`**:
      - Garantisce che il messaggio sia scritto in **tutte le repliche** delle partizioni prima di essere confermato come consegnato.
      - Fornisce **robustezza** e **durabilità** maggiore, ma aumenta la latenza.
    - **`batch.size: 500`**:
      - Limita la dimensione massima del batch (in byte) che il producer accumula prima di inviarlo.
      - Accumulare batch riduce il numero di richieste al broker, migliorando l'efficienza.
    - **`linger.ms: 500`**:
      - Introduce un **ritardo massimo di 500 ms** per consentire l'accumulo di più messaggi in batch prima di inviarli.
      - Se il batch si riempie prima del timeout, viene inviato immediatamente.
    - **`max.in.flight.requests.per.connection: 1`**:
      - Garantisce che una sola richiesta sia inviata alla volta, prevenendo potenziali problemi di ordine nel caso di ritrasmissioni.
    - **`retries: 3`**:
      - Specifica il numero massimo di tentativi che il producer farà in caso di errori temporanei (es. rete non disponibile o leader della partizione non trovato).

    Questa configurazione privilegia la **robustezza** e l'**affidabilità** rispetto alla latenza, garantendo che i messaggi siano sempre consegnati e replicati correttamente.

    - **Alert System Consumer**

    ```
    'bootstrap.servers': 'kafka-broker:9092',  
    'group.id': 'group1', 
    'auto.offset.reset': 'earliest',  
    'enable.auto.commit': False
    ```

    Il **consumer** del topic `to-alert-system` nell'**Alert System** è stato configurato per leggere i messaggi prodotti dal **Data Collector**.  La configurazione del consumer include i seguenti parametri:

    - **`bootstrap.servers`**: Specifica il broker Kafka a cui connettersi.
    - **`group.id`**: Identifica il gruppo di consumer come `group1`. Tutti i consumer che appartengono a questo gruppo condividono il carico del topic assegnato, consumando messaggi in modo bilanciato.
    - **`auto.offset.reset`**: Specifica il comportamento del consumer in caso di mancanza di un offset salvato:

      - `earliest`: Legge i messaggi dalla prima posizione disponibile.
      - `latest`: Consuma solo i messaggi pubblicati dopo l'avvio del consumer.
    - **`enable.auto.commit`**: False, il consumer salva manualmente l'offset dopo aver elaborato i messaggi. Questo approccio garantisce che i messaggi vengano processati con successo prima di aggiornare l'offset.
    - **Alert System Producer**

    ```
    'bootstrap.servers': 'kafka-broker:9092',  
    'acks': 'all',
    'batch.size': 500,
    'linger.ms': 500,
    'retries': 3
    ```

    Il producer dell'**Alert System** è responsabile di inviare messaggi al topic `to-notifier`. La configurazione del producer include i seguenti parametri:

    - **`bootstrap.servers`**: Specifica il broker Kafka a cui connettersi.
    - **`acks`**: Con `all`, il producer attende la conferma di tutte le repliche, garantendo una maggiore robustezza dei dati.
    - **`batch.size`**: Accumula messaggi fino a un massimo di 500 byte prima di inviarli, ottimizzando le prestazioni.
    - **`linger.ms`**: Introduce un ritardo massimo di 500 ms per consentire l'accumulo di più messaggi in batch prima dell'invio.
    - **`retries`**: Specifica il numero massimo di tentativi per inviare un messaggio in caso di errore temporaneo.

    Questa configurazione garantisce una buona combinazione tra robustezza e performance, assicurando che i messaggi critici vengano consegnati correttamente.

    - **Alert Notification System Consumer**

    ```
    'bootstrap.servers': 'kafka-broker:9092',  
    'group.id': 'group2',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True  
    ```

    L'**Alert Notification System** consuma i messaggi dal topic `to-notifier`, prodotti dall'**Alert System**. La configurazione del consumer include i seguenti parametri:

    - **`bootstrap.servers`**: Specifica il broker Kafka a cui connettersi.
    - **`group.id`**: Identifica il gruppo di consumer come `group2`. Tutti i consumer che appartengono a questo gruppo condividono il carico del topic assegnato, consumando messaggi in modo bilanciato.
    - **`auto.offset.reset`**: Impostato su `earliest`, consente di leggere i messaggi dall'inizio del topic se non sono presenti offset salvati.
    - **`enable.auto.commit`**: Abilitato (`True`), salva automaticamente l'offset dei messaggi dopo la lettura, semplificando la gestione degli offset.
   
- Abbiamo integrato Prometheus per raccogliere e monitorare metriche chiave nei diversi microservizi del sistema: di seguito, un'analisi delle principali metriche implementate:
  - **Server**:
    - **`users`**: Conta il numero totale di utenti gestiti dal sistema, fornendo una misura della crescita del database utenti e dell'interazione con il sistema.
    - **`requests_total`**: Conta il numero di richieste ricevute dal server, distinguendo per metodo (`Login`, `Register`, ecc.) e tipo di risposta (`cached`, `processed`). Questa metrica permette di analizzare il carico del server e il comportamento delle risposte.
    - **`request_duration`**: Misura il tempo impiegato per completare richieste specifiche, distinte per metodo (`Login`, `Register`, ecc.). Forniscono una panoramica delle prestazioni per endpoint critici.
    - **`errors`**: Conta il numero di errori verificatisi durante l'elaborazione delle richieste, classificati per tipo di errore (es. `401 Unauthorized`, `500 Internal Server Error`). Aiuta a monitorare la stabilità del sistema e a identificare problemi ricorrenti.
    - **`cache_size`**: Misura il numero di elementi attualmente presenti nella cache del server. Questa metrica consente di valutare l'efficienza della gestione della cache e di rilevare eventuali sovraccarichi o inefficienze.


  - **Data Collector**:
    - **`tickers_count`**: Numero di ticker monitorati attivamente dal sistema, utile per valutare la scalabilità.
    - **`yf_count`**: Conta le chiamate effettuate a `yfinance`, tracciando l'attività del Data Collector.
    - **`yf_request_duration_seconds`**: Misura la latenza delle chiamate a `yfinance`, evidenziando potenziali colli di bottiglia nelle comunicazioni con i servizi esterni.
  
  - **Data Cleaner**:
    - **`shares_deleted`**: Conta il numero di azioni eliminate dal database, categorizzate per motivazione (`old` o `unused`), utile per monitorare le operazioni di pulizia.
    - **`ticker_management_deleted`**: Conta il numero di ticker eliminati dal sistema di gestione dei ticker, utile per monitorare la pulizia dei dati ticker non più di interesse.
    - **`cleaning_request_duration_seconds`**: Histograms che misurano il tempo impiegato per ogni ciclo di pulizia.
    - **`old_shares_ratio`**: Calcola la percentuale di azioni eliminate perché obsolete rispetto al totale, fornendo informazioni sull'efficienza del Data Cleaner.
  
  - **Alert System**:
    - **`alerts_sent`**: Conta gli alert inviati, distinguendo per tipo (`high_limit`, `low_limit`), utile per monitorare la frequenza e la natura delle notifiche.
    - **`alert_send_latency_seconds`**: Misura il tempo impiegato per inviare un messaggio di alert, tracciando le prestazioni del sistema.
    - **`messages_consumed`** e **`messages_produced_for_notifications`**: Monitorano rispettivamente i messaggi Kafka consumati e prodotti, fornendo visibilità sulle operazioni di comunicazione.
    - **`processing_errors`**: Conta il numero di errori verificatisi durante l'elaborazione dei messaggi, utile per identificare problemi nei flussi di lavoro o nei dati ricevuti.
    - **`delivery_failures`**: Conta i fallimenti nell'invio dei messaggi al topic Kafka, permettendo di monitorare l'affidabilità del sistema.

  
  - **Alert Notification System**:
    - **`messages_consumed`**: Conta il numero di messaggi consumati dal topic Kafka `to-notifier`, garantendo visibilità sull'attività del consumer.
    - **`emails_sent`**: Conta il numero di email inviate con successo agli utenti, evidenziando l'efficacia del sistema.
    - **`email_send_errors`**: Monitora gli errori durante l'invio delle email, utile per identificare problemi nel sistema di notifiche.
    - **`email_send_latency`**: Misura il tempo necessario per inviare un'email, fornendo indicazioni sulle prestazioni del servizio.
      
Queste metriche ci permettono di monitorare l'intero ecosistema di microservizi in modo dettagliato, fornendo una base solida per ottimizzazioni future e garantendo un livello elevato di affidabilità e scalabilità.



---

## **Diagramma architetturale**
![architettura](https://github.com/alestrange01/DSBD_HW/blob/main/img/Diagramma_architettura.png)

## **Diagramma delle interazioni**

**Registra Utente**

L'utente invia una richiesta per registrarsi al sistema. Il server verifica se la richiesta è già in cache. In caso contrario, tenta l’inserimento del nuovo record nella tabella users ed in caso aggiorna la tabella ticker_management per tracciare il ticker azionario associato all'utente.
![op1](https://github.com/alestrange01/DSBD_HW/blob/main/img/op1.png)

**Login**

Un utente o un amministratore invia una richiesta di login. Il server controlla la cache o legge dalla tabella users per autenticare l'utente. A seconda del ruolo, restituisce un oggetto user o admin.
![op2](https://github.com/alestrange01/DSBD_HW/blob/main/img/op2.png)

**Elimina Utente**

Un amministratore richiede la cancellazione di un utente o un utente del proprio account. Il server verifica prima in cache e poi elimina il record dalla tabella users. Successivamente, aggiorna la tabella ticker_management per decrementare il counter del tiker associato all’utente eleliminato.
![op3](https://github.com/alestrange01/DSBD_HW/blob/main/img/op3.png)

**Modifica Utente**

Un utente o un admin invia una richiesta per aggiornare i propri dati (o quelli di un altro utente). Il server verifica la cache e, in caso di assenza, aggiorna il record nella tabella users. Viene anche aggiornata la tabella ticker_management per riflettere eventuali cambiamenti.
![op4](https://github.com/alestrange01/DSBD_HW/blob/main/img/op4.png)

**Richiedi share value**

L'utente richiede il valore più recente di un titolo azionario specifico. Il server controlla la cache o esegue una query nella tabella shares per recuperare il valore associato al ticker specificato.
![op5](https://github.com/alestrange01/DSBD_HW/blob/main/img/op5.png)

**Richiedi share mean**

L'utente richiede il valore medio dei titoli azionari per un determinato nome di share. Il server esegue una query nella tabella shares per calcolare e restituire il valore medio.
![op6](https://github.com/alestrange01/DSBD_HW/blob/main/img/op6.png)

**Richiedi tutti gli utenti**

Un amministratore richiede la lista di tutti gli utenti registrati. Il server verifica se i dati sono già in cache, altrimenti esegue una query sulla tabella users e restituisce l'elenco degli utenti.
![op7](https://github.com/alestrange01/DSBD_HW/blob/main/img/op7.png)

**Richiedi tutti gli shares**

Un amministratore richiede la lista di tutti i titoli azionari. Il server controlla la cache o esegue una query sulla tabella shares per restituire i dati di tutti i titoli.
![op8](https://github.com/alestrange01/DSBD_HW/blob/main/img/op8.png)

**Richiedi tutti i ticker managements**

Un amministratore richiede i dati di gestione dei ticker. Il server verifica la cache o esegue una query sulla tabella ticker_management per restituire i dati relativi ai ticker.
![op9](https://github.com/alestrange01/DSBD_HW/blob/main/img/op9.png)

**Data collector**

Il DataCollector è un microservizio responsabile della raccolta e dell'aggiornamento dei dati relativi ai titoli azionari.

- Loop continuo: Il DataCollector esegue periodicamente un ciclo per raccogliere i dati sui titoli azionari.
- Selezione ticker attivi: Interroga la tabella ticker_management per recuperare i ticker con contatore diverso da zero, che rappresentano i ticker attivamente monitorati dagli utenti.
- Chiamate al Circuit Breaker: Per ogni ticker, utilizza il Circuit Breaker per effettuare richieste a Yahoo Finance. Il Circuit Breaker gestisce guasti e fallback in caso di errori temporanei.
- Recupero e inserimento dati: Dopo aver recuperato il valore del titolo, il servizio inserisce un nuovo record nella tabella shares con il valore recuperato.
  ![data_collector](https://github.com/alestrange01/DSBD_HW/blob/main/img/DataCollector.png)

**Data cleaner**

Il DataCleaner è un microservizio che opera autonomamente per garantire la pulizia dei dati non più rilevanti nel sistema, migliorando l'efficienza e l'utilizzo dello spazio nel database.

- Loop continuo: Il DataCleaner esegue periodicamente un ciclo per effettuare operazioni di pulizia.
- Eliminazione dati obsoleti: Vengono rimossi i record dalla tabella shares con un timestamp più vecchio di 14 giorni, assicurandosi che solo dati recenti siano mantenuti.
- Verifica e rimozione ticker inutilizzati: Seleziona i ticker dalla tabella ticker_management con contatore a zero (indicando che non sono associati ad alcun utente attivo) e ne rimuove i record.
  ![data_cleaner](https://github.com/alestrange01/DSBD_HW/blob/main/img/DataCleaner.png)

**Alert system**

L'AlertSystem è un microservizio che opera da producer per il topic `to-notifier` e da consumer per il topic `to-alert-system`, il suo ruolo è quello di valutare al termine del lavoro del `data_collector` se è stata ecceduta una soglia, minima o massima, per ogni utente ed in caso affemativo andare ad inviare un messaggio sul topic `to-notifier`.
![alert system](https://github.com/alestrange01/DSBD_HW/blob/main/img/AlertSystem.png)

**Alert notification system**

L'AlertNotificationSystem è un microservizio che opera da consumer del topic `to-notifier`, il suo ruolo è quello di inviare una mail, sfruttando il package python `email` ed il template engine `jinja` per poter inviare email con template html oltre che text.
![alert notification system](https://github.com/alestrange01/DSBD_HW/blob/main/img/AlertNotificationSystem.png)

## **Schema del database**

1. Tabella **users**:  Memorizza le informazioni dell'utente, come l'e-mail e il ticker azionario associato.

- Colonne: `id`, `email`, `password`, `ticker`, `hig_value`, `low_value` .

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
- **Minikube**
- **Kubectl**

### **Passi**

1. **Clonare il repository**

```bash
 git clone https://github.com/alestrange01/DSBD_HW.git
 cd root/project
```

2. **Spostarsi all'interno della cartella "manifests"**
   Eseguire il seguente comando per spostarsi all'interno della cartella manifests:

```bash
 cd manifests
```

3. **Avviare minikube**
   Avviare minikube con il seguente comando:

```bash
 minikube start
```
4. **Creare i secrets all'interno di minikube**
   Eseguire il seguente comando per creare i secrets necessari all'invio delle email:

```bash
 kubectl create secret generic email-credentials   --from-literal=EMAIL_SENDER_USER=dsbd.romeo.strano@gmail.com   --from-literal=EMAIL_SENDER_PASSWORD='vekp tjaq tnsa iqbf'
```

5. **Avvio dell'applicativo**
   Eseguire il seguente comando per avviare l'applicativo:

```bash
  kubectl apply -f .
```

6. **Esposizione del server**
   Eseguire il seguente comando per esporre una porta del server all'esterno del cluster:

```bash
  minikube service server-service --url
```
  Copiare l'output del comando all'interno della variabile "target" del file /server/app/client.py

7. **Eseguire il client**
   Navigare nella directory del server ed eseguire lo script del client:

```bash
 cd ../server/
 python client_main.py
```

---

## **Riassunto dell'architettura**

Il sistema comprende:

- **Server**: Gestisce le interazioni con gli utenti e le operazioni del database.
- **Data Collector**: Recupera periodicamente i dati sugli shares.
- **Data Cleaner**: Ottimizza il database rimuovendo le informazioni obsolete.
- **Alert System**: Valuta al termine del lavoro del data collector se qualche soglia è stata superata.
- **Alert Notification System**: Si occupa di inviare le notifiche via email agli utenti.
- **Database**: Istanza PostgreSQL per la persistenza dei dati.

Tutti i microservizi sono orchestrati utilizzando **k8s** e la comunicazione tra client e server avviene tramite **gRPC**.
