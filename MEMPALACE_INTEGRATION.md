# MemPalace & LM Studio Integration Guide

## Overview

Narrative Nexus V4.0 now integrates **MemPalace** as its primary memory system for novel storage and **LM Studio** (along with other LLM providers) for AI-powered content generation.

### What is MemPalace?

[MemPalace](https://github.com/MemPalace/mempalace) is an advanced memory system that provides AI applications with long-term memory capabilities using:
- **ChromaDB** for vector storage and semantic search
- **Multiple LLM providers** (LM Studio, Ollama, OpenAI, Anthropic)
- **Automatic entity extraction** and deduplication
- **Context-aware retrieval** for consistent storytelling

### What is LM Studio?

[LM Studio](https://lmstudio.ai/) is a desktop application that allows you to:
- Run local LLM models (Llama, Mistral, etc.)
- Expose them via an OpenAI-compatible API
- Use them offline with full privacy
- Test different models easily

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Narrative      │────▶│   MemPalace      │────▶│  LM Studio /    │
│  Nexus Frontend │     │   Service        │     │  Ollama /       │
│                 │◀────│                  │◀────│  OpenAI         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │   ChromaDB       │
                        │   (Vector Store) │
                        └──────────────────┘
```

## Setup Instructions

### 1. Install LM Studio

**Download:** https://lmstudio.ai/

**Steps:**
1. Download and install LM Studio for your OS
2. Open LM Studio and download a model (e.g., `Llama-3.2-3B-Instruct`)
3. Go to the "Server" tab (↔️ icon)
4. Click "Start Server"
5. Note the port (default: `1234`)

**Verify LM Studio is running:**
```bash
curl http://localhost:1234/v1/models
```

Expected response:
```json
{"object":"list","data":[{"id":"local-model","object":"model"}]}
```

### 2. Configure Environment Variables

Create or update `.env` in the backend directory:

```bash
# MemPalace Configuration
MEMPALACE_LLM_PROVIDER=openai-compat
MEMPALACE_LLM_MODEL=local-model
MEMPALACE_LLM_ENDPOINT=http://localhost:1234/v1
MEMPALACE_LLM_API_KEY=not-needed
MEMPALACE_CHROMA_PATH=./mempalace_data
MEMPALACE_TIMEOUT=120

# Alternative: Ollama
# MEMPALACE_LLM_PROVIDER=ollama
# MEMPALACE_LLM_MODEL=llama3.2
# MEMPALACE_LLM_ENDPOINT=http://localhost:11434

# Alternative: OpenAI
# MEMPALACE_LLM_PROVIDER=openai
# MEMPALACE_LLM_MODEL=gpt-4o-mini
# MEMPALACE_LLM_API_KEY=sk-your-key-here
```

### 3. Initialize MemPalace Service

**Via API:**
```bash
curl -X POST http://localhost:8000/api/v1/mempalace/initialize \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai-compat","model":"local-model","endpoint":"http://localhost:1234/v1"}'
```

Response:
```json
{"success":true,"message":"MemPalace initialized successfully"}
```

## API Endpoints

### 1. Check MemPalace Status

```bash
GET /api/v1/mempalace/status
```

Response:
```json
{
  "initialized": true,
  "config": {
    "llm_provider": "openai-compat",
    "llm_model": "local-model",
    "chroma_path": "./mempalace_data"
  },
  "provider": {
    "name": "openai-compat",
    "model": "local-model",
    "endpoint": "http://localhost:1234/v1",
    "available": true,
    "status": "Provider is available"
  }
}
```

### 2. Test LLM Connection

```bash
POST /api/v1/mempalace/test-llm
Content-Type: application/json

{"provider":"openai-compat","model":"local-model","endpoint":"http://localhost:1234/v1"}
```

### 3. Debug Connection Issues

```bash
POST /api/v1/mempalace/debug/connection
Content-Type: application/json

{"provider":"openai-compat","endpoint":"http://localhost:1234/v1","timeout":10}
```

Response includes step-by-step diagnostics showing URL validation, provider creation, availability check, and query test results.

### 4. Store Memory

```bash
POST /api/v1/mempalace/memory/store
Content-Type: application/json

{
  "collection_name": "story_123",
  "content": "Character John is a detective in Victorian London",
  "metadata": {"type": "character", "character_name": "John", "chapter": 1}
}
```

### 5. Search Memories

```bash
POST /api/v1/mempalace/memory/search
Content-Type: application/json

{"collection_name":"story_123","query":"Who is John?","n_results":5}
```

### 6. Check Story Consistency

```bash
POST /api/v1/mempalace/consistency/check
Content-Type: application/json

{
  "story_id": "123",
  "new_content": "John pulled out his smartphone and called Mary.",
  "context": "Victorian era setting"
}
```

Response:
```json
{
  "success": true,
  "report": {
    "consistent": false,
    "issues": [{
      "type": "anachronism",
      "description": "Smartphones didn't exist in Victorian era",
      "severity": "high"
    }],
    "suggestions": ["Replace 'smartphone' with 'telegram' or 'letter'"]
  }
}
```

### 7. Extract Entities

```bash
POST /api/v1/mempalace/entities/extract
Content-Type: application/json

{"story_id":"123","content":"Detective John Smith walked through London."}
```

Response:
```json
{
  "success": true,
  "entities": {
    "characters": ["John Smith"],
    "locations": ["London"],
    "objects": [],
    "organizations": []
  }
}
```

## Common Errors & Solutions

### Error 1: "Failed to connect to LLM provider"

**Symptoms:**
- `/test-llm` returns `success: false`
- Error: "Connection refused" or "Timeout"

**Solutions:**

1. **Check if LM Studio is running:**
   ```bash
   curl http://localhost:1234/v1/models
   ```

2. **Verify endpoint URL:**
   - Default LM Studio: `http://localhost:1234/v1`
   - Default Ollama: `http://localhost:11434`
   - No trailing slashes

3. **Use debug endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/mempalace/debug/connection \
     -H "Content-Type: application/json" \
     -d '{"provider":"openai-compat","endpoint":"http://localhost:1234/v1"}'
   ```

### Error 2: "Model not found"

**Symptoms:**
- LM Studio returns 404
- Model name mismatch

**Solutions:**

1. **List available models:**
   ```bash
   curl http://localhost:1234/v1/models
   ```

2. **Load a model in LM Studio:**
   - Open LM Studio → "My Models" tab
   - Click on downloaded model
   - Wait for "Ready to serve"

3. **Use correct model name:**
   - LM Studio: `local-model`
   - Ollama: actual model name (e.g., `llama3.2`)

### Error 3: "ChromaDB initialization failed"

**Solutions:**

1. **Check disk space:** `df -h .`

2. **Clear ChromaDB data:**
   ```bash
   rm -rf ./mempalace_data
   ```

3. **Ensure write permissions:**
   ```bash
   chmod -R 755 ./mempalace_data
   ```

### Error 4: "Timeout during query"

**Solutions:**

1. **Increase timeout:**
   ```bash
   MEMPALACE_TIMEOUT=300
   ```

2. **Use smaller/faster model:**
   - Try `Llama-3.2-1B` instead of `7B`
   - Use quantized models (Q4_K_M)

3. **Reduce context length** in LM Studio settings

### Error 5: "No space left on device"

**Solutions:**

1. **Clean npm cache:**
   ```bash
   cd frontend
   rm -rf node_modules/.cache
   npm cache clean --force
   ```

2. **Remove old ChromaDB data:**
   ```bash
   rm -rf backend/mempalace_data
   ```

3. **Check disk usage:**
   ```bash
   df -h
   du -sh ./* | sort -h
   ```

## Frontend Integration

The frontend automatically connects to MemPalace through the API client:

```typescript
import { api } from './api/client';

// Check MemPalace status
const status = await api.getMemPalaceStatus();
console.log(`Initialized: ${status.initialized}`);

// Test LLM connection
const result = await api.testLLMConnection({
  provider: 'openai-compat',
  model: 'local-model',
  endpoint: 'http://localhost:1234/v1'
});

// Store character memory
await api.storeMemory(
  'story_123',
  'John is a detective in Victorian London',
  { type: 'character', name: 'John' }
);

// Check consistency before saving
const report = await api.checkConsistency(
  'story_123',
  'John used his smartphone',
  'Victorian setting'
);

if (!report.consistent) {
  console.warn('Issues:', report.issues);
}

// Search memories
const memories = await api.searchMemories('story_123', 'detective', 5);

// Extract entities
const entities = await api.extractEntities('story_123', 'Chapter content...');
```

## Best Practices

### Memory Organization

- **Descriptive collection names:** `story_{id}`, `story_{id}_characters`
- **Rich metadata:** Include chapter numbers, character names, timestamps
- **Tag memories:** Use tags like `character`, `plot`, `setting`

### Performance Optimization

- **Batch operations:** Store multiple memories together
- **Limit search results:** Use `n_results` parameter (default: 5)
- **Cache frequently accessed data**

### Consistency Checking

- **Check before saving:** Run checks before committing changes
- **Provide context:** Better analysis with relevant context
- **Review suggestions:** Don't blindly accept AI suggestions

## Troubleshooting Checklist

- [ ] LM Studio server is running (check port 1234)
- [ ] Model is loaded in LM Studio
- [ ] Correct endpoint URL in .env
- [ ] MemPalace service is initialized
- [ ] ChromaDB directory exists and writable
- [ ] No firewall blocking connections
- [ ] Sufficient disk space available
- [ ] Backend restarted after config changes

## Quick Start Commands

```bash
# Start LM Studio server (in LM Studio app)
# Then verify:
curl http://localhost:1234/v1/models

# Start Narrative Nexus backend
cd backend
uvicorn app.main:app --reload

# Initialize MemPalace
curl -X POST http://localhost:8000/api/v1/mempalace/initialize \
  -H "Content-Type: application/json" \
  -d '{"provider":"openai-compat","model":"local-model","endpoint":"http://localhost:1234/v1"}'

# Check status
curl http://localhost:8000/api/v1/mempalace/status

# Start frontend
cd frontend
npm run dev
```

## Additional Resources

- [MemPalace Documentation](https://mempalaceofficial.com/guide/getting-started.html)
- [MemPalace GitHub](https://github.com/MemPalace/mempalace)
- [LM Studio Download](https://lmstudio.ai/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)

## Support

For issues:
- **MemPalace:** [GitHub Issues](https://github.com/MemPalace/mempalace/issues)
- **LM Studio:** [Discord](https://discord.gg/lmstudio)
- **Narrative Nexus:** Open issue on this repository
