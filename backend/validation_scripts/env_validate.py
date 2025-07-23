"""
Configuration Validation Script
Run this script to validate your environment configuration before starting the server
"""
import os
from dotenv import load_dotenv

def validate_environment_configuration():
    """Validate all required environment variables are properly set"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔍 Validating Environment Configuration...")
    print("=" * 50)
    
    # Required API Keys
    api_keys = []
    for i in range(1, 11):
        key = os.getenv(f"GEMINI_API_KEY_{i}")
        if key:
            api_keys.append(f"GEMINI_API_KEY_{i}")
    
    print(f"✅ API Keys Found: {len(api_keys)} keys")
    for key_name in api_keys:
        key_value = os.getenv(key_name)
        print(f"   - {key_name}: ...{key_value[-4:] if key_value and len(key_value) > 4 else 'INVALID'}")
    
    if len(api_keys) == 0:
        print("❌ ERROR: No API keys found! Set GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.")
        return False
    
    # Timeout Configuration
    print("\n⏰ Timeout Configuration:")
    api_timeout = os.getenv("GEMINI_API_TIMEOUT", "720")
    overall_timeout = os.getenv("OVERALL_PROCESS_TIMEOUT", "1200")
    print(f"   - Individual API Timeout: {api_timeout}s ({int(api_timeout)//60} minutes)")
    print(f"   - Overall Process Timeout: {overall_timeout}s ({int(overall_timeout)//60} minutes)")
    
    # Exponential Backoff Configuration
    print("\n🚨 Exponential Backoff Configuration:")
    max_retries = os.getenv("GEMINI_MAX_RETRIES", "6")
    base_delay = os.getenv("GEMINI_BASE_RETRY_DELAY", "30")
    max_delay = os.getenv("GEMINI_MAX_RETRY_DELAY", "600")
    exp_multiplier = os.getenv("GEMINI_EXPONENTIAL_MULTIPLIER", "2.0")
    overload_multiplier = os.getenv("GEMINI_OVERLOAD_MULTIPLIER", "5.0")
    
    print(f"   - Max Retries: {max_retries}")
    print(f"   - Base Delay: {base_delay}s")
    print(f"   - Max Delay: {max_delay}s ({int(max_delay)//60} minutes)")
    print(f"   - Exponential Multiplier: {exp_multiplier}x")
    print(f"   - Overload Multiplier: {overload_multiplier}x")
    
    # Pro Model Protection
    print("\n🛡️ Pro Model Protection:")
    pro_min_delay = os.getenv("PRO_MODEL_MIN_DELAY", "15.0")
    pro_overload_delay = os.getenv("PRO_MODEL_OVERLOAD_DELAY", "120.0")
    print(f"   - Minimum Delay Between Pro Calls: {pro_min_delay}s")
    print(f"   - Post-Overload Delay: {pro_overload_delay}s ({int(float(pro_overload_delay))//60} minutes)")
    
    # CORS Configuration
    print("\n🌐 CORS Configuration:")
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    print(f"   - Frontend URL: {frontend_url}")
    
    # Example Delay Calculation
    print("\n📊 Example Exponential Backoff Delays (for 503 overload):")
    base = int(base_delay)
    multiplier = float(exp_multiplier)
    overload_mult = float(overload_multiplier)
    max_delay_val = int(max_delay)
    
    for attempt in range(int(max_retries)):
        delay = base * overload_mult * (multiplier ** attempt)
        delay = min(delay, max_delay_val)
        print(f"   - Attempt {attempt + 1}: {delay:.0f}s ({delay//60:.0f}m {delay%60:.0f}s)")
    
    print("\n" + "=" * 50)
    print("✅ Configuration validation completed successfully!")
    print("\n💡 Tips:")
    print("   - Ensure you have multiple API keys for better rate limiting")
    print("   - Monitor logs for '503 OVERLOAD detected' messages")
    print("   - Exponential backoff will automatically handle overload errors")
    print("   - Pro model calls are limited to 1 concurrent with 15s delays")
    
    return True

if __name__ == "__main__":
    try:
        validate_environment_configuration()
    except Exception as e:
        print(f"❌ Configuration validation failed: {str(e)}")
        print("Please check your .env file and fix any issues.")