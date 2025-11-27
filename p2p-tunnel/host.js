const Peer = require('simple-peer');
const wrtc = require('wrtc');
const http = require('http');
const { Signaling } = require('./utils');

// Configuration
const LOCAL_APP_PORT = 3000;
const SESSION_ID = process.env.SESSION_ID || 'my-secret-tunnel';

console.log(`[Host] Starting Tunnel Host for Session: ${SESSION_ID}`);
console.log(`[Host] Forwarding to localhost:${LOCAL_APP_PORT}`);

let peer = null;
let signaling = null;

function start() {
    signaling = new Signaling(SESSION_ID, 'host', (data) => {
        if (peer) peer.signal(data);
    });

    peer = new Peer({ initiator: true, wrtc: wrtc });

    peer.on('signal', (data) => {
        signaling.send(data);
    });

    peer.on('connect', () => {
        console.log('[Host] Peer connected! Tunnel is ready.');
    });

    peer.on('data', (data) => {
        try {
            const msg = JSON.parse(data.toString());
            if (msg.type === 'request') {
                handleRequest(msg);
            }
        } catch (e) {
            console.error('[Host] Invalid data received', e);
        }
    });

    peer.on('close', () => {
        console.log('[Host] Peer disconnected. Restarting...');
        restart();
    });

    peer.on('error', (err) => {
        console.error('[Host] Peer error:', err);
        restart(); // Simple restart strategy
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

function handleRequest(reqMsg) {
    const { id, method, url, headers, body } = reqMsg;
    console.log(`[Host] Forwarding ${method} ${url}`);

    // Filter headers (host header causes issues)
    const fwdHeaders = { ...headers };
    delete fwdHeaders['host'];
    delete fwdHeaders['connection'];

    const options = {
        hostname: 'localhost',
        port: LOCAL_APP_PORT,
        path: url,
        method: method,
        headers: fwdHeaders,
    };

    const req = http.request(options, (res) => {
        // Send Response Start
        sendJson({
            type: 'response-start',
            reqId: id,
            statusCode: res.statusCode,
            headers: res.headers
        });

        // Stream data chunks
        res.on('data', (chunk) => {
            sendJson({
                type: 'response-chunk',
                reqId: id,
                data: chunk.toString('base64')
            });
        });

        res.on('end', () => {
            sendJson({
                type: 'response-end',
                reqId: id
            });
            console.log(`[Host] Completed ${method} ${url} [${res.statusCode}]`);
        });
    });

    req.on('error', (e) => {
        console.error(`[Host] Request failed: ${e.message}`);
        sendJson({
            type: 'response-error',
            reqId: id,
            error: e.message
        });
    });

    if (body) {
        req.write(Buffer.from(body, 'base64'));
    }
    req.end();
}

function sendJson(obj) {
    if (peer && peer.connected) {
        try {
            peer.send(JSON.stringify(obj));
        } catch (e) {
            console.error('[Host] Failed to send data:', e);
        }
    }
}

start();
