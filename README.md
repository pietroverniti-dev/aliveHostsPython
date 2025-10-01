# Monitoraggio Rete con MQTT

## Introduzione

Monitorare i nodi di rete è fondamentale in qualsiasi infrastruttura IT. Questo progetto prevede un'applicazione Python che controlla regolarmente lo stato di diversi host (tramite ping e porte TCP) e invia i risultati via MQTT. Un client riceve questi dati e segnala eventuali problemi.

---

## Descrizione del Problema

L’obiettivo è creare un sistema in Python che:
- Controlli una lista di host (IP o nome),
- Verifichi la connessione con ping ICMP,
- Controlli se alcune porte TCP sono aperte o chiuse,
- Inviati i risultati su un broker MQTT con topic organizzati,
- Usi un client MQTT per ricevere aggiornamenti e notificare problemi.

Le impostazioni (IP, porte, ecc.) vengono lette da un file JSON.

---

## Analisi del Problema

Il sistema deve:
- Gestire più controlli contemporaneamente,
- Separare bene le funzioni: controllo, invio, ricezione e notifica,
- Essere facile da espandere.

Le difficoltà principali sono:
- Gestire correttamente thread e code,
- Usare bene i topic MQTT,
- Eseguire i controlli a intervalli regolari.

---

## Requisiti – Specifiche di Progetto

### Requisiti Funzionali

| Requisito                    | Descrizione                                |
|-----------------------------|--------------------------------------------|
| Ping ICMP                   | Verifica se l’host è raggiungibile         |
| Controllo porte TCP         | Verifica lo stato delle porte              |
| Configurazione JSON         | Legge host, porte, intervalli, ecc.        |
| Pubblicazione MQTT          | Su topic tipo `<cognome>/<host>/...`       |
| Concorrenza                 | Uso di thread e code                       |
| Client MQTT subscriber      | Riceve e segnala problemi                  |

### Requisiti Non Funzionali

- Codice strutturato e modulare
- Librerie standard + `paho-mqtt`
- Supporto per decine di host
- Intervallo configurabile (es. 2 minuti)
- Output in console e log

---

## Soluzione Proposta

La soluzione è composta da:

1. **Controllore Principale**: Legge la configurazione e avvia i thread.
2. **Agenti (Agent)**: Fanno ping e controllano porte.
3. **Publisher MQTT**: Invia i risultati.
4. **Subscriber**: Riceve i dati e avvisa in caso di problemi.

La comunicazione avviene tramite due code: `input_queue` e `output_queue`.

---

## Architettura della Soluzione

### Schema a Blocchi

[ config.json ]
↓
[ Thread principale ]
↓
[ Coda Input ] → [ Thread Agenti ] → [ Coda Output ] → [ Publisher MQTT ]
↓
[ Broker MQTT ]
↓
[ Subscriber MQTT ]
↓
[ Console / Log ]


---

## Progettazione dei Componenti

### Classe `Host`

Contiene:
- Nome, IP, porte
- Stato (ping, porte)
- Ultimo ping e data

### Classe `Agent`

Thread che:
- Esegue ping
- Controlla le porte
- Aggiorna lo stato dell'host
- Invia l’host aggiornato in output

### Publisher

Thread che:
- Legge dalla coda di output
- Pubblica su topic MQTT:
  - `<cognome>/<host>/status`
  - `<cognome>/<host>/delay`
  - `<cognome>/<host>/last_seen`
  - `<cognome>/<host>/ports/<porta>/state`

### Thread Principale

- Legge la configurazione
- Crea gli oggetti `Host`
- Avvia gli agenti e il publisher
- Inserisce gli host nella coda input a intervalli

### Subscriber

Client MQTT che:
- Si iscrive ai topic `<cognome>/#`
- Tiene traccia dello stato degli host
- Notifica se un host non risponde

---

## Esempi di Topic MQTT

| Topic                              | Esempio Payload            |
|------------------------------------|-----------------------------|
| `Verniti/server1/status`             | `reachable`                 |
| `Verniti/server1/delay`              | `0.042`                     |
| `Verniti/server1/last_seen`          | `2025-09-30T16:12:10Z`      |
| `Verniti/server1/ports/22/state`     | `open`                      |

---

## Diagramma di Flusso – Thread Agente

┌─────────────────────┐
│ Leggi host da input │
└────────┬────────────┘
↓
┌─────────────────────┐
│ Ping (ICMP) │
└────────┬────────────┘
↓
┌─────────────────────┐
│ Controllo porte TCP │
└────────┬────────────┘
↓
┌─────────────────────┐
│ Aggiorna oggetto │
│ Host con risultati │
└────────┬────────────┘
↓
┌─────────────────────┐
│ Inserisci in output │
│ queue │
└─────────────────────┘


---

## Conclusioni e Note Finali

L’applicazione permette di monitorare host di rete, inviare i dati via MQTT e segnalare anomalie. La struttura modulare con thread e code la rende efficiente e scalabile.

Possibili estensioni:
- Notifiche Telegram o Email
- Salvataggio su file/database
- Interfaccia web
- Supporto a protocolli come SNMP

---

### Allegati – Codice Sorgente

- `host.py`: classe per rappresentare un host
- `agent.py`: thread per controlli di rete
- `main.py`: gestione generale del sistema
- `publisher.py`: invia i risultati via MQTT
- `subscriber.py`: riceve i dati e segnala problemi
- `config.json`: configurazione host, porte, ecc.

---

### Istruzioni Finali

- Salva questo documento come `CognomeAliveHosts.md`.
- Per convertirlo in PDF puoi usare:
  - [Dillinger.io](https://dillinger.io/)
  - [Typora](https://typora.io/)
  - Oppure il comando Pandoc:

```bash
pandoc CognomeAliveHosts.md -o CognomeAliveHosts.pdf
