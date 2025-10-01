# Rapporto di Progetto Sintetico: Monitoraggio Rete con MQTT

## 1. Introduzione

Il presente progetto ha come obiettivo lo sviluppo di un'applicazione in linguaggio Python per il monitoraggio in tempo reale di host di rete, mediante protocolli ICMP e TCP.  
I risultati delle verifiche vengono trasmessi asincronamente tramite protocollo MQTT (Message Queuing Telemetry Transport), garantendo efficienza e scalabilità.

---

## 2. Descrizione del Problema

L'applicazione deve implementare un sistema in grado di:

- Monitorare host e porte specificate in un file di configurazione JSON.
- Eseguire controlli di raggiungibilità tramite ping ICMP.
- Verificare lo stato delle porte TCP (aperte/chiuse).
- Pubblicare i risultati su un broker MQTT utilizzando topic standardizzati (`<cognome>/<host>/...`).
- Utilizzare un client subscriber separato per ricevere i messaggi e notificare eventuali anomalie (`unreachable`).

---

## 3. Analisi del Problema

L'architettura richiesta è **modulare** e **concorrente**, al fine di garantire prestazioni elevate e separazione dei compiti.  
L'utilizzo di **thread** e **code** (`input_queue`, `output_queue`) in Python consente una gestione efficiente dei processi di controllo e pubblicazione.

---

## 4. Requisiti – Specifiche di Progetto

### Requisiti Funzionali

| Requisito           | Descrizione                                         |
|---------------------|-----------------------------------------------------|
| Ping ICMP           | Verifica della raggiungibilità e misurazione del delay. |
| Controllo porte TCP | Verifica dello stato delle porte (aperte/chiuse).   |
| Configurazione JSON | Caricamento dei parametri operativi da file.        |
| Pubblicazione MQTT  | Invio dei risultati su topic con prefisso utente.   |
| Concorrenza         | Utilizzo di thread e code per esecuzione parallela. |
| Client Subscriber   | Ricezione dei messaggi e notifica delle anomalie.   |

### Requisiti Non Funzionali

- Il sistema deve essere **scalabile**.
- Deve essere sviluppato in **Python 3.x**.
- È richiesto l'utilizzo della libreria **paho-mqtt**.
- L'intervallo di monitoraggio deve essere **configurabile**.

---

## 5. Soluzione Proposta

L'architettura si basa su thread comunicanti, ciascuno con un ruolo specifico:

- **Thread Principale**: gestisce lo scheduling e l'invio dei task.
- **Agenti**: eseguono i controlli ICMP/TCP.
- **Publisher**: pubblica i risultati su MQTT.
- **Subscriber**: riceve i messaggi e notifica gli allarmi.

La comunicazione interna tra thread avviene tramite una **coda di output** condivisa.

---

## 6. Architettura della Soluzione

### Schema a Blocchi del Flusso Dati

```text
[config.json]
      ↓
[Thread Principale (main)]
      ↓
[Coda Input] ←── [Thread Agenti (N)] ──→ [Coda Output]
      ↓
[Publisher MQTT] ──→ [Broker MQTT]
      ↓
[Subscriber MQTT]
```

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