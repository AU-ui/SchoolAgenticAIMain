const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../../middleware/auth');
const { query } = require('../../config/database');

// Get ML insights for a class
router.get('/insights/:classId', authenticateToken, async (req, res) => {
  try {
    const { classId } = req.params;
    const teacherId = req.user.id;

    // Verify teacher owns this class
    const classCheck = await query(
      'SELECT id FROM classes WHERE id = $1 AND teacher_id = $2 AND is_active = true',
      [classId, teacherId]
    );

    if (classCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        message: 'You do not have permission to access this class'
      });
    }

    // Get attendance data for analysis
    const attendanceData = await query(`
      SELECT 
        DATE(a.created_at) as date,
        COUNT(*) as total_students,
        COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
        COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent_count,
        COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_count
      FROM attendance_records a
      JOIN students s ON a.student_id = s.id
      WHERE s.class_id = $1 AND a.created_at >= NOW() - INTERVAL '30 days'
      GROUP BY DATE(a.created_at)
      ORDER BY date
    `, [classId]);

    // Get grade data for analysis
    const gradeData = await query(`
      SELECT 
        sg.score,
        sg.max_score,
        sg.grade_letter,
        a.assignment_type
      FROM student_grades sg
      JOIN assignments a ON sg.assignment_id = a.id
      JOIN students s ON sg.student_id = s.id
      WHERE s.class_id = $1 AND sg.score IS NOT NULL
    `, [classId]);

    // Generate ML insights
    const insights = generateInsights(attendanceData.rows, gradeData.rows);

    res.json({
      success: true,
      data: {
        insights: insights
      }
    });
  } catch (error) {
    console.error('Error generating ML insights:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to generate insights'
    });
  }
});

// Generate AI report
router.post('/generate-report', authenticateToken, async (req, res) => {
  try {
    const { classId, templateId, dateRange, includeInsights, includePredictions } = req.body;
    const teacherId = req.user.id;

    // Verify teacher owns this class
    const classCheck = await query(
      'SELECT id, name FROM classes WHERE id = $1 AND teacher_id = $2 AND is_active = true',
      [classId, teacherId]
    );

    if (classCheck.rows.length === 0) {
      return res.status(403).json({
        success: false,
        message: 'You do not have permission to access this class'
      });
    }

    // Get template
    const templateResult = await query(
      'SELECT * FROM report_templates WHERE id = $1 AND is_active = true',
      [templateId]
    );

    if (templateResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Report template not found'
      });
    }

    const template = templateResult.rows[0];
    const className = classCheck.rows[0].name;

    // Generate report data
    const reportData = await generateReportData(classId, dateRange, includeInsights, includePredictions);

    // Create report record
    const reportResult = await query(`
      INSERT INTO generated_reports (template_id, teacher_id, class_id, report_data, generated_at)
      VALUES ($1, $2, $3, $4, NOW())
      RETURNING id
    `, [templateId, teacherId, classId, JSON.stringify(reportData)]);

    const reportId = reportResult.rows[0].id;

    // Generate report file (CSV/PDF)
    const reportUrl = await generateReportFile(reportData, className, template);

    res.json({
      success: true,
      data: {
        reportId: reportId,
        reportUrl: reportUrl,
        message: 'Report generated successfully'
      }
    });
  } catch (error) {
    console.error('Error generating report:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to generate report'
    });
  }
});

// Helper function to generate insights
function generateInsights(attendanceData, gradeData) {
  const insights = {
    attendanceTrends: [],
    performancePredictions: [],
    studentEngagement: [],
    recommendations: []
  };

  // Analyze attendance trends
  if (attendanceData.length > 0) {
    const totalDays = attendanceData.length;
    const avgAttendance = attendanceData.reduce((sum, day) => 
      sum + (day.present_count / day.total_students), 0) / totalDays;

    if (avgAttendance > 0.9) {
      insights.attendanceTrends.push({
        type: 'positive',
        description: 'Excellent attendance rate of ' + Math.round(avgAttendance * 100) + '%'
      });
    } else if (avgAttendance < 0.8) {
      insights.attendanceTrends.push({
        type: 'warning',
        description: 'Low attendance rate of ' + Math.round(avgAttendance * 100) + '% - consider intervention'
      });
    } else {
      insights.attendanceTrends.push({
        type: 'neutral',
        description: 'Good attendance rate of ' + Math.round(avgAttendance * 100) + '%'
      });
    }
  }

  // Analyze performance predictions
  if (gradeData.length > 0) {
    const avgGrade = gradeData.reduce((sum, grade) => 
      sum + (grade.score / grade.max_score), 0) / gradeData.length;

    if (avgGrade > 0.85) {
      insights.performancePredictions.push({
        type: 'positive',
        description: 'Strong academic performance predicted - students are on track for success'
      });
    } else if (avgGrade < 0.7) {
      insights.performancePredictions.push({
        type: 'warning',
        description: 'Performance below target - consider additional support strategies'
      });
    }
  }

  // Generate recommendations
  if (attendanceData.length > 0 && gradeData.length > 0) {
    const avgAttendance = attendanceData.reduce((sum, day) => 
      sum + (day.present_count / day.total_students), 0) / attendanceData.length;
    const avgGrade = gradeData.reduce((sum, grade) => 
      sum + (grade.score / grade.max_score), 0) / gradeData.length;

    if (avgAttendance < 0.8 && avgGrade < 0.75) {
      insights.recommendations.push({
        priority: 'high',
        description: 'Implement attendance improvement program and academic support'
      });
    } else if (avgAttendance < 0.8) {
      insights.recommendations.push({
        priority: 'medium',
        description: 'Focus on improving attendance through engagement strategies'
      });
    } else if (avgGrade < 0.75) {
      insights.recommendations.push({
        priority: 'medium',
        description: 'Provide additional academic support and tutoring resources'
      });
    } else {
      insights.recommendations.push({
        priority: 'low',
        description: 'Maintain current successful strategies'
      });
    }
  }

  return insights;
}

// Helper function to generate report data
async function generateReportData(classId, dateRange, includeInsights, includePredictions) {
  const reportData = {
    classInfo: {},
    attendance: {},
    grades: {},
    insights: includeInsights ? {} : null,
    predictions: includePredictions ? {} : null
  };

  // Get class information
  const classInfo = await query(`
    SELECT c.name, c.grade_level, COUNT(s.id) as student_count
    FROM classes c
    LEFT JOIN students s ON c.id = s.class_id
    WHERE c.id = $1
    GROUP BY c.id, c.name, c.grade_level
  `, [classId]);

  if (classInfo.rows.length > 0) {
    reportData.classInfo = classInfo.rows[0];
  }

  // Get attendance data
  const attendanceData = await query(`
    SELECT 
      DATE(a.created_at) as date,
      COUNT(*) as total_records,
      COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_count,
      COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent_count,
      COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_count
    FROM attendance_records a
    JOIN students s ON a.student_id = s.id
    WHERE s.class_id = $1 AND a.created_at >= NOW() - INTERVAL '1 $2'
    GROUP BY DATE(a.created_at)
    ORDER BY date
  `, [classId, dateRange]);

  reportData.attendance = {
    totalDays: attendanceData.rows.length,
    records: attendanceData.rows
  };

  // Get grade data
  const gradeData = await query(`
    SELECT 
      a.title,
      a.assignment_type,
      AVG(sg.score::float / sg.max_score) as avg_percentage,
      COUNT(sg.id) as total_submissions
    FROM assignments a
    LEFT JOIN student_grades sg ON a.id = sg.assignment_id
    JOIN students s ON sg.student_id = s.id
    WHERE s.class_id = $1
    GROUP BY a.id, a.title, a.assignment_type
    ORDER BY a.created_at DESC
  `, [classId]);

  reportData.grades = {
    totalAssignments: gradeData.rows.length,
    assignments: gradeData.rows
  };

  return reportData;
}

// Helper function to generate report file
async function generateReportFile(reportData, className, template) {
  // This would typically generate a CSV or PDF file
  // For now, we'll return a mock URL
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `${className}_report_${timestamp}.csv`;
  
  return {
    filename: filename,
    url: `/reports/${filename}`,
    size: '2.5KB'
  };
}

module.exports = router; 