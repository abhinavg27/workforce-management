#!/usr/bin/env python3
"""
Test script to validate the /optimize API fix
"""

import json

# Test data that should work with the fixed API
test_payload = {
    "date": "2025-08-05",
    "tasks": [
        {
            "id": "1",
            "name": "Test Task",
            "skill_id": 100,
            "priority": 5,
            "units": 50,
            "dependencies": [],
            "type": "In"
        }
    ],
    "workers": [
        {
            "id": "TEST001",
            "name": "Test Worker",
            "skills": [100],
            "productivity": {100: 80},
            "skill_levels": {100: 3},
            "shift_start": "08:00",
            "shift_end": "16:00",
            "break_minutes": 60
        }
    ]
}

def test_optimization_logic():
    """Test the optimization logic without running the server"""
    print("Testing optimization logic...")
    
    # Import the necessary functions (if running in the right environment)
    try:
        from main import get_skill_quality_score, get_minimum_skill_level_required
        from main import Worker, Task, OptimizeRequest
        
        # Test the helper functions
        worker_data = test_payload["workers"][0]
        worker = Worker(**worker_data)
        
        quality_score = get_skill_quality_score(worker, 100)
        print(f"✅ Quality score calculation: {quality_score:.3f}")
        
        min_level = get_minimum_skill_level_required(5)
        print(f"✅ Minimum skill level for priority 5: {min_level}")
        
        # Test request parsing
        request = OptimizeRequest(**test_payload)
        print(f"✅ Request parsing successful: {len(request.tasks)} tasks, {len(request.workers)} workers")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Cannot test directly (missing dependencies): {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_json_payload():
    """Test that the JSON payload is valid"""
    try:
        json_str = json.dumps(test_payload)
        parsed = json.loads(json_str)
        print("✅ JSON payload is valid")
        return True
    except Exception as e:
        print(f"❌ JSON payload invalid: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing API fix...")
    
    # Test JSON payload
    test_json_payload()
    
    # Test optimization logic (if possible)
    test_optimization_logic()
    
    print("\n📋 Test payload for manual API testing:")
    print(json.dumps(test_payload, indent=2))
    
    print("\n🚀 To test the API:")
    print("1. Start the optimizer: uvicorn main:app --reload")
    print("2. Use curl or Postman to POST to http://localhost:8000/optimize")
    print("3. Use the test payload above")