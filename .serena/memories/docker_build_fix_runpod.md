# Docker Build Fix: RunPod Serverless Container

## Issue Summary
Critical Docker build failure in GitHub Actions CI/CD pipeline for RunPod serverless container deployment.

## Technical Problem
- **File**: `runpod.Dockerfile` lines 36-63
- **Error**: `dockerfile parse error on line 37: unknown instruction: HANDLER_TYPE=${HANDLER_TYPE:-tts}`
- **Root Cause**: Multiline RUN command with embedded bash script not properly escaped for Docker Buildx parser

## Solution Applied
**Before (Problematic)**:
```dockerfile
RUN echo '#!/bin/bash
HANDLER_TYPE=${HANDLER_TYPE:-tts}
cd /app/runpod_handlers
...
```

**After (Fixed)**:
```dockerfile
RUN echo '#!/bin/bash\n\
HANDLER_TYPE=${HANDLER_TYPE:-tts}\n\
cd /app/runpod_handlers\n\
...
```

## Key Learning
Docker Buildx requires explicit line continuation syntax (`\n\`) for multiline RUN commands. Heredoc-style multiline strings are not compatible with Docker's strict parsing requirements.

## Impact
- ✅ CI/CD pipeline unblocked
- ✅ All container variants build successfully (standard, CUDA, RunPod serverless)
- ✅ Automated deployment to DockerHub restored

## Prevention
- Use proper Docker syntax for multiline commands
- Test Dockerfiles locally before pushing to CI/CD
- Consider single-line alternatives for complex bash scripts

## Related Files
- `runpod.Dockerfile` - Fixed multiline RUN command
- `.github/workflows/docker-build.yml` - CI/CD pipeline that was failing
- `TASKS.md` - Task TASK-2025-07-26-005 documented
- `JOURNAL.md` - Full technical details recorded