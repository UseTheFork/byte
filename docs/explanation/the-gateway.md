# The Gateway

**Category**: Explanation

Byte's gateway is a WebSocket JSON-RPC 2.0 bridge that exposes an authenticated RPC interface for external clients. Editors, IDE plugins, and custom tooling connect to the gateway and invoke methods on Byte remotely—adding files to context, configuring models, receiving streaming responses in real time. The gateway handles everything: auth, session lifecycle, request dispatch, and pushing notifications back to clients.

## What Is the Gateway?

The gateway is not a REST API or a CLI wrapper. It's a persistent, stateful WebSocket server that maintains a single authenticated session per client connection. When a client connects, it must authenticate with a token. Once authenticated, it can issue RPC requests and receive streaming notifications.

The design is deliberate: a single session per connection means client-side state stays in sync with Byte's internal state. There's no polling, no request batching ambiguity, no stateless HTTP headaches. Messages flow bidirectionally in real time.

## How It Works

### Auth Handshake

The first message on any new WebSocket connection **must** be an `auth` request with a token parameter:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "auth",
  "params": { "token": "..." }
}
```

The token is generated when the gateway server starts and written to disk at `.byte/cache/gateway.token` with permissions `0o600` (readable only by the user). External clients read this file to authenticate. If the token is invalid, the connection closes. If it's valid, the server responds with an OK and the session begins.

This token-based handshake is simple and secure enough for local development workflows. For distributed scenarios, you'd implement a different auth mechanism.

### Session Lifecycle

Once authenticated, a `SessionService` instance is created for that connection. The session processes inbound RPC requests, routes them to handlers, and sends back `RpcResponse` objects (success or error). It also receives application events from other parts of Byte and pushes `RpcNotification` objects to the client asynchronously.

The session runs until the client disconnects or an error occurs. One session per connection; state is tied to that session.

### Streaming Notifications

Responses are synchronous — each RPC request gets a single `RpcResponse` back. But notifications are asynchronous and flow only from server to client. When Byte has updates to push (e.g., chunks of a streamed response, a tool execution result, status changes), it sends `RpcNotification` objects to the client. Your client receives these interleaved with response completions, enabling real-time bidirectional communication. See [The Protocol](#the-protocol) section below for the notification format.

## The Protocol

The gateway speaks JSON-RPC 2.0. All messages are JSON objects with a `jsonrpc` field set to `"2.0"`.

### RpcRequest

Inbound requests from the client. Required fields: `jsonrpc`, `id`, `method`. Optional field: `params`.

```json
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "method": "add_file",
  "params": { "file_path": "src/main.py" }
}
```

### RpcResponse

The final result (success or error) for a request id. Contains either `result` (success) or `error` (failure), never both.

```json
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "result": { "ok": true, "file_path": "src/main.py" }
}
```

### RpcNotification

Outbound streaming events with no request id. Sent asynchronously.

```json
{
  "jsonrpc": "2.0",
  "method": "stream/response",
  "params": { "content": "The answer is...", "done": false }
}
```

### RpcError

Embedded in error responses. Contains `code` (integer), `message` (string), and optional `data`.

```json
{
  "code": -32000,
  "message": "Unauthorized",
  "data": null
}
```

Standard JSON-RPC error codes are used: `-32700` (Parse Error), `-32600` (Invalid Request), `-32601` (Method Not Found), and custom codes like `-32000` (Unauthorized) and `-32001` (Internal Error).

## Configuration

Enable and configure the gateway in `.byte/config.jsonc`:

```jsonc
{
  "gateway": {
    "enable": true,
    "host": "127.0.0.1",
    "port": 0,
  },
}
```

- `enable` — Whether the gateway server starts at boot. Defaults to `false`.
- `host` — The hostname to bind to. Defaults to `"127.0.0.1"` (localhost only).
- `port` — The port to bind to. Defaults to `0` (let the OS choose an available port). If you set a fixed port, you must manage port conflicts yourself.

When the gateway starts, it writes a discovery file to `.byte/cache/gateway.json` containing the actual host, port, and token file path. External clients read this file to know where to connect.

## Security

**Token-based authentication** is the first line of defense. The token is generated using `secrets.token_urlsafe(32)` (cryptographically strong) and written to disk with `0o600` permissions (readable only by the user). External clients must read this file to authenticate.

**Discovery file** (`.byte/cache/gateway.json`) tells clients where the server is running and where to find the token file. It's written every time the server starts.

**Localhost by default** — The gateway binds to `127.0.0.1` by default, rejecting remote connections. If you expose the gateway to a network, the token becomes your only protection. For distributed development, you'd layer additional auth (mutual TLS, API keys, OAuth) on top.

## Available Requests

The gateway exposes a set of RPC methods that external clients can invoke. Each method is defined as a dataclass on the `Requests` namespace in `src/byte/gateway/requests.py`. The full list and detailed documentation is available on the [Gateway Requests](gateway-requests.md) subpage.
