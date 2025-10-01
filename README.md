# Rapporto di Progetto Sintetico: Monitoraggio Rete con MQTT

## 1. Introduzione

Il progetto sviluppa un'applicazione Python per il monitoraggio in tempo reale di host (ICMP/TCP).  
I risultati vengono trasmessi asincronamente tramite MQTT (Message Queuing Telemetry Transport).

---

## 2. Descrizione del Problema

L'obiettivo è creare un sistema che:

- Controlli host e porte definite in un file JSON.
- Esegua verifiche ping ICMP e stato porte TCP.
- Invii i dati su broker MQTT con topic standard (`<cognome>/<host>/...`).
- Utilizzi un Client Subscriber separato per ricevere e notificare le anomalie (`unreachable`).

---

## 3. Analisi del Problema

È richiesta un'architettura **modulare e concorrente**.  
L'uso di **thread** e **code** (`input_queue`, `output_queue`) in Python è fondamentale per garantire l'efficienza e separare i compiti di controllo dalla pubblicazione.

---

## 4. Requisiti – Specifiche di Progetto

### Requisiti Funzionali

| Requisito          | Descrizione                                       |
|--------------------|---------------------------------------------------|
| Ping ICMP          | Verifica raggiungibilità e delay.                 |
| Controllo porte TCP| Verifica stato (aperta/chiusa).                   |
| Configurazione JSON| Caricamento parametri operativi.                  |
| Pubblicazione MQTT | Invio risultati su topic con prefisso utente.     |
| Concorrenza        | Uso di thread e code per esecuzione in parallelo. |
| Client Subscriber  | Ricezione messaggi e notifica anomalie.           |

### Requisiti Non Funzionali

- Il sistema deve essere **scalabile**.
- Implementato in **Python 3.x**.
- Utilizzo della libreria **paho-mqtt**.
- Intervallo di monitoraggio **configurabile**.

---

## 5. Soluzione Proposta

Il sistema si basa su **thread comunicanti**:

- **Thread Principale** (scheduling)
- **Agenti** (controlli)
- **Publisher** (invio MQTT)
- **Subscriber** (notifica allarmi)

La comunicazione interna avviene tramite **Coda Output**.

---

## 6. Architettura della Soluzione

### Schema a Blocchi del Flusso Dati


Schema a Blocchi del Flusso Dati
[config.json]
↓
[Thread Principale (main)]
↓
[Coda Input] ←── [Thread Agenti (N)] ──→ [Coda Output]
↓
[Publisher MQTT] ──→ [Broker MQTT]
↓
[Subscriber MQTT]

## 7. Progettazione dei Componenti
Classe Host (host.py): Struttura dati per lo stato (status, delay, porte).

Classe Agent (agent.py): Thread che esegue ping/TCP e aggiorna lo stato Host.

Publisher (publisher.py): Thread che legge dalla Coda Output e pubblica su MQTT.

Subscriber (subscriber.py): Client che si iscrive ai topic e notifica gli errori.

Topic MQTT: Struttura chiave: Verniti/server1/status, Verniti/server1/ports/22/state.

## 8. Conclusioni e Note Finali
Il sistema è un monitoraggio efficiente e scalabile, basato sulla concorrenza Python e sulla notifica rapida via MQTT.

Estensioni future: Notifiche avanzate (Telegram) e persistenza dei dati.

## 9. Allegati: Codice Sorgente

[host.py](host.py)
[agent.py](agent.py)
[main.py](main.py)
[publisher.py](publisher.py)
[subscriber.py](subscriber.py)
[config.json](config.json)