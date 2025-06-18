#!/bin/bash
# QA Test Script using curl to test student submission workflow

BASE_URL="https://dd.kronisto.net/api/v1"

echo "=== QA TEST: Student Submission Workflow ==="
echo

# Function to login and get token
login_user() {
    local username=$1
    local password=$2
    echo "Logging in as $username..."
    
    response=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=$username&password=$password&grant_type=password")
    
    if [ $? -eq 0 ]; then
        token=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        if [ -n "$token" ]; then
            echo "✅ SUCCESS: $username logged in"
            echo "$token"
        else
            echo "❌ FAILED: Could not extract token for $username"
            echo "Response: $response"
            echo ""
        fi
    else
        echo "❌ FAILED: Login failed for $username"
        echo ""
    fi
}

# Test 1: Login as student1
echo "1. Testing login as student1..."
STUDENT1_TOKEN=$(login_user "student1" "12345678")
echo

if [ -z "$STUDENT1_TOKEN" ]; then
    echo "❌ CRITICAL: Cannot proceed without student1 token"
    exit 1
fi

# Test 2: Create student update
echo "2. Creating new student update..."
response=$(curl -s -X POST "$BASE_URL/updates/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $STUDENT1_TOKEN" \
    -d '{
        "user_id": 9,
        "meeting_id": 2,
        "progress_text": "QA TEST: Completed database schema refactor and testing new unified agenda system. Successfully migrated from fragmented tables to unified approach.",
        "challenges_text": "QA TEST: Minor challenges with backwards compatibility, but resolved with adapter pattern.",
        "next_steps_text": "QA TEST: Complete frontend migration and remove legacy endpoints.",
        "meeting_notes": "QA TEST: Discussed new schema benefits with team.",
        "will_present": true
    }')

echo "Create response: $response"

# Extract update ID
UPDATE_ID=$(echo "$response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
echo "Created update ID: $UPDATE_ID"
echo

if [ -z "$UPDATE_ID" ]; then
    echo "❌ FAILED: Could not create student update"
    exit 1
fi

echo "✅ SUCCESS: Created student update with ID $UPDATE_ID"
echo

# Test 3: student1 edit their own submission
echo "3. Testing student1 editing their own submission..."
response=$(curl -s -X PUT "$BASE_URL/updates/$UPDATE_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $STUDENT1_TOKEN" \
    -d '{
        "progress_text": "QA TEST EDIT: Updated progress text by original student",
        "challenges_text": "QA TEST EDIT: Updated challenges by original student"
    }')

if echo "$response" | grep -q "QA TEST EDIT"; then
    echo "✅ SUCCESS: student1 can edit their own submission"
else
    echo "❌ FAILED: student1 cannot edit their own submission"
    echo "Response: $response"
fi
echo

# Test 4: testuser cannot edit
echo "4. Testing testuser (different student) cannot edit..."
TESTUSER_TOKEN=$(login_user "testuser" "password123")

if [ -n "$TESTUSER_TOKEN" ]; then
    response=$(curl -s -X PUT "$BASE_URL/updates/$UPDATE_ID" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TESTUSER_TOKEN" \
        -d '{"progress_text": "UNAUTHORIZED EDIT ATTEMPT"}')
    
    if echo "$response" | grep -q "403\|Forbidden\|only access your own"; then
        echo "✅ SUCCESS: testuser correctly denied permission"
    else
        echo "❌ FAILED: testuser should be denied"
        echo "Response: $response"
    fi
else
    echo "❌ FAILED: Could not login as testuser"
fi
echo

# Test 5: cerebro (admin) can edit
echo "5. Testing cerebro (admin) can edit..."
ADMIN_TOKEN=$(login_user "cerebro" "123")

if [ -n "$ADMIN_TOKEN" ]; then
    response=$(curl -s -X PUT "$BASE_URL/updates/$UPDATE_ID" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -d '{"meeting_notes": "QA TEST: Admin edit - verified admin permissions"}')
    
    if echo "$response" | grep -q "Admin edit"; then
        echo "✅ SUCCESS: cerebro (admin) can edit any submission"
    else
        echo "❌ FAILED: admin edit failed"
        echo "Response: $response"
    fi
else
    echo "❌ FAILED: Could not login as cerebro"
fi
echo

# Test 6: aalexandrian (faculty) can edit
echo "6. Testing aalexandrian (faculty) can edit..."
FACULTY_TOKEN=$(login_user "aalexandrian" "12345678")

if [ -n "$FACULTY_TOKEN" ]; then
    response=$(curl -s -X PUT "$BASE_URL/updates/$UPDATE_ID" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $FACULTY_TOKEN" \
        -d '{"meeting_notes": "QA TEST: Faculty edit - verified faculty permissions"}')
    
    if echo "$response" | grep -q "Faculty edit"; then
        echo "✅ SUCCESS: aalexandrian (faculty) can edit student submissions"
    else
        echo "❌ FAILED: faculty edit failed"
        echo "Response: $response"
    fi
else
    echo "❌ FAILED: Could not login as aalexandrian"
fi
echo

# Test 7: View agenda as different users
echo "7. Testing meeting agenda view..."
for user in "student1:$STUDENT1_TOKEN:STUDENT" "cerebro:$ADMIN_TOKEN:ADMIN" "aalexandrian:$FACULTY_TOKEN:FACULTY"; do
    username=$(echo "$user" | cut -d':' -f1)
    token=$(echo "$user" | cut -d':' -f2)
    role=$(echo "$user" | cut -d':' -f3)
    
    if [ -n "$token" ]; then
        response=$(curl -s -X GET "$BASE_URL/meetings/2/agenda" \
            -H "Authorization: Bearer $token")
        
        if echo "$response" | grep -q "student_updates"; then
            update_count=$(echo "$response" | grep -o '"student_updates":\[[^]]*\]' | grep -o '"id":[0-9]*' | wc -l)
            echo "✅ SUCCESS: $role can view agenda ($update_count student updates visible)"
        else
            echo "❌ FAILED: $role cannot view agenda"
        fi
    fi
done

echo
echo "=== QA TEST COMPLETE ==="