/* 부장님이 잠드셨다 — 온라인 협동 중계 서버
   방 하나 = Durable Object 하나(코드로 명명). 최대 2인, 호스트 권위 방식의 릴레이만 담당. */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
};

const ALPHA = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'; // 헷갈리는 I/L/O/0/1 제외
function makeCode() {
  let s = '';
  for (let i = 0; i < 4; i++) s += ALPHA[Math.floor(Math.random() * ALPHA.length)];
  return s;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === 'OPTIONS') return new Response(null, { headers: CORS });
    if (url.pathname === '/new') {
      return new Response(JSON.stringify({ code: makeCode() }), {
        headers: { 'content-type': 'application/json', ...CORS },
      });
    }
    const m = url.pathname.match(/^\/ws\/([A-Za-z0-9]{4,8})$/);
    if (m) {
      if (req.headers.get('Upgrade') !== 'websocket')
        return new Response('expected websocket', { status: 426, headers: CORS });
      const id = env.ROOMS.idFromName(m[1].toUpperCase());
      return env.ROOMS.get(id).fetch(req);
    }
    return new Response('dont-drop-him online relay OK', { headers: CORS });
  },
};

export class RoomDO {
  constructor(ctx) {
    this.ctx = ctx;
  }

  async fetch() {
    const sockets = this.ctx.getWebSockets();
    if (sockets.length >= 2) return new Response('room full', { status: 409, headers: CORS });

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    const hasHost = sockets.some((w) => (w.deserializeAttachment() || {}).host);
    this.ctx.acceptWebSocket(server);
    server.serializeAttachment({
      id: sockets.length === 0 ? 'A' : 'B',
      host: !hasHost,
      role: null,
    });
    this.roster();
    return new Response(null, { status: 101, webSocket: client });
  }

  webSocketMessage(ws, msg) {
    if (typeof msg !== 'string' || msg.length > 65536) return;
    let d;
    try { d = JSON.parse(msg); } catch (_) { return; }
    const a = ws.deserializeAttachment() || {};

    if (d.t === 'role') {
      const want = d.role === 'front' || d.role === 'back' ? d.role : null;
      const taken = want && this.ctx.getWebSockets().some(
        (w) => w !== ws && (w.deserializeAttachment() || {}).role === want
      );
      if (!taken) { a.role = want; ws.serializeAttachment(a); }
      this.roster();
    } else if (d.t === 'start') {
      if (a.host) this.bcast({ t: 'start', level: d.level || 1, mi: d.mi | 0 });
    } else if (d.t === 'relay') {
      for (const w of this.ctx.getWebSockets())
        if (w !== ws) { try { w.send(msg); } catch (_) {} }
    } else if (d.t === 'ping') {
      try { ws.send('{"t":"pong"}'); } catch (_) {}
    }
  }

  webSocketClose(ws) { this.drop(ws); }
  webSocketError(ws) { this.drop(ws); }

  drop(ws) {
    try { ws.close(); } catch (_) {}
    const rest = this.ctx.getWebSockets().filter((w) => w !== ws);
    if (rest.length === 1) {
      const a = rest[0].deserializeAttachment() || {};
      if (!a.host) { a.host = true; rest[0].serializeAttachment(a); }
      try { rest[0].send('{"t":"peer_left"}'); } catch (_) {}
    }
    this.roster(ws);
  }

  roster(except) {
    const list = this.ctx.getWebSockets().filter((w) => w !== except);
    const players = list.map((w) => {
      const a = w.deserializeAttachment() || {};
      return { id: a.id, host: !!a.host, role: a.role || null };
    });
    for (const w of list) {
      const a = w.deserializeAttachment() || {};
      try {
        w.send(JSON.stringify({ t: 'roster', you: a.id, host: !!a.host, players }));
      } catch (_) {}
    }
  }

  bcast(o) {
    const s = JSON.stringify(o);
    for (const w of this.ctx.getWebSockets()) { try { w.send(s); } catch (_) {} }
  }
}
