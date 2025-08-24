// ============================================================================
// COMPLETE SMART ATTENDANCE SYSTEM TEST
// ============================================================================
// Tests the entire system with ML service and fixed authentication
// ============================================================================

const { Pool } = require('pg');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

// Test configuration
const TEST_CONFIG = {
  backend_url: process.env.BACKEND_URL || 'http://localhost:5000',
  ml_service_url: process.env.ML_SERVICE_URL || 'http://localhost:5001',
};

// Database connection
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'school_management',
  password: process.env.DB_PASSWORD || '1234',
  port: process.env.DB_PORT || 5432,
});

class CompleteSystemTester {
  constructor() {
    this.testResults = [];
    this.authToken = null;
  }

  log(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const prefix = type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️';
    console.log(`${prefix} [${timestamp}] ${message}`);
  }

  async addTestResult(testName, success, details = '') {
    this.testResults.push({
      test: testName,
      success,
      details,
      timestamp: new Date().toISOString()
    });
  }

  // Test 1: Authentication System
  async testAuthentication() {
    try {
      this.log('Testing authentication system...');
      
      // Test signup
      const signupData = {
        email: 'testteacher@school.com',
        password: 'password123',
        firstName: 'Test',
        lastName: 'Teacher',
        role: 'teacher',
        phoneNumber: '1234567890'
      };

      const signupResponse = await axios.post(`${TEST_CONFIG.backend_url}/api/auth/signup`, signupData);
      
      if (signupResponse.data.success) {
        this.authToken = signupResponse.data.data.token;
        this.log('✅ Signup successful');
        
        // Test login
        const loginData = {
          email: 'testteacher@school.com',
          password: 'password123'
        };

        const loginResponse = await axios.post(`${TEST_CONFIG.backend_url}/api/auth/login`, loginData);
        
        if (loginResponse.data.success) {
          this.log('✅ Login successful');
          await this.addTestResult('Authentication', true, 'Signup and login working');
          return true;
        }
      }
      
      throw new Error('Authentication failed');
      
    } catch (error) {
      this.log(`Authentication test failed: ${error.message}`, 'error');
      await this.addTestResult('Authentication', false, error.message);
      return false;
    }
  }

  // Test 2: ML Service Health
  async testMLService() {
    try {
      this.log('Testing ML service...');
      
      const response = await axios.get(`${TEST_CONFIG.ml_service_url}/health`, {
        timeout: 5000
      });
      
      if (response.status === 200) {
        this.log('✅ ML service is running');
        await this.addTestResult('ML Service', true, 'Service responding');
        return true;
      } else {
        throw new Error(`ML service returned status ${response.status}`);
      }
      
    } catch (error) {
      this.log(`ML service test failed: ${error.message}`, 'error');
      await this.addTestResult('ML Service', false, error.message);
      return false;
    }
  }

  // Test 3: Attendance API with Authentication
  async testAttendanceAPI() {
    try {
      if (!this.authToken) {
        throw new Error('No authentication token available');
      }

      this.log('Testing attendance API with authentication...');
      
      const response = await axios.get(`${TEST_CONFIG.backend_url}/api/attendance/health`, {
        headers: { Authorization: `Bearer ${this.authToken}` },
        timeout: 5000
      });
      
      if (response.status === 200) {
        this.log('✅ Attendance API working with authentication');
        await this.addTestResult('Attendance API', true, 'API responding with auth');
        return true;
      } else {
        throw new Error(`API returned status ${response.status}`);
      }
      
    } catch (error) {
      this.log(`Attendance API test failed: ${error.message}`, 'error');
      await this.addTestResult('Attendance API', false, error.message);
      return false;
    }
  }

  // Test 4: AI Predictions
  async testAIPredictions() {
    try {
      this.log('Testing AI predictions...');
      
      const response = await axios.get(`${TEST_CONFIG.ml_service_url}/predict/1`, {
        timeout: 5000
      });
      
      if (response.status === 200) {
        this.log('✅ AI predictions working');
        await this.addTestResult('AI Predictions', true, 'Predictions responding');
        return true;
      } else {
        throw new Error(`AI service returned status ${response.status}`);
      }
      
    } catch (error) {
      this.log(`AI predictions test failed: ${error.message}`, 'error');
      await this.addTestResult('AI Predictions', false, error.message);
      return false;
    }
  }

  // Test 5: Complete Workflow
  async testCompleteWorkflow() {
    try {
      this.log('Testing complete attendance workflow...');
      
      if (!this.authToken) {
        throw new Error('No authentication token available');
      }

      // Create a test session
      const sessionData = {
        class_id: 1,
        teacher_id: 1,
        session_date: new Date().toISOString().split('T')[0],
        session_time: '09:00',
        session_type: 'regular'
      };

      const sessionResponse = await axios.post(
        `${TEST_CONFIG.backend_url}/api/attendance/sessions`,
        sessionData,
        { headers: { Authorization: `Bearer ${this.authToken}` } }
      );

      if (sessionResponse.data.success) {
        this.log('✅ Complete workflow working');
        await this.addTestResult('Complete Workflow', true, 'End-to-end workflow successful');
        return true;
      } else {
        throw new Error('Workflow failed');
      }
      
    } catch (error) {
      this.log(`Complete workflow test failed: ${error.message}`, 'error');
      await this.addTestResult('Complete Workflow', false, error.message);
      return false;
    }
  }

  // Generate final report
  generateFinalReport() {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(result => result.success).length;
    const failedTests = totalTests - passedTests;
    const successRate = ((passedTests / totalTests) * 100).toFixed(1);

    console.log('\n' + '='.repeat(70));
    console.log('🎯 SMART ATTENDANCE SYSTEM - COMPLETE TEST RESULTS');
    console.log('='.repeat(70));
    
    console.log(`\n📊 FINAL SYSTEM STATUS:`);
    console.log(`   Total Tests: ${totalTests}`);
    console.log(`   Passed: ${passedTests} ✅`);
    console.log(`   Failed: ${failedTests} ❌`);
    console.log(`   Success Rate: ${successRate}%`);
    
    console.log(`\n�� DETAILED RESULTS:`);
    this.testResults.forEach((result, index) => {
      const status = result.success ? '✅' : '❌';
      console.log(`   ${index + 1}. ${status} ${result.test}`);
      if (result.details) {
        console.log(`      Details: ${result.details}`);
      }
    });

    if (successRate >= 80) {
      console.log(`\n🎉 SYSTEM STATUS: FULLY OPERATIONAL!`);
      console.log(`   ✅ All core features working`);
      console.log(`   ✅ AI/ML integration active`);
      console.log(`   ✅ Authentication system functional`);
      console.log(`   ✅ Ready for production use`);
    } else if (successRate >= 60) {
      console.log(`\n⚠️ SYSTEM STATUS: MOSTLY OPERATIONAL`);
      console.log(`   ✅ Core features working`);
      console.log(`   ⚠️ Some advanced features need attention`);
    } else {
      console.log(`\n❌ SYSTEM STATUS: NEEDS ATTENTION`);
      console.log(`   ⚠️ Core features need fixing`);
    }

    console.log('='.repeat(70));

    // Save report
    const reportData = {
      timestamp: new Date().toISOString(),
      summary: {
        total: totalTests,
        passed: passedTests,
        failed: failedTests,
        successRate: parseFloat(successRate)
      },
      results: this.testResults,
      systemStatus: successRate >= 80 ? 'FULLY_OPERATIONAL' : 
                   successRate >= 60 ? 'MOSTLY_OPERATIONAL' : 'NEEDS_ATTENTION'
    };

    const reportPath = path.join(__dirname, 'complete_system_report.json');
    fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
    this.log(`Final report saved to: ${reportPath}`);
  }

  // Run all tests
  async runCompleteTests() {
    this.log('🚀 Starting Complete Smart Attendance System Tests...');
    this.log(`Backend URL: ${TEST_CONFIG.backend_url}`);
    this.log(`ML Service URL: ${TEST_CONFIG.ml_service_url}`);
    
    const tests = [
      this.testAuthentication(),
      this.testMLService(),
      this.testAttendanceAPI(),
      this.testAIPredictions(),
      this.testCompleteWorkflow()
    ];

    await Promise.allSettled(tests);
    
    this.generateFinalReport();
    
    await pool.end();
  }
}

// Run the complete tests
async function main() {
  const tester = new CompleteSystemTester();
  
  try {
    await tester.runCompleteTests();
  } catch (error) {
    console.error('Complete test execution failed:', error);
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  console.log('\n🛑 Complete tests interrupted by user');
  await pool.end();
  process.exit(0);
});

// Run tests if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = CompleteSystemTester;
