const express = require('express');
const router = express.Router();
const DashboardController = require('../controllers/DashboardController');

// Dashboard Data API Routes
router.get('/teacher/:teacherId', DashboardController.getTeacherDashboardData);    // Teacher dashboard data
router.get('/admin/:schoolId', DashboardController.getAdminDashboardData);         // Admin dashboard data
router.get('/student/:studentId', DashboardController.getStudentDashboardData);    // Student dashboard data
router.get('/parent/:parentId', DashboardController.getParentDashboardData);       // Parent dashboard data

// Real-time Dashboard Updates
router.get('/updates/:userType/:userId', DashboardController.getDashboardUpdates); // Real-time updates

module.exports = router;
