# 12 — Real-time Specification

## Overview

Nexus AI uses Socket.IO for real-time, bidirectional communication between the frontend and API Gateway. This enables live streaming of AI responses, agent step-by-step execution visibility, and notifications.

## Architecture

```
┌──────────┐  Socket.IO   ┌──────────┐    HTTP     ┌──────────┐
│ Next.js  │◄────────────►│ NestJS   │◄───────────►│ FastAPI  │
│ Client   │   (WebSocket) │ Gateway  │             │ Backend  │
└──────────┘              └──────────┘             └──────────┘
                                │
                           ┌────▼────┐
                           │  Redis  │ (Pub/Sub for cross-instance)
                           └─────────┘
```

## Socket.IO Setup (NestJS)

```typescript
// gateway/src/realtime/realtime.gateway.ts
@WebSocketGateway({
  namespace: 'ws',
  cors: { origin: process.env.FRONTEND_URL },
})
export class RealtimeGateway
  implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer() server: Server;
  
  afterInit(server: Server) {
    this.logger.log('WebSocket Gateway initialized');
  }
  
  async handleConnection(client: Socket) {
    const token = client.handshake.auth.token;
    const user = await this.authService.validateToken(token);
    if (!user) {
      client.disconnect();
      return;
    }
    client.data.user = user;
    this.logger.log(`Client connected: ${user.sub}`);
  }
  
  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.data.user?.sub}`);
  }
  
  // Join a conversation room
  @SubscribeMessage('conversation:join')
  async handleJoinConversation(
    client: Socket,
    payload: { conversationId: string },
  ) {
    // Verify access
    await this.conversationService.verifyAccess(
      client.data.user.sub,
      payload.conversationId,
    );
    client.join(`conversation:${payload.conversationId}`);
  }
  
  // Send message in conversation
  @SubscribeMessage('conversation:message')
  async handleMessage(
    client: Socket,
    payload: { conversationId: string; content: string },
  ) {
    // Forward to AI backend
    const response = await this.aiService.sendMessage(
      payload.conversationId,
      payload.content,
      client.data.user.sub,
    );
    
    // Broadcast to room
    this.server.to(`conversation:${payload.conversationId}`).emit(
      'conversation:message',
      response,
    );
  }
}
```

## Event Catalog

### Client → Server

| Event                    | Payload                                  |
|--------------------------|------------------------------------------|
| `conversation:join`      | `{ conversationId: string }`             |
| `conversation:leave`     | `{ conversationId: string }`             |
| `conversation:message`   | `{ conversationId, content, attachments? }` |
| `conversation:typing`    | `{ conversationId: string }`             |
| `agent:run`              | `{ agentId: string, input: string }`     |
| `agent:cancel`           | `{ runId: string }`                      |

### Server → Client

| Event                    | Payload                                  |
|--------------------------|------------------------------------------|
| `conversation:message`   | `{ id, role, content, metadata }`        |
| `conversation:token`     | `{ content: string, done: boolean }`     |
| `conversation:typing`    | `{ userId: string, isTyping: boolean }`  |
| `agent:step`             | `{ runId, step, thought, action, observation }` |
| `agent:token`            | `{ runId, content: string, done: boolean }` |
| `agent:complete`         | `{ runId, output, steps, durationMs }`   |
| `agent:error`            | `{ runId, error: string }`               |
| `notification:info`      | `{ title, message, type }`               |
| `notification:error`     | `{ title, message }`                     |

## Streaming AI Responses

```typescript
// Server streams tokens as they're generated
async *streamAIResponse(conversationId: string, message: string) {
  const stream = await this.aiService.streamChat(conversationId, message);
  
  for await (const chunk of stream) {
    yield { content: chunk.token, done: false };
  }
  yield { content: '', done: true };
}

// In gateway
async handleMessage(client: Socket, payload: MessagePayload) {
  const stream = this.streamAIResponse(payload.conversationId, payload.content);
  
  for await (const chunk of stream) {
    this.server
      .to(`conversation:${payload.conversationId}`)
      .emit('conversation:token', chunk);
  }
}
```

## Agent Step Visualization

```typescript
// Agent emits each step so frontend can visualize
@SubscribeMessage('agent:run')
async handleAgentRun(client: Socket, payload: AgentRunPayload) {
  const runId = uuid();
  
  this.server.to(client.id).emit('agent:step', {
    runId,
    step: 'planning',
    thought: 'Analyzing task...',
  });
  
  try {
    const result = await this.agentService.run(
      payload.agentId,
      payload.input,
      (step) => {
        // Callback for each step
        this.server.to(client.id).emit('agent:step', {
          runId,
          ...step,
        });
      },
    );
    
    this.server.to(client.id).emit('agent:complete', {
      runId,
      output: result.output,
      steps: result.steps,
    });
  } catch (error) {
    this.server.to(client.id).emit('agent:error', {
      runId,
      error: error.message,
    });
  }
}
```

## Cross-Instance Pub/Sub (Redis Adapter)

```typescript
// For horizontal scaling, use Redis adapter
import { createAdapter } from '@socket.io/redis-adapter';

const pubClient = createRedisClient();
const subClient = pubClient.duplicate();

@WebSocketGateway({
  adapter: createAdapter(pubClient, subClient),
})
export class RealtimeGateway {}
```

## Connection Management

```typescript
// Heartbeat every 25s
// Reconnect with exponential backoff (1s, 2s, 4s, max 30s)
// Max 3 connections per user

const SOCKET_CONFIG = {
  pingInterval: 25000,
  pingTimeout: 20000,
  connectTimeout: 10000,
  maxConnectionsPerUser: 3,
};
```
