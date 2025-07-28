#!/usr/bin/env python3
"""
S3-Compatible Storage Connection Diagnostic Script
Tests S3-compatible storage configuration (e.g., Backblaze B2) and helps identify credential issues.
"""

import os
import sys
import subprocess
import tempfile
from datetime import datetime

def check_env_vars():
    """Check if all required environment variables are set."""
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY', 
        'AWS_S3_BUCKET',
        'AWS_ENDPOINT_URL',
        'AWS_DEFAULT_REGION'
    ]
    
    print("🔍 Checking environment variables...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: NOT SET")
        else:
            # Mask sensitive values
            if 'KEY' in var:
                masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def validate_key_format():
    """Validate that Key ID looks like an S3-compatible application key."""
    key_id = os.getenv('AWS_ACCESS_KEY_ID', '')
    
    print("\n🔑 Validating Key ID format...")
    
    # S3-compatible app keys are typically shorter than master keys
    # Master keys are usually much longer (50+ chars)
    # S3-compatible keys are usually 20-25 characters
    if len(key_id) > 40:
        print(f"⚠️  Key ID is {len(key_id)} characters - this may be a MASTER KEY")
        print("   Master keys don't work with S3-compatible API!")
        print("   Create a new S3-compatible Application Key in Backblaze web UI")
        return False
    elif 20 <= len(key_id) <= 30:
        print(f"✅ Key ID length ({len(key_id)} chars) looks like S3-compatible format")
        return True
    else:
        print(f"⚠️  Key ID length ({len(key_id)} chars) is unusual")
        print("   Double-check this is an S3-compatible Application Key")
        return True

def test_aws_cli_installation():
    """Test if AWS CLI can be installed and configured."""
    print("\n🛠️  Testing AWS CLI installation...")
    
    try:
        # Check if AWS CLI is already installed
        result = subprocess.run(['aws', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ AWS CLI already installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("📦 AWS CLI not found, testing installation...")
    
    # Test if we can install required packages
    try:
        print("   Testing apt-get update...")
        result = subprocess.run(['apt-get', 'update'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ apt-get update failed: {result.stderr}")
            return False
        
        print("   Testing unzip installation...")
        result = subprocess.run(['apt-get', 'install', '-y', '--no-install-recommends', 'unzip'], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ unzip installation failed: {result.stderr}")
            return False
        
        print("✅ System dependencies can be installed")
        return True
        
    except Exception as e:
        print(f"❌ System dependency test failed: {e}")
        return False

def test_s3_connection():
    """Test connection to Backblaze B2 using environment variables."""
    print("\n🌐 Testing Backblaze B2 connection...")
    
    # Set up environment for AWS CLI
    env = os.environ.copy()
    # AWS environment variables already set by user
    # Region already set via AWS_DEFAULT_REGION environment variable
    
    bucket = os.getenv('AWS_S3_BUCKET')
    endpoint = os.getenv('AWS_ENDPOINT_URL')
    
    try:
        # Test bucket listing
        print(f"   Testing bucket listing for: {bucket}")
        result = subprocess.run([
            'aws', 's3', 'ls', f's3://{bucket}',
            '--endpoint-url', endpoint
        ], capture_output=True, text=True, env=env, timeout=30)
        
        if result.returncode == 0:
            print("✅ Successfully connected to Backblaze B2!")
            print(f"   Bucket contents preview: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            
            # Analyze specific error messages
            if 'InvalidAccessKeyId' in result.stderr:
                print("   → This suggests the Key ID is invalid or not S3-compatible")
            elif 'SignatureDoesNotMatch' in result.stderr:
                print("   → This suggests the Application Key is incorrect")
            elif 'NoSuchBucket' in result.stderr:
                print("   → The bucket name may be incorrect")
            elif 'AccessDenied' in result.stderr:
                print("   → Key may not have permission to access this bucket")
            
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection test timed out (30s)")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_file_operations():
    """Test basic file upload/download operations."""
    print("\n📁 Testing file operations...")
    
    bucket = os.getenv('AWS_S3_BUCKET')
    endpoint = os.getenv('AWS_ENDPOINT_URL')
    
    # Set up environment for AWS CLI
    env = os.environ.copy()
    # AWS environment variables already set by user
    # Region already set via AWS_DEFAULT_REGION environment variable
    
    try:
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = f"Test file created at {datetime.now()}\n"
            f.write(test_content)
            temp_file = f.name
        
        test_key = f"runpod-cache/test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        
        print(f"   Uploading test file to: s3://{bucket}/{test_key}")
        result = subprocess.run([
            'aws', 's3', 'cp', temp_file, f's3://{bucket}/{test_key}',
            '--endpoint-url', endpoint
        ], capture_output=True, text=True, env=env, timeout=30)
        
        if result.returncode == 0:
            print("✅ File upload successful!")
            
            # Test download
            download_file = temp_file + '.download'
            print(f"   Downloading test file...")
            result = subprocess.run([
                'aws', 's3', 'cp', f's3://{bucket}/{test_key}', download_file,
                '--endpoint-url', endpoint
            ], capture_output=True, text=True, env=env, timeout=30)
            
            if result.returncode == 0:
                print("✅ File download successful!")
                
                # Verify content
                with open(download_file, 'r') as f:
                    downloaded_content = f.read()
                
                if downloaded_content == test_content:
                    print("✅ File content verification successful!")
                else:
                    print("⚠️  Downloaded content doesn't match uploaded content")
                
                # Cleanup
                os.unlink(download_file)
                
                # Delete test file from bucket
                subprocess.run([
                    'aws', 's3', 'rm', f's3://{bucket}/{test_key}',
                    '--endpoint-url', endpoint
                ], capture_output=True, text=True, env=env)
                
                return True
            else:
                print(f"❌ File download failed: {result.stderr}")
                return False
        else:
            print(f"❌ File upload failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file):
            os.unlink(temp_file)

def main():
    """Run all diagnostic tests."""
    print("🧪 S3-Compatible Storage Connection Diagnostic Tool")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", check_env_vars),
        ("Key Format Validation", validate_key_format),
        ("AWS CLI Installation", test_aws_cli_installation),
        ("S3 Storage Connection", test_s3_connection),
        ("File Operations", test_file_operations)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
        
        if not results[test_name] and test_name in ["Environment Variables", "Key Format Validation"]:
            print(f"\n🛑 Critical test '{test_name}' failed. Stopping here.")
            break
    
    # Summary
    print(f"\n{'=' * 20} SUMMARY {'=' * 20}")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print(f"\n🎉 All tests passed! Your S3-compatible storage configuration is working correctly.")
    else:
        print(f"\n🚨 Some tests failed. Please address the issues above.")
        
        print(f"\n💡 Common solutions:")
        print(f"   1. Create a NEW S3-compatible Application Key (not master key)")
        print(f"   2. Ensure the key has 'listAllBucketNames' permission")
        print(f"   3. Check bucket name and endpoint URL are correct")
        print(f"   4. Verify you're using the Application Key ID (shorter format)")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())