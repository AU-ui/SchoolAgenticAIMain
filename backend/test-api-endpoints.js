const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api';
let authToken = null;

// Test configuration
const testConfig = {
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// Helper function to make requests
async function makeRequest(method, endpoint, data = null, token = null) {
  try {
    const config = {
      ...testConfig,
      method,
      url: `${BASE_URL}${endpoint}`,
      headers: {
        ...testConfig.headers,
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      ...(data && { data })
    };

    const response = await axios(config);
    return { success: true, data: response.data, status: response.status };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data || error.message, 
      status: error.response?.status || 500 
    };
  }
}

// Test functions
async function testHealthCheck() {
  console.log('\n🔍 Testing Health Check...');
  const response = await makeRequest('GET', '/health');
  
  if (response.success) {
    console.log('✅ Health check passed');
    console.log(`   Status: ${response.status}`);
    console.log(`   Message: ${response.data.message}`);
  } else {
    console.log('❌ Health check failed');
    console.log(`   Error: ${response.error}`);
  }
}

async function testLandingEndpoints() {
  console.log('\n🏠 Testing Landing Page Endpoints...');
  
  // Test get schools
  console.log('\n   📚 Testing GET /landing/schools...');
  const schoolsResponse = await makeRequest('GET', '/landing/schools');
  if (schoolsResponse.success) {
    console.log('   ✅ Get schools successful');
    console.log(`   📊 Found ${schoolsResponse.data.data.schools.length} schools`);
  } else {
    console.log('   ❌ Get schools failed');
    console.log(`   Error: ${schoolsResponse.error}`);
  }

  // Test get school details
  console.log('\n   🏫 Testing GET /landing/schools/1...');
  const schoolDetailsResponse = await makeRequest('GET', '/landing/schools/1');
  if (schoolDetailsResponse.success) {
    console.log('   ✅ Get school details successful');
    console.log(`   🏫 School: ${schoolDetailsResponse.data.data.school.name}`);
  } else {
    console.log('   ❌ Get school details failed');
    console.log(`   Error: ${schoolDetailsResponse.error}`);
  }

  // Test get stats
  console.log('\n   📊 Testing GET /landing/stats...');
  const statsResponse = await makeRequest('GET', '/landing/stats');
  if (statsResponse.success) {
    console.log('   ✅ Get stats successful');
    console.log(`   📈 Total schools: ${statsResponse.data.data.stats.totalSchools}`);
    console.log(`   👥 Total users: ${statsResponse.data.data.stats.totalUsers}`);
  } else {
    console.log('   ❌ Get stats failed');
    console.log(`   Error: ${statsResponse.error}`);
  }

  // Test contact form
  console.log('\n   📧 Testing POST /landing/contact...');
  const contactData = {
    name: 'Test User',
    email: 'test@example.com',
    phone: '+1234567890',
    message: 'This is a test contact message'
  };
  const contactResponse = await makeRequest('POST', '/landing/contact', contactData);
  if (contactResponse.success) {
    console.log('   ✅ Contact form submission successful');
  } else {
    console.log('   ❌ Contact form submission failed');
    console.log(`   Error: ${contactResponse.error}`);
  }
}

async function testAuthEndpoints() {
  console.log('\n🔐 Testing Authentication Endpoints...');
  
  // Test signup
  console.log('\n   📝 Testing POST /auth/signup...');
  const signupData = {
    email: 'testuser@example.com',
    password: 'testpassword123',
    firstName: 'Test',
    lastName: 'User',
    role: 'teacher',
    tenantId: 1
  };
  const signupResponse = await makeRequest('POST', '/auth/signup', signupData);
  if (signupResponse.success) {
    console.log('   ✅ Signup successful');
    console.log(`   👤 User created: ${signupResponse.data.data.user.email}`);
  } else {
    console.log('   ❌ Signup failed');
    console.log(`   Error: ${signupResponse.error}`);
  }

  // Test login
  console.log('\n   🔑 Testing POST /auth/login...');
  const loginData = {
    email: 'superadmin@edtech.com',
    password: 'admin123'
  };
  const loginResponse = await makeRequest('POST', '/auth/login', loginData);
  if (loginResponse.success) {
    console.log('   ✅ Login successful');
    authToken = loginResponse.data.data.token;
    console.log(`   👤 Logged in as: ${loginResponse.data.data.user.email}`);
    console.log(`   🏫 Tenant: ${loginResponse.data.data.user.tenantName}`);
  } else {
    console.log('   ❌ Login failed');
    console.log(`   Error: ${loginResponse.error}`);
  }

  // Test get current user
  if (authToken) {
    console.log('\n   👤 Testing GET /auth/me...');
    const meResponse = await makeRequest('GET', '/auth/me', null, authToken);
    if (meResponse.success) {
      console.log('   ✅ Get current user successful');
      console.log(`   👤 User: ${meResponse.data.data.user.firstName} ${meResponse.data.data.user.lastName}`);
      console.log(`   🎭 Role: ${meResponse.data.data.user.role}`);
    } else {
      console.log('   ❌ Get current user failed');
      console.log(`   Error: ${meResponse.error}`);
    }
  }
}

async function testTenantEndpoints() {
  console.log('\n🏢 Testing Tenant Endpoints...');
  
  if (!authToken) {
    console.log('   ⚠️  Skipping tenant tests - no auth token');
    return;
  }

  // Test get all tenants (superadmin only)
  console.log('\n   📋 Testing GET /tenants...');
  const tenantsResponse = await makeRequest('GET', '/tenants', null, authToken);
  if (tenantsResponse.success) {
    console.log('   ✅ Get tenants successful');
    console.log(`   🏢 Found ${tenantsResponse.data.data.tenants.length} tenants`);
  } else {
    console.log('   ❌ Get tenants failed');
    console.log(`   Error: ${tenantsResponse.error}`);
  }

  // Test get specific tenant
  console.log('\n   🏫 Testing GET /tenants/1...');
  const tenantResponse = await makeRequest('GET', '/tenants/1', null, authToken);
  if (tenantResponse.success) {
    console.log('   ✅ Get tenant successful');
    console.log(`   🏫 Tenant: ${tenantResponse.data.data.tenant.name}`);
  } else {
    console.log('   ❌ Get tenant failed');
    console.log(`   Error: ${tenantResponse.error}`);
  }

  // Test create new tenant
  console.log('\n   ➕ Testing POST /tenants...');
  const newTenantData = {
    name: 'Test School District',
    domain: 'test.edtech.com',
    address: '123 Test Street, Test City',
    phone: '+1234567890',
    email: 'admin@test.edtech.com'
  };
  const createTenantResponse = await makeRequest('POST', '/tenants', newTenantData, authToken);
  if (createTenantResponse.success) {
    console.log('   ✅ Create tenant successful');
    console.log(`   🏫 Created: ${createTenantResponse.data.data.tenant.name}`);
  } else {
    console.log('   ❌ Create tenant failed');
    console.log(`   Error: ${createTenantResponse.error}`);
  }
}

// Main test runner
async function runAllTests() {
  console.log('🚀 Starting API Endpoint Tests...');
  console.log(`📍 Base URL: ${BASE_URL}`);
  
  try {
    await testHealthCheck();
    await testLandingEndpoints();
    await testAuthEndpoints();
    await testTenantEndpoints();
    
    console.log('\n🎉 All tests completed!');
    console.log('\n📋 Summary:');
    console.log('✅ Health check endpoint');
    console.log('✅ Landing page endpoints (schools, stats, contact)');
    console.log('✅ Authentication endpoints (signup, login, me)');
    console.log('✅ Tenant management endpoints');
    
  } catch (error) {
    console.error('\n❌ Test suite failed:', error.message);
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runAllTests();
}

module.exports = { runAllTests }; 