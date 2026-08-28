var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// src/index.js
var CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS"
};
var ALPHA = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
function makeCode() {
  let s = "";
  for (let i = 0; i < 4; i++) s += ALPHA[Math.floor(Math.random() * ALPHA.length)];
  return s;
}
__name(makeCode, "makeCode");
var src_default = {
  async fetch(req, env) {
    const url = new URL(req.url);
    if (req.method === "OPTIONS") return new Response(null, { headers: CORS });
    if (url.pathname === "/new") {
      return new Response(JSON.stringify({ code: makeCode() }), {
        headers: { "content-type": "application/json", ...CORS }
      });
    }
    const m = url.pathname.match(/^\/ws\/([A-Za-z0-9]{4,8})$/);
    if (m) {
      if (req.headers.get("Upgrade") !== "websocket")
        return new Response("expected websocket", { status: 426, headers: CORS });
      const id = env.ROOMS.idFromName(m[1].toUpperCase());
      return env.ROOMS.get(id).fetch(req);
    }
    return new Response("dont-drop-him online relay OK", { headers: CORS });
  }
};
var RoomDO = class {
  static {
    __name(this, "RoomDO");
  }
  constructor(ctx) {
    this.ctx = ctx;
  }
  async fetch() {
    const sockets = this.ctx.getWebSockets();
    if (sockets.length >= 2) return new Response("room full", { status: 409, headers: CORS });
    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);
    const hasHost = sockets.some((w) => (w.deserializeAttachment() || {}).host);
    this.ctx.acceptWebSocket(server);
    server.serializeAttachment({
      id: sockets.length === 0 ? "A" : "B",
      host: !hasHost,
      role: null
    });
    this.roster();
    return new Response(null, { status: 101, webSocket: client });
  }
  webSocketMessage(ws, msg) {
    if (typeof msg !== "string" || msg.length > 65536) return;
    let d;
    try {
      d = JSON.parse(msg);
    } catch (_) {
      return;
    }
    const a = ws.deserializeAttachment() || {};
    if (d.t === "role") {
      const want = d.role === "front" || d.role === "back" ? d.role : null;
      const taken = want && this.ctx.getWebSockets().some(
        (w) => w !== ws && (w.deserializeAttachment() || {}).role === want
      );
      if (!taken) {
        a.role = want;
        ws.serializeAttachment(a);
      }
      this.roster();
    } else if (d.t === "start") {
      if (a.host) this.bcast({ t: "start", level: d.level || 1, mi: d.mi | 0 });
    } else if (d.t === "relay") {
      for (const w of this.ctx.getWebSockets())
        if (w !== ws) {
          try {
            w.send(msg);
          } catch (_) {
          }
        }
    } else if (d.t === "ping") {
      try {
        ws.send('{"t":"pong"}');
      } catch (_) {
      }
    }
  }
  webSocketClose(ws) {
    this.drop(ws);
  }
  webSocketError(ws) {
    this.drop(ws);
  }
  drop(ws) {
    try {
      ws.close();
    } catch (_) {
    }
    const rest = this.ctx.getWebSockets().filter((w) => w !== ws);
    if (rest.length === 1) {
      const a = rest[0].deserializeAttachment() || {};
      if (!a.host) {
        a.host = true;
        rest[0].serializeAttachment(a);
      }
      try {
        rest[0].send('{"t":"peer_left"}');
      } catch (_) {
      }
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
        w.send(JSON.stringify({ t: "roster", you: a.id, host: !!a.host, players }));
      } catch (_) {
      }
    }
  }
  bcast(o) {
    const s = JSON.stringify(o);
    for (const w of this.ctx.getWebSockets()) {
      try {
        w.send(s);
      } catch (_) {
      }
    }
  }
};

// ../../../../AppData/Local/npm-cache/_npx/d77349f55c2be1c0/node_modules/wrangler/templates/middleware/middleware-ensure-req-body-drained.ts
var drainBody = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } finally {
    try {
      if (request.body !== null && !request.bodyUsed) {
        const reader = request.body.getReader();
        while (!(await reader.read()).done) {
        }
      }
    } catch (e) {
      console.error("Failed to drain the unused request body.", e);
    }
  }
}, "drainBody");
var middleware_ensure_req_body_drained_default = drainBody;

// ../../../../AppData/Local/npm-cache/_npx/d77349f55c2be1c0/node_modules/wrangler/templates/middleware/middleware-miniflare3-json-error.ts
function reduceError(e) {
  return {
    name: e?.name,
    message: e?.message ?? String(e),
    stack: e?.stack,
    cause: e?.cause === void 0 ? void 0 : reduceError(e.cause)
  };
}
__name(reduceError, "reduceError");
var jsonError = /* @__PURE__ */ __name(async (request, env, _ctx, middlewareCtx) => {
  try {
    return await middlewareCtx.next(request, env);
  } catch (e) {
    const error = reduceError(e);
    const body = JSON.stringify(error);
    const headers = {
      "Content-Type": "application/json",
      "MF-Experimental-Error-Stack": "true"
    };
    const encoded = encodeURIComponent(body);
    if (encoded.length <= 8192) {
      headers["MF-Experimental-Error-Stack-Payload"] = encoded;
    }
    return new Response(body, { status: 500, headers });
  }
}, "jsonError");
var middleware_miniflare3_json_error_default = jsonError;

// .wrangler/tmp/bundle-PSiaJ7/middleware-insertion-facade.js
var __INTERNAL_WRANGLER_MIDDLEWARE__ = [
  middleware_ensure_req_body_drained_default,
  middleware_miniflare3_json_error_default
];
var middleware_insertion_facade_default = src_default;

// ../../../../AppData/Local/npm-cache/_npx/d77349f55c2be1c0/node_modules/wrangler/templates/middleware/common.ts
var __facade_middleware__ = [];
function __facade_register__(...args) {
  __facade_middleware__.push(...args.flat());
}
__name(__facade_register__, "__facade_register__");
function __facade_invokeChain__(request, env, ctx, dispatch, middlewareChain) {
  const [head, ...tail] = middlewareChain;
  const middlewareCtx = {
    dispatch,
    next(newRequest, newEnv) {
      return __facade_invokeChain__(newRequest, newEnv, ctx, dispatch, tail);
    }
  };
  return head(request, env, ctx, middlewareCtx);
}
__name(__facade_invokeChain__, "__facade_invokeChain__");
function __facade_invoke__(request, env, ctx, dispatch, finalMiddleware) {
  return __facade_invokeChain__(request, env, ctx, dispatch, [
    ...__facade_middleware__,
    finalMiddleware
  ]);
}
__name(__facade_invoke__, "__facade_invoke__");

// .wrangler/tmp/bundle-PSiaJ7/middleware-loader.entry.ts
var __Facade_ScheduledController__ = class ___Facade_ScheduledController__ {
  constructor(scheduledTime, cron, noRetry) {
    this.scheduledTime = scheduledTime;
    this.cron = cron;
    this.#noRetry = noRetry;
  }
  scheduledTime;
  cron;
  static {
    __name(this, "__Facade_ScheduledController__");
  }
  #noRetry;
  noRetry() {
    if (!(this instanceof ___Facade_ScheduledController__)) {
      throw new TypeError("Illegal invocation");
    }
    this.#noRetry();
  }
};
function wrapExportedHandler(worker) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return worker;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  const fetchDispatcher = /* @__PURE__ */ __name(function(request, env, ctx) {
    if (worker.fetch === void 0) {
      throw new Error("Handler does not export a fetch() function.");
    }
    return worker.fetch(request, env, ctx);
  }, "fetchDispatcher");
  return {
    ...worker,
    fetch(request, env, ctx) {
      const dispatcher = /* @__PURE__ */ __name(function(type, init) {
        if (type === "scheduled" && worker.scheduled !== void 0) {
          const controller = new __Facade_ScheduledController__(
            Date.now(),
            init.cron ?? "",
            () => {
            }
          );
          return worker.scheduled(controller, env, ctx);
        }
      }, "dispatcher");
      return __facade_invoke__(request, env, ctx, dispatcher, fetchDispatcher);
    }
  };
}
__name(wrapExportedHandler, "wrapExportedHandler");
function wrapWorkerEntrypoint(klass) {
  if (__INTERNAL_WRANGLER_MIDDLEWARE__ === void 0 || __INTERNAL_WRANGLER_MIDDLEWARE__.length === 0) {
    return klass;
  }
  for (const middleware of __INTERNAL_WRANGLER_MIDDLEWARE__) {
    __facade_register__(middleware);
  }
  return class extends klass {
    #fetchDispatcher = /* @__PURE__ */ __name((request, env, ctx) => {
      this.env = env;
      this.ctx = ctx;
      if (super.fetch === void 0) {
        throw new Error("Entrypoint class does not define a fetch() function.");
      }
      return super.fetch(request);
    }, "#fetchDispatcher");
    #dispatcher = /* @__PURE__ */ __name((type, init) => {
      if (type === "scheduled" && super.scheduled !== void 0) {
        const controller = new __Facade_ScheduledController__(
          Date.now(),
          init.cron ?? "",
          () => {
          }
        );
        return super.scheduled(controller);
      }
    }, "#dispatcher");
    fetch(request) {
      return __facade_invoke__(
        request,
        this.env,
        this.ctx,
        this.#dispatcher,
        this.#fetchDispatcher
      );
    }
  };
}
__name(wrapWorkerEntrypoint, "wrapWorkerEntrypoint");
var WRAPPED_ENTRY;
if (typeof middleware_insertion_facade_default === "object") {
  WRAPPED_ENTRY = wrapExportedHandler(middleware_insertion_facade_default);
} else if (typeof middleware_insertion_facade_default === "function") {
  WRAPPED_ENTRY = wrapWorkerEntrypoint(middleware_insertion_facade_default);
}
var middleware_loader_entry_default = WRAPPED_ENTRY;
export {
  RoomDO,
  __INTERNAL_WRANGLER_MIDDLEWARE__,
  middleware_loader_entry_default as default
};
//# sourceMappingURL=index.js.map
