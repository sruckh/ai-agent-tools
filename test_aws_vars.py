#!/usr/bin/env python3
"""
Quick AWS Variables Test Script
Simple test to verify your AWS environment variables work with Backblaze B2.
"""

import os
import sys
import subprocess

def test_aws_vars():
    """Test if AWS environment variables are properly configured."""
    print("🧪 Quick AWS Variables Test")
    print("=" * 30)
    
    # Check required variables
    required_vars = {
        'AWS_ACCESS_KEY_ID': 'Access Key ID (25-char format for Backblaze)',
        'AWS_SECRET_ACCESS_KEY': 'Secret Access Key',
        'AWS_S3_BUCKET': 'S3 Bucket Name',
        'AWS_ENDPOINT_URL': 'Endpoint URL (e.g., https://s3.us-west-004.backblazeb2.com)',
        'AWS_DEFAULT_REGION': 'Region (e.g., us-west-004)'
    }
    
    print("🔍 Checking environment variables...")
    missing = []
    
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            if 'KEY' in var:
                masked = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                print(f"✅ {var}: {masked}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing:
        print(f"\n❌ Missing variables: {', '.join(missing)}")
        print(f"\n💡 Set them like this:")
        print(f"export AWS_ACCESS_KEY_ID='your-25-char-key-id'")
        print(f"export AWS_SECRET_ACCESS_KEY='your-secret-key'")
        print(f"export AWS_S3_BUCKET='your-bucket-name'")
        print(f"export AWS_ENDPOINT_URL='https://s3.us-west-004.backblazeb2.com'")
        print(f"export AWS_DEFAULT_REGION='us-west-004'")
        return False
    
    # Quick connection test
    print(f"\n🌐 Testing connection...")
    bucket = os.getenv('AWS_S3_BUCKET')
    
    try:
        result = subprocess.run([
            'aws', 's3', 'ls', f's3://{bucket}'
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS! Connected to bucket: {bucket}")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr.strip()}")
            
            # Give specific advice
            if 'InvalidAccessKeyId' in result.stderr:
                print("💡 Key ID issue - make sure you're using the 25-character format")
            elif 'SignatureDoesNotMatch' in result.stderr:
                print("💡 Secret key issue - double-check your AWS_SECRET_ACCESS_KEY")
            elif 'NoSuchBucket' in result.stderr:
                print("💡 Bucket name issue - check AWS_S3_BUCKET value")
            
            return False
            
    except FileNotFoundError:
        print("❌ AWS CLI not installed")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_aws_vars()
    if success:
        print(f"\n🎉 All good! Your AWS variables are configured correctly.")
        print(f"   You can now build and deploy your RunPod container.")
    else:
        print(f"\n🚨 Fix the issues above and try again.")
    sys.exit(0 if success else 1)