const mqtt = require('mqtt');

// --- Signaling Helper ---
class Signaling {
    constructor(sessionId, role, onSignal) {
        this.sessionId = sessionId;
        this.role = role; // 'host' or 'client'
        this.peerRole = role === 'host' ? 'client' : 'host';
        this.onSignal = onSignal;

        // Use a public broker. 
        // Alternatives: 'mqtt://broker.hivemq.com', 'mqtt://test.mosquitto.org'
        this.client = mqtt.connect('mqtt://test.mosquitto.org');

        this.topicIncoming = `maang-tunnel/${sessionId}/${this.role}`;
        this.topicOutgoing = `maang-tunnel/${sessionId}/${this.peerRole}`;

        this.client.on('connect', () => {
            console.log(`[Signaling] Connected to broker. Session: ${sessionId}`);
            this.client.subscribe(this.topicIncoming, (err) => {
                if (!err) {
                    console.log(`[Signaling] Waiting for peer at ${this.topicIncoming}`);
                }
            });
        });

        this.client.on('message', (topic, message) => {
            if (topic === this.topicIncoming) {
                try {
                    const data = JSON.parse(message.toString());
                    this.onSignal(data);
                } catch (e) {
                    console.error('[Signaling] Failed to parse message');
                }
            }
        });
    }

    send(signalData) {
        this.client.publish(this.topicOutgoing, JSON.stringify(signalData));
    }

    close() {
        this.client.end();
    }
}

// --- Chunking Helpers ---
const CHUNK_SIZE = 16 * 1024; // 16KB safe limit for DataChannel

function chunkBuffer(buffer, msgId) {
    const chunks = [];
    const total = Math.ceil(buffer.length / CHUNK_SIZE);

    for (let i = 0; i < total; i++) {
        const start = i * CHUNK_SIZE;
        const end = Math.min(start + CHUNK_SIZE, buffer.length);
        const chunkData = buffer.slice(start, end);

        // Header: MsgID (4 bytes) + Index (4 bytes) + Total (4 bytes) + Data
        // Simple JSON wrapper is easier for Node.js prototyping than raw binary packing
        // unless performance is critical. Let's use JSON for reliability/debugging first.

        chunks.push(JSON.stringify({
            type: 'chunk',
            id: msgId,
            idx: i,
            total: total,
            data: chunkData.toString('base64')
        }));
    }
    return chunks;
}

module.exports = { Signaling, chunkBuffer };
