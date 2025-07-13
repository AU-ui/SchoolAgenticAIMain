const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const router = express.Router();

// GET /api/parent/dashboard
router.get('/dashboard', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    
    // Get parent's children and their stats
    const dashboardQuery = `
      SELECT 
        s.id as student_id,
        s.first_name,
        s.last_name,
        s.grade_level,
        s.class_id,
        c.name as class_name,
        COUNT(DISTINCT ar.id) as total_attendance,
        COUNT(DISTINCT CASE WHEN ar.status = 'present' THEN ar.id END) as present_days,
        COUNT(DISTINCT a.id) as total_assignments,
        COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) as completed_assignments
      FROM students s
      LEFT JOIN classes c ON s.class_id = c.id
      LEFT JOIN attendance_records ar ON s.id = ar.student_id
      LEFT JOIN assignments a ON s.id = a.student_id
      WHERE s.parent_id = $1 AND s.tenant_id = $2
      GROUP BY s.id, s.first_name, s.last_name, s.grade_level, s.class_id, c.name
    `;
    
    const result = await query(dashboardQuery, [parentId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching parent dashboard:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load dashboard data'
    });
  }
});

// GET /api/parent/communications
router.get('/communications', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    
    const communicationsQuery = `
      SELECT 
        c.id,
        c.title,
        c.message,
        c.type,
        c.priority,
        c.created_at,
        c.sender_id,
        u.first_name as sender_name,
        c.is_read,
        c.language,
        c.translated_message
      FROM communications c
      LEFT JOIN users u ON c.sender_id = u.id
      WHERE c.recipient_id = $1 AND c.tenant_id = $2
      ORDER BY c.created_at DESC
    `;
    
    const result = await query(communicationsQuery, [parentId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching communications:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load communications'
    });
  }
});

// POST /api/parent/communications
router.post('/communications', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    const { recipient_id, title, message, type, priority, language } = req.body;
    
    const insertQuery = `
      INSERT INTO communications (
        sender_id, recipient_id, title, message, type, priority, 
        language, tenant_id, created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
      RETURNING id
    `;
    
    const result = await query(insertQuery, [
      parentId, recipient_id, title, message, type, priority, language, tenantId
    ]);
    
    res.json({
      success: true,
      data: { id: result.rows[0].id }
    });
  } catch (error) {
    console.error('Error creating communication:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to send message'
    });
  }
});

// PUT /api/parent/communications/:id/read
router.put('/communications/:id/read', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId } = req.user;
    const { id: communicationId } = req.params;
    
    const updateQuery = `
      UPDATE communications 
      SET is_read = true, read_at = NOW()
      WHERE id = $1 AND recipient_id = $2
    `;
    
    await query(updateQuery, [communicationId, parentId]);
    
    res.json({
      success: true,
      message: 'Message marked as read'
    });
  } catch (error) {
    console.error('Error marking communication as read:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to mark message as read'
    });
  }
});

// GET /api/parent/notifications
router.get('/notifications', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    
    const notificationsQuery = `
      SELECT 
        n.id,
        n.title,
        n.message,
        n.type,
        n.priority,
        n.created_at,
        n.is_read,
        n.related_student_id,
        s.first_name as student_name
      FROM notifications n
      LEFT JOIN students s ON n.related_student_id = s.id
      WHERE n.recipient_id = $1 AND n.tenant_id = $2
      ORDER BY n.created_at DESC
    `;
    
    const result = await query(notificationsQuery, [parentId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching notifications:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load notifications'
    });
  }
});

// PUT /api/parent/notifications/:id/read
router.put('/notifications/:id/read', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId } = req.user;
    const { id: notificationId } = req.params;
    
    const updateQuery = `
      UPDATE notifications 
      SET is_read = true, read_at = NOW()
      WHERE id = $1 AND recipient_id = $2
    `;
    
    await query(updateQuery, [notificationId, parentId]);
    
    res.json({
      success: true,
      message: 'Notification marked as read'
    });
  } catch (error) {
    console.error('Error marking notification as read:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to mark notification as read'
    });
  }
});

// GET /api/parent/progress/:studentId
router.get('/progress/:studentId', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    const { studentId } = req.params;
    
    // Verify parent has access to this student
    const accessQuery = `
      SELECT id FROM students 
      WHERE id = $1 AND parent_id = $2 AND tenant_id = $3
    `;
    const accessResult = await query(accessQuery, [studentId, parentId, tenantId]);
    
    if (accessResult.rows.length === 0) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    // Get student progress data
    const progressQuery = `
      SELECT 
        s.first_name,
        s.last_name,
        s.grade_level,
        c.name as class_name,
        COUNT(DISTINCT ar.id) as total_attendance,
        COUNT(DISTINCT CASE WHEN ar.status = 'present' THEN ar.id END) as present_days,
        COUNT(DISTINCT a.id) as total_assignments,
        COUNT(DISTINCT CASE WHEN a.status = 'completed' THEN a.id END) as completed_assignments,
        AVG(a.grade) as average_grade
      FROM students s
      LEFT JOIN classes c ON s.class_id = c.id
      LEFT JOIN attendance_records ar ON s.id = ar.student_id
      LEFT JOIN assignments a ON s.id = a.student_id
      WHERE s.id = $1
      GROUP BY s.id, s.first_name, s.last_name, s.grade_level, c.name
    `;
    
    const result = await query(progressQuery, [studentId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Student not found'
      });
    }
    
    res.json({
      success: true,
      data: result.rows[0]
    });
  } catch (error) {
    console.error('Error fetching student progress:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load progress data'
    });
  }
});

// GET /api/parent/fees
router.get('/fees', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    
    const feesQuery = `
      SELECT 
        f.id,
        f.student_id,
        s.first_name,
        s.last_name,
        f.fee_type,
        f.amount,
        f.due_date,
        f.status,
        f.payment_method,
        f.payment_date,
        f.description
      FROM fees f
      JOIN students s ON f.student_id = s.id
      WHERE s.parent_id = $1 AND f.tenant_id = $2
      ORDER BY f.due_date DESC
    `;
    
    const result = await query(feesQuery, [parentId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching fees:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load fees'
    });
  }
});

// POST /api/parent/fees/:id/pay
router.post('/fees/:id/pay', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId } = req.user;
    const { id: feeId } = req.params;
    const { payment_method, transaction_id } = req.body;
    
    // Verify parent has access to this fee
    const accessQuery = `
      SELECT f.id FROM fees f
      JOIN students s ON f.student_id = s.id
      WHERE f.id = $1 AND s.parent_id = $2
    `;
    const accessResult = await query(accessQuery, [feeId, parentId]);
    
    if (accessResult.rows.length === 0) {
      return res.status(403).json({
        success: false,
        message: 'Access denied'
      });
    }
    
    const updateQuery = `
      UPDATE fees 
      SET status = 'paid', payment_method = $1, payment_date = NOW(), transaction_id = $2
      WHERE id = $3
    `;
    
    await query(updateQuery, [payment_method, transaction_id, feeId]);
    
    res.json({
      success: true,
      message: 'Payment processed successfully'
    });
  } catch (error) {
    console.error('Error processing payment:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to process payment'
    });
  }
});

// GET /api/parent/events
router.get('/events', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    
    const eventsQuery = `
      SELECT 
        e.id,
        e.title,
        e.description,
        e.type,
        e.date,
        e.time,
        e.location,
        e.capacity,
        e.registered_count,
        e.registration_deadline,
        e.requirements,
        e.additional_info,
        e.organizer,
        e.created_at,
        CASE WHEN er.parent_id IS NOT NULL THEN true ELSE false END as is_registered
      FROM events e
      LEFT JOIN event_registrations er ON e.id = er.event_id AND er.parent_id = $1
      WHERE e.tenant_id = $2 AND e.date >= CURRENT_DATE
      ORDER BY e.date ASC
    `;
    
    const result = await query(eventsQuery, [parentId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching events:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load events'
    });
  }
});

// POST /api/parent/events/:id/register
router.post('/events/:id/register', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId } = req.user;
    const { id: eventId } = req.params;
    
    // Check if event exists and has capacity
    const eventQuery = `
      SELECT id, capacity, registered_count FROM events WHERE id = $1
    `;
    const eventResult = await query(eventQuery, [eventId]);
    
    if (eventResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Event not found'
      });
    }
    
    const event = eventResult.rows[0];
    if (event.capacity && event.registered_count >= event.capacity) {
      return res.status(400).json({
        success: false,
        message: 'Event is full'
      });
    }
    
    // Check if already registered
    const existingQuery = `
      SELECT id FROM event_registrations WHERE event_id = $1 AND parent_id = $2
    `;
    const existingResult = await query(existingQuery, [eventId, parentId]);
    
    if (existingResult.rows.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Already registered for this event'
      });
    }
    
    // Register for event
    const registerQuery = `
      INSERT INTO event_registrations (event_id, parent_id, registered_at)
      VALUES ($1, $2, NOW())
    `;
    
    await query(registerQuery, [eventId, parentId]);
    
    // Update event registration count
    const updateQuery = `
      UPDATE events SET registered_count = registered_count + 1 WHERE id = $1
    `;
    
    await query(updateQuery, [eventId]);
    
    res.json({
      success: true,
      message: 'Successfully registered for event'
    });
  } catch (error) {
    console.error('Error registering for event:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to register for event'
    });
  }
});

// DELETE /api/parent/events/:id/register
router.delete('/events/:id/register', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId } = req.user;
    const { id: eventId } = req.params;
    
    // Remove registration
    const deleteQuery = `
      DELETE FROM event_registrations WHERE event_id = $1 AND parent_id = $2
    `;
    
    const result = await query(deleteQuery, [eventId, parentId]);
    
    if (result.rowCount === 0) {
      return res.status(404).json({
        success: false,
        message: 'Registration not found'
      });
    }
    
    // Update event registration count
    const updateQuery = `
      UPDATE events SET registered_count = registered_count - 1 WHERE id = $1
    `;
    
    await query(updateQuery, [eventId]);
    
    res.json({
      success: true,
      message: 'Successfully unregistered from event'
    });
  } catch (error) {
    console.error('Error unregistering from event:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to unregister from event'
    });
  }
});

// GET /api/parent/emergencies
router.get('/emergencies', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId, tenantId } = req.user;
    
    const emergenciesQuery = `
      SELECT 
        e.id,
        e.title,
        e.message,
        e.priority,
        e.affected_area,
        e.contact_info,
        e.instructions,
        e.additional_info,
        e.created_at,
        CASE WHEN ea.parent_id IS NOT NULL THEN true ELSE false END as is_acknowledged
      FROM emergencies e
      LEFT JOIN emergency_acknowledgments ea ON e.id = ea.emergency_id AND ea.parent_id = $1
      WHERE e.tenant_id = $2 AND e.is_active = true
      ORDER BY e.created_at DESC
    `;
    
    const result = await query(emergenciesQuery, [parentId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching emergencies:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load emergency communications'
    });
  }
});

// POST /api/parent/emergencies/:id/acknowledge
router.post('/emergencies/:id/acknowledge', authenticateToken, requireRole(['parent']), async (req, res) => {
  try {
    const { id: parentId } = req.user;
    const { id: emergencyId } = req.params;
    
    // Check if already acknowledged
    const existingQuery = `
      SELECT id FROM emergency_acknowledgments WHERE emergency_id = $1 AND parent_id = $2
    `;
    const existingResult = await query(existingQuery, [emergencyId, parentId]);
    
    if (existingResult.rows.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Already acknowledged'
      });
    }
    
    // Acknowledge emergency
    const acknowledgeQuery = `
      INSERT INTO emergency_acknowledgments (emergency_id, parent_id, acknowledged_at)
      VALUES ($1, $2, NOW())
    `;
    
    await query(acknowledgeQuery, [emergencyId, parentId]);
    
    res.json({
      success: true,
      message: 'Emergency acknowledged'
    });
  } catch (error) {
    console.error('Error acknowledging emergency:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to acknowledge emergency'
    });
  }
});

module.exports = router; 