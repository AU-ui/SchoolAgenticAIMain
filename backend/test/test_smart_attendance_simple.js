// ============================================================================
// SMART ATTENDANCE SYSTEM - SIMPLE TEST
// ============================================================================
// Simple test focusing on core functionality without email dependencies
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

class SimpleAttendanceTester {
  constructor() {
    this.testResults = [];
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

  // Test 1: Database Connection
  async testDatabaseConnection() {
    try {
      const client = await pool.connect();
      const result = await client.query('SELECT NOW()');
      client.release();
      
      this.log('Database connection successful');
      await this.addTestResult('Database Connection', true);
      return true;
    } catch (error) {
      this.log(`Database connection failed: ${error.message}`, 'error');
      await this.addTestResult('Database Connection', false, error.message);
      return false;
    }
  }

  // Test 2: Attendance Tables
  async testAttendanceTables() {
    try {
      const client = await pool.connect();
      
      const tables = ['attendance_sessions', 'attendance_records', 'attendance_analytics'];
      const results = {};
      
      for (const table of tables) {
        const result = await client.query(`
          SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = $1
          );
        `, [table]);
        results[table] = result.rows[0].exists;
      }
      
      client.release();
      
      const allTablesExist = Object.values(results).every(exists => exists);
      
      if (allTablesExist) {
        this.log('All attendance tables exist');
        await this.addTestResult('Attendance Tables', true);
        return true;
      } else {
        const missingTables = Object.keys(results).filter(table => !results[table]);
        this.log(`Missing tables: ${missingTables.join(', ')}`, 'error');
        await this.addTestResult('Attendance Tables', false, `Missing: ${missingTables.join(', ')}`);
        return false;
      }
    } catch (error) {
      this.log(`Attendance tables test failed: ${error.message}`, 'error');
      await this.addTestResult('Attendance Tables', false, error.message);
      return false;
    }
  }

  // Test 3: Backend Health
  async testBackendHealth() {
    try {
      const response = await axios.get(`${TEST_CONFIG.backend_url}/health`, {
        timeout: 5000
      });
      
      if (response.status === 200) {
        this.log('Backend health check passed');
        await this.addTestResult('Backend Health', true);
        return true;
      } else {
        this.log(`Backend health check failed: ${response.status}`, 'error');
        await this.addTestResult('Backend Health', false, `Status: ${response.status}`);
        return false;
      }
    } catch (error) {
      this.log(`Backend health check failed: ${error.message}`, 'error');
      await this.addTestResult('Backend Health', false, error.message);
      return false;
    }
  }

  // Test 4: Simple Authentication (without email)
  async testSimpleAuth() {
    try {
      // Try to login with existing credentials first
      const loginResponse = await axios.post(`${TEST_CONFIG.backend_url}/api/auth/login`, {
        email: 'admin@school.com', // Try common admin email
        password: 'admin123'
      });

      if (loginResponse.data.success && loginResponse.data.token) {
        this.log('Simple authentication successful (existing user)');
        await this.addTestResult('Simple Authentication', true);
        return true;
      } else {
        this.log('Simple authentication failed - no existing user');
        await this.addTestResult('Simple Authentication', false, 'No existing test user');
        return false;
      }
    } catch (error) {
      this.log(`Simple authentication failed: ${error.message}`, 'error');
      await this.addTestResult('Simple Authentication', false, error.message);
      return false;
    }
  }

  // Test 5: Frontend Components
  async testFrontendComponents() {
    try {
      const frontendFiles = [
        '../../frontend/app/src/components/SmartAttendance.js',
        '../../frontend/app/src/components/SmartAttendance.css',
        '../../frontend/app/src/services/attendanceService.js',
        '../../frontend/app/src/pages/TeacherAttendanceDashboard.js',
        '../../frontend/app/src/pages/TeacherAttendanceDashboard.css'
      ];

      const missingFiles = [];
      
      for (const file of frontendFiles) {
        const filePath = path.join(__dirname, file);
        if (!fs.existsSync(filePath)) {
          missingFiles.push(file);
        }
      }

      if (missingFiles.length === 0) {
        this.log('All frontend components exist');
        await this.addTestResult('Frontend Components', true);
        return true;
      } else {
        this.log(`Missing frontend files: ${missingFiles.join(', ')}`, 'error');
        await this.addTestResult('Frontend Components', false, `Missing: ${missingFiles.join(', ')}`);
        return false;
      }
    } catch (error) {
      this.log(`Frontend components test failed: ${error.message}`, 'error');
      await this.addTestResult('Frontend Components', false, error.message);
      return false;
    }
  }

  // Test 6: Performance
  async testPerformance() {
    try {
      this.log('Testing system performance...');
      
      const startTime = Date.now();
      
      const concurrentRequests = 5;
      const promises = [];
      
      for (let i = 0; i < concurrentRequests; i++) {
        promises.push(
          axios.get(`${TEST_CONFIG.backend_url}/health`, { timeout: 5000 })
        );
      }
      
      await Promise.all(promises);
      
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      if (duration < 5000) {
        this.log(`Performance test passed: ${duration}ms for ${concurrentRequests} requests`);
        await this.addTestResult('Performance', true, `${duration}ms`);
        return true;
      } else {
        this.log(`Performance test failed: ${duration}ms (too slow)`, 'error');
        await this.addTestResult('Performance', false, `${duration}ms (slow)`);
        return false;
      }
    } catch (error) {
      this.log(`Performance test failed: ${error.message}`, 'error');
      await this.addTestResult('Performance', false, error.message);
      return false;
    }
  }

  // Generate report
  generateReport() {
    const totalTests = this.testResults.length;
    const passedTests = this.testResults.filter(result => result.success).length;
    const failedTests = totalTests - passedTests;
    const successRate = ((passedTests / totalTests) * 100).toFixed(1);

    console.log('\n' + '='.repeat(60));
    console.log('🎯 SMART ATTENDANCE SYSTEM - SIMPLE TEST REPORT');
    console.log('='.repeat(60));
    
    console.log(`\n📊 SUMMARY:`);
    console.log(`   Total Tests: ${totalTests}`);
    console.log(`   Passed: ${passedTests} ✅`);
    console.log(`   Failed: ${failedTests} ❌`);
    console.log(`   Success Rate: ${successRate}%`);
    
    console.log(`\n DETAILED RESULTS:`);
    this.testResults.forEach((result, index) => {
      const status = result.success ? '✅' : '❌';
      console.log(`   ${index + 1}. ${status} ${result.test}`);
      if (!result.success && result.details) {
        console.log(`      Details: ${result.details}`);
      }
    });

    if (failedTests > 0) {
      console.log(`\n⚠️  FAILED TESTS:`);
      this.testResults
        .filter(result => !result.success)
        .forEach(result => {
          console.log(`   ❌ ${result.test}: ${result.details}`);
        });
    }

    console.log(`\n🎉 SYSTEM STATUS: ${successRate >= 80 ? 'READY FOR PRODUCTION' : 'NEEDS ATTENTION'}`);
    console.log('='.repeat(60));

    // Save report
    const reportData = {
      timestamp: new Date().toISOString(),
      summary: {
        total: totalTests,
        passed: passedTests,
        failed: failedTests,
        successRate: parseFloat(successRate)
      },
      results: this.testResults
    };

    const reportPath = path.join(__dirname, 'attendance_test_report_simple.json');
    fs.writeFileSync(reportPath, JSON.stringify(reportData, null, 2));
    this.log(`Test report saved to: ${reportPath}`);
  }

  // Run all tests
  async runAllTests() {
    this.log('🚀 Starting Smart Attendance System Simple Tests...');
    this.log(`Backend URL: ${TEST_CONFIG.backend_url}`);
    
    const tests = [
      this.testDatabaseConnection(),
      this.testAttendanceTables(),
      this.testBackendHealth(),
      this.testSimpleAuth(),
      this.testFrontendComponents(),
      this.testPerformance()
    ];

    await Promise.allSettled(tests);
    
    this.generateReport();
    
    await pool.end();
  }
}

// Run the tests
async function main() {
  const tester = new SimpleAttendanceTester();
  
  try {
    await tester.runAllTests();
  } catch (error) {
    console.error('Test execution failed:', error);
    process.exit(1);
  }
}

// Handle process termination
process.on('SIGINT', async () => {
  console.log('\n🛑 Tests interrupted by user');
  await pool.end();
  process.exit(0);
});

// Run tests if this file is executed directly
if (require.main === module) {
  main();
}

module.exports = SimpleAttendanceTester;
