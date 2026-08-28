/* 부장님이 잠드셨다 — 온라인 협동 중계 서버
   RoomDO: 방 하나(최대 2인, 역할/시작/릴레이). LobbyDO: 공개 방 목록(싱글톤).
   방은 상태가 바뀔 때마다 로비에 보고하고, 클라이언트는 GET /rooms로 목록을 본다. */

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
};

const ALPHA = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
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
    if (url.pathname === '/rooms') {
      return env.LOBBY.get(env.LOBBY.idFromName('main')).fetch(req);
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
  constructor(ctx, env) {
    this.ctx = ctx;
    this.env = env;
  }

  async meta(key) {
    return this.ctx.storage.get(key);
  }

  async fetch(req) {
    const url = new URL(req.url);
    const code = (url.pathname.split('/')[2] || '').toUpperCase();
    const sockets = this.ctx.getWebSockets();
    if (sockets.length >= 2) return new Response('room full', { status: 409, headers: CORS });
    if (await this.meta('started')) return new Response('already started', { status: 409, headers: CORS });

    await this.ctx.storage.put('code', code);
    const qName = (url.searchParams.get('name') || '').slice(0, 24).trim();
    if (qName && !(await this.meta('name'))) await this.ctx.storage.put('name', qName);

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    const hasHost = sockets.some((w) => (w.deserializeAttachment() || {}).host);
    this.ctx.acceptWebSocket(server);
    server.serializeAttachment({
      id: sockets.length === 0 ? 'A' : 'B',
      host: !hasHost,
      role: null,
    });
    await this.roster();
    await this.report();
    return new Response(null, { status: 101, webSocket: client });
  }

  async webSocketMessage(ws, msg) {
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
      await this.roster();
    } else if (d.t === 'start') {
      if (a.host) {
        await this.ctx.storage.put('started', 1);
        this.bcast({ t: 'start', level: d.level || 1, mi: d.mi | 0 });
        await this.report();
      }
    } else if (d.t === 'reopen') {
      // 게임 중 상대가 이탈한 뒤, 남은 방장이 방을 다시 공개
      if (a.host) {
        await this.ctx.storage.delete('started');
        await this.roster();
        await this.report();
      }
    } else if (d.t === 'relay') {
      for (const w of this.ctx.getWebSockets())
        if (w !== ws) { try { w.send(msg); } catch (_) {} }
    } else if (d.t === 'ping') {
      try { ws.send('{"t":"pong"}'); } catch (_) {}
      await this.report(); // 하트비트: 로비 목록 신선도 유지
    }
  }

  async webSocketClose(ws) { await this.drop(ws); }
  async webSocketError(ws) { await this.drop(ws); }

  async drop(ws) {
    try { ws.close(); } catch (_) {}
    const rest = this.ctx.getWebSockets().filter((w) => w !== ws);
    if (rest.length === 1) {
      const a = rest[0].deserializeAttachment() || {};
      if (!a.host) { a.host = true; rest[0].serializeAttachment(a); }
      try { rest[0].send('{"t":"peer_left"}'); } catch (_) {}
    }
    if (rest.length === 0) {
      await this.ctx.storage.delete('started'); // 다 나가면 방 리셋
    }
    await this.roster(ws);
    await this.report(ws);
  }

  async roster(except) {
    const list = this.ctx.getWebSockets().filter((w) => w !== except);
    const name = (await this.meta('name')) || null;
    const players = list.map((w) => {
      const a = w.deserializeAttachment() || {};
      return { id: a.id, host: !!a.host, role: a.role || null };
    });
    for (const w of list) {
      const a = w.deserializeAttachment() || {};
      try {
        w.send(JSON.stringify({ t: 'roster', you: a.id, host: !!a.host, players, name }));
      } catch (_) {}
    }
  }

  async report(except) {
    const code = await this.meta('code');
    if (!code) return;
    const n = this.ctx.getWebSockets().filter((w) => w !== except).length;
    const body = JSON.stringify({
      code,
      name: (await this.meta('name')) || null,
      players: n,
      started: !!(await this.meta('started')),
    });
    try {
      await this.env.LOBBY.get(this.env.LOBBY.idFromName('main'))
        .fetch('https://lobby/report', { method: 'POST', body });
    } catch (_) {}
  }

  bcast(o) {
    const s = JSON.stringify(o);
    for (const w of this.ctx.getWebSockets()) { try { w.send(s); } catch (_) {} }
  }
}

export class LobbyDO {
  constructor(ctx) {
    this.ctx = ctx;
    this.rooms = null;
  }

  async load() {
    if (!this.rooms) this.rooms = (await this.ctx.storage.get('rooms')) || {};
  }

  async fetch(req) {
    await this.load();
    const url = new URL(req.url);

    if (req.method === 'POST' && url.pathname === '/report') {
      let d;
      try { d = await req.json(); } catch (_) { return new Response('bad', { status: 400 }); }
      if (!d.code) return new Response('bad', { status: 400 });
      if (d.players < 1 || d.started || d.players >= 2) delete this.rooms[d.code];
      else this.rooms[d.code] = { code: d.code, name: d.name || null, players: d.players, at: Date.now() };
      await this.ctx.storage.put('rooms', this.rooms);
      return new Response('ok');
    }

    // GET /rooms — 90초 이상 소식 없는 방은 목록에서 제거
    const now = Date.now();
    let dirty = false;
    for (const c in this.rooms)
      if (now - this.rooms[c].at > 90000) { delete this.rooms[c]; dirty = true; }
    if (dirty) await this.ctx.storage.put('rooms', this.rooms);
    const list = Object.values(this.rooms).sort((a, b) => b.at - a.at).slice(0, 200);
    return new Response(JSON.stringify({ rooms: list }), {
      headers: { 'content-type': 'application/json', ...CORS },
    });
  }
}
