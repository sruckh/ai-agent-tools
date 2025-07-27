# RunPod Serverless with Backblaze B2 Persistent Storage

This guide explains how to configure your RunPod serverless endpoint to use Backblaze B2 for persistent storage, solving out-of-space errors and providing true persistence across serverless instances.

## Why Backblaze B2?

- **Cost Effective**: Much cheaper than storing data in container images
- **True Persistence**: Data survives across serverless cold starts and shutdowns  
- **S3 Compatible**: Works with standard AWS CLI and Python libraries
- **Fast Downloads**: Direct S3-compatible access without RunPod markup
- **Unlimited Size**: No container size restrictions

## Required Backblaze B2 Setup

### 1. Create Backblaze B2 Account and Bucket

1. Sign up at [backblaze.com](https://www.backblaze.com/b2/cloud-storage.html)
2. Create a new bucket (e.g., `my-runpod-cache`)
3. Note your region endpoint (e.g., `s3.us-west-004.backblazeb2.com`)

### 2. Generate Application Key

1. Go to **App Keys** in your Backblaze B2 console
2. Click **Add a New Application Key**
3. Configure:
   - **Name**: `RunPod Serverless Cache`
   - **Allow access to**: Choose your bucket
   - **Type of access**: Read and Write
4. Copy the **keyID** and **applicationKey**

## RunPod Endpoint Configuration

### Required Environment Variables

Set these environment variables in your RunPod endpoint configuration:

```bash
# Backblaze B2 Credentials (from your App Key)
BACKBLAZE_KEY_ID=your_key_id_here
BACKBLAZE_APPLICATION_KEY=your_application_key_here

# Backblaze B2 Bucket Configuration  
BACKBLAZE_BUCKET=your-bucket-name
BACKBLAZE_ENDPOINT=s3.us-west-004.backblazeb2.com

# Handler Configuration
HANDLER_TYPE=tts  # or video, audio, storage
```

### Finding Your Backblaze Endpoint

Your endpoint URL depends on your Backblaze B2 region:

- **US West**: `s3.us-west-004.backblazeb2.com`
- **US East**: `s3.us-east-005.backblazeb2.com`  
- **EU Central**: `s3.eu-central-003.backblazeb2.com`

Check your bucket details in the Backblaze B2 console for the exact endpoint.

## How It Works

### Storage Architecture

```
RunPod Serverless Container
├── /tmp/runpod-cache/           # Local fast cache
│   ├── models/                  # AI model files
│   ├── pip/                     # Python package cache
│   └── deps/                    # System dependencies
│
└── Backblaze B2 Bucket
    └── runpod-cache/            # Persistent storage
        ├── models/              # Synced model files
        ├── pip/                 # Synced package cache
        └── deps/                # Synced dependencies
```

### Startup Process

1. **Validation**: Check required Backblaze B2 environment variables
2. **S3 Setup**: Configure AWS CLI for Backblaze B2 compatibility
3. **Cache Sync**: Download existing cached data from Backblaze B2
4. **Installation**: Install dependencies using local cache
5. **Handler Start**: Launch your AI handler

### Shutdown Process

1. **Auto-Backup**: Upload any new cache data to Backblaze B2
2. **Cleanup**: Clean up local temporary files
3. **Terminate**: Container shuts down

## Performance Benefits

### First Run (Cold Start)
- **Download Cache**: 30-60 seconds (if exists)
- **Install Dependencies**: 3-5 minutes (with fast local cache)
- **Total Cold Start**: ~4-6 minutes

### Subsequent Runs (Warm Start)
- **Download Cache**: 10-30 seconds (incremental sync)
- **Skip Installation**: Dependencies already cached
- **Total Warm Start**: ~30-60 seconds

### Storage Savings
- **Container Size**: Stays minimal (~50-100MB)
- **No Pre-installation**: Zero build-time dependencies
- **Persistent Cache**: Never re-download the same packages

## Troubleshooting

### Environment Variable Issues

**Error**: `Missing required Backblaze B2 environment variables`

**Solution**: Verify all 4 environment variables are set in RunPod:
- `BACKBLAZE_KEY_ID`
- `BACKBLAZE_APPLICATION_KEY` 
- `BACKBLAZE_BUCKET`
- `BACKBLAZE_ENDPOINT`

### Connection Issues

**Error**: `Failed to connect to Backblaze B2`

**Solutions**:
1. Verify bucket name is correct
2. Check endpoint URL matches your region
3. Ensure App Key has Read/Write access to the bucket
4. Verify App Key is not expired

### Performance Issues

**Slow Downloads**: Check if you're using the correct regional endpoint closest to your RunPod datacenter.

**Large Cache**: Consider cleaning up old model files or pip cache periodically.

## Cost Optimization

### Backblaze B2 Pricing (as of 2024)
- **Storage**: $0.005/GB/month
- **Downloads**: $0.01/GB (first 1GB/day free)
- **API Calls**: Very low cost

### Example Monthly Costs
- **10GB AI Models**: ~$0.05/month storage
- **5GB Package Cache**: ~$0.025/month storage  
- **Daily Usage**: Usually within free tier

Much cheaper than pre-installing in container images!

## Security Notes

- Backblaze B2 credentials are stored as RunPod environment variables
- Data is encrypted in transit and at rest
- Use dedicated App Keys with minimal permissions
- Regularly rotate App Keys for security

## Monitoring

Check logs for these key indicators:

- `✅ Successfully connected to Backblaze B2 bucket`
- `📥 Syncing models from Backblaze B2...`
- `📤 Backing up models to Backblaze B2...`
- `✅ Dependencies already installed, skipping installation`

These confirm the persistent storage system is working correctly.