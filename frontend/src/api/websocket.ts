import { io, Socket } from 'socket.io-client';
import type { PipelineState } from '../types';

type WSEventHandler = (payload: any) => void;

class WebSocketClient {
  private socket: Socket | null = null;
  private eventHandlers: Map<string, Set<WSEventHandler>> = new Map();
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(storyId?: string) {
    const url = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`;
    
    this.socket = io(url, {
      query: storyId ? { story_id: storyId } : {},
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    // Handle different message types
    this.socket.on('pipeline_update', (payload: PipelineState) => {
      this.emit('pipeline_update', payload);
    });

    this.socket.on('story_update', (payload: any) => {
      this.emit('story_update', payload);
    });

    this.socket.on('character_update', (payload: any) => {
      this.emit('character_update', payload);
    });

    this.socket.on('memory_update', (payload: any) => {
      this.emit('memory_update', payload);
    });

    this.socket.on('error', (payload: any) => {
      this.emit('error', payload);
    });

    return this;
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  on(event: string, handler: WSEventHandler) {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set());
    }
    this.eventHandlers.get(event)!.add(handler);
    return () => this.off(event, handler);
  }

  off(event: string, handler: WSEventHandler) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  private emit(event: string, payload: any) {
    const handlers = this.eventHandlers.get(event);
    if (handlers) {
      handlers.forEach((handler) => handler(payload));
    }
  }

  // Send messages to server
  send(type: string, payload: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit(type, payload);
    } else {
      console.warn('WebSocket not connected');
    }
  }

  // Pipeline control messages
  approvePhase(phase: string) {
    this.send('approve_phase', { phase });
  }

  rejectPhase(phase: string, reason: string) {
    this.send('reject_phase', { phase, reason });
  }

  requestPipelineUpdate() {
    this.send('request_update', {});
  }
}

export const wsClient = new WebSocketClient();
export default wsClient;
