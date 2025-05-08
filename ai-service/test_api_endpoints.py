# backend/test_api_endpoints.py

import httpx
import asyncio
import sys

# --- Configuration ---
# Base URL of your running FastAPI application
BASE_URL = "http://127.0.0.1:8000"
# Get project name from main.py for accurate checks
# You might need to adjust this if your settings access changes
try:
    # Attempt to import settings IF the script is run from 'backend' dir
    from app.core.config import settings
    EXPECTED_SERVICE_NAME = settings.PROJECT_NAME
except ImportError:
    # Fallback if run from elsewhere or if direct import fails
    print("Warning: Could not import settings directly. Using default service name 'AI Service'.")
    EXPECTED_SERVICE_NAME = "AI Service"
# --- End Configuration ---

async def check_endpoint(client: httpx.AsyncClient, url: str, expected_status: int, expected_json: dict = None):
    """Helper function to check a single endpoint."""
    print(f"\n--- Testing Endpoint: {url} ---")
    try:
        response = await client.get(url, timeout=10.0) # Add a timeout
        print(f"Status Code: {response.status_code}")

        if response.status_code == expected_status:
            print(f"  Expected Status: {expected_status} (OK)")
        else:
            print(f"  Expected Status: {expected_status} (FAIL!)")
            print(f"  Response Text: {response.text[:200]}...") # Show beginning of response
            return False # Test failed

        if expected_json:
            try:
                actual_json = response.json()
                print(f"Response JSON: {actual_json}")
                if actual_json == expected_json:
                    print(f"  Expected JSON: Matches (OK)")
                else:
                    print(f"  Expected JSON: {expected_json} (FAIL!)")
                    print(f"  Actual JSON:   {actual_json}")
                    return False # Test failed
            except Exception as e:
                print(f"  Failed to parse response as JSON: {e} (FAIL!)")
                print(f"  Response Text: {response.text[:200]}...")
                return False # Test failed

        print(">>> Test PASSED <<<")
        return True # Test passed

    except httpx.ConnectError:
        print(f"!! Connection Error: Could not connect to {url}.")
        print("   Is the FastAPI server running at the correct address and port?")
        print(">>> Test FAILED <<<")
        return False
    except httpx.TimeoutException:
        print(f"!! Timeout Error: Request to {url} timed out.")
        print(">>> Test FAILED <<<")
        return False
    except Exception as e:
        print(f"!! An unexpected error occurred: {e}")
        print(">>> Test FAILED <<<")
        return False

async def run_tests():
    """Runs all defined API tests."""
    print(f"Starting tests against base URL: {BASE_URL}")
    all_passed = True

    async with httpx.AsyncClient() as client:
        # Test 1: Root endpoint '/'
        passed = await check_endpoint(
            client,
            url=f"{BASE_URL}/",
            expected_status=200,
            expected_json={"message": f"Welcome to the {EXPECTED_SERVICE_NAME}"}
        )
        if not passed: all_passed = False

        # Test 2: Health check endpoint '/health'
        passed = await check_endpoint(
            client,
            url=f"{BASE_URL}/health",
            expected_status=200,
            expected_json={"status": "ok", "service": EXPECTED_SERVICE_NAME}
        )
        if not passed: all_passed = False

    print("\n--- Test Summary ---")
    if all_passed:
        print("✅ All tests passed!")
        # Exit with code 0 for success (useful in CI/CD)
        # sys.exit(0)
    else:
        print("❌ Some tests failed.")
        # Exit with code 1 for failure
        # sys.exit(1)


if __name__ == "__main__":
    # Ensure httpx is installed
    try:
        import httpx
    except ImportError:
        print("Error: 'httpx' library is not installed.")
        print("Please install it: pip install httpx")
        sys.exit(1)

    # Run the async tests
    asyncio.run(run_tests())