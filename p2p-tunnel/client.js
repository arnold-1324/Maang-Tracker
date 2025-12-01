const Peer = require('simple-peer');
const wrtc = require('wrtc');
const http = require('http');
const crypto = require('crypto');
const { Signaling } = require('./utils');

// Configuration
const LOCAL_PORT = 8080;
const SESSION_ID = process.env.SESSION_ID || 'my-secret-tunnel';

console.log(`[Client] Starting Tunnel Client for Session: ${SESSION_ID}`);
console.log(`[Client] Open your browser at http://localhost:${LOCAL_PORT}`);

let peer = null;
let signaling = null;
const pendingRequests = new Map(); // ID -> res object

function start() {
    signaling = new Signaling(SESSION_ID, 'client', (data) => {
        if (peer) peer.signal(data);
    });

    peer = new Peer({ initiator: false, wrtc: wrtc });

    peer.on('signal', (data) => {
        signaling.send(data);
    });

    peer.on('connect', () => {
        console.log('[Client] Connected to Host! Ready to browse.');
    });

    peer.on('data', (data) => {
        try {
            const msg = JSON.parse(data.toString());
            handleMessage(msg);
        } catch (e) {
            console.error('[Client] Invalid data received', e);
        }
    });

    peer.on('close', () => {
        console.log('[Client] Disconnected. Reconnecting...');
        restart();
    });

    peer.on('error', (err) => {
        console.error('[Client] Peer error:', err);
        restart();
    });
}

function restart() {
    if (peer) {
        peer.destroy();
        peer = null;
    }
    if (signaling) {
        signaling.close();
        signaling = null;
    }
    setTimeout(start, 2000);
}

function handleMessage(msg) {
    const res = pendingRequests.get(msg.reqId);
    if (!res) return;

    switch (msg.type) {
        case 'response-start':
            res.writeHead(msg.statusCode, msg.headers);
            break;
        case 'response-chunk':
            res.write(Buffer.from(msg.data, 'base64'));
            break;
        case 'response-end':
            res.end();
            pendingRequests.delete(msg.reqId);
            break;
        case 'response-error':
            res.statusCode = 500;
            res.end(`Tunnel Error: ${msg.error}`);
            pendingRequests.delete(msg.reqId);
            break;
    }
}

// Local HTTP Server
const server = http.createServer((req, res) => {
    if (!peer || !peer.connected) {
        res.statusCode = 503;
        res.end('Tunnel not connected yet. Please wait...');
        return;
    }

    const reqId = crypto.randomBytes(8).toString('hex');
    pendingRequests.set(reqId, res);

    // Buffer request body
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
        const body = Buffer.concat(chunks);

        const reqMsg = {
            type: 'request',
            id: reqId,
            method: req.method,
            url: req.url,
            headers: req.headers,
            body: body.length > 0 ? body.toString('base64') : null
        };

        try {
            peer.send(JSON.stringify(reqMsg));
        } catch (e) {
            console.error('[Client] Failed to send request', e);
            res.statusCode = 500;
            res.end('Failed to send request through tunnel');
            pendingRequests.delete(reqId);
        }
    });
});

server.listen(LOCAL_PORT, () => {
    console.log(`[Client] Server listening on port ${LOCAL_PORT}`);
    start();
});
