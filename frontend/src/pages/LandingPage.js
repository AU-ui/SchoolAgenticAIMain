import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const [schools, setSchools] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch schools and stats in parallel
      const [schoolsResponse, statsResponse] = await Promise.all([
        fetch('http://localhost:5000/api/landing/schools'),
        fetch('http://localhost:5000/api/landing/stats')
      ]);

      if (schoolsResponse.ok && statsResponse.ok) {
        const schoolsData = await schoolsResponse.json();
        const statsData = await statsResponse.json();
        
        setSchools(schoolsData.data.schools);
        setStats(statsData.data.stats);
      } else {
        throw new Error('Failed to fetch data');
      }
    } catch (err) {
      setError('Failed to load data. Please try again later.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
      const response = await fetch('http://localhost:5000/api/landing/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.get('name'),
          email: formData.get('email'),
          phone: formData.get('phone'),
          message: formData.get('message')
        })
      });

      if (response.ok) {
        alert('Thank you for your message! We will get back to you soon.');
        e.target.reset();
      } else {
        alert('Failed to send message. Please try again.');
      }
    } catch (err) {
      alert('Failed to send message. Please try again.');
      console.error('Error sending contact form:', err);
    }
  };

  if (loading) {
    return (
      <div className="landing-page">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="landing-page">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="landing-page">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="logo">
            <h1>EdTech Platform</h1>
          </div>
          <nav className="nav">
            <Link to="/signup" className="btn btn-primary">Sign Up</Link>
            <Link to="/login" className="btn btn-secondary">Login</Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>Transform Education with Smart Technology</h1>
            <p>Empowering schools, teachers, parents, and students with innovative digital solutions for better learning outcomes.</p>
            <div className="hero-buttons">
              <Link to="/signup" className="btn btn-primary btn-large">Get Started</Link>
              <Link to="/login" className="btn btn-outline btn-large">Sign In</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats">
        <div className="container">
          <h2>Platform Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <h3>{stats.totalSchools || 0}</h3>
              <p>Schools</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalUsers || 0}</h3>
              <p>Users</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalTeachers || 0}</h3>
              <p>Teachers</p>
            </div>
            <div className="stat-card">
              <h3>{stats.totalStudents || 0}</h3>
              <p>Students</p>
            </div>
          </div>
        </div>
      </section>

      {/* Schools Section */}
      <section className="schools">
        <div className="container">
          <h2>Featured Schools</h2>
          <div className="schools-grid">
            {schools.map(school => (
              <div key={school.id} className="school-card">
                {school.logoUrl && (
                  <div className="school-logo">
                    <img src={school.logoUrl} alt={`${school.name} logo`} />
                  </div>
                )}
                <div className="school-info">
                  <h3>{school.name}</h3>
                  <p className="school-address">{school.address}</p>
                  <p className="school-contact">
                    📧 {school.email} | 📞 {school.phone}
                  </p>
                  <div className="school-stats">
                    <span>🏫 {school.schoolCount} campuses</span>
                    <span>👥 {school.userCount} users</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="contact">
        <div className="container">
          <h2>Get in Touch</h2>
          <div className="contact-content">
            <div className="contact-info">
              <h3>Ready to Transform Your School?</h3>
              <p>Join thousands of schools already using our platform to improve education outcomes.</p>
              <div className="contact-details">
                <p>📧 info@edtechplatform.com</p>
                <p>📞 +1 (555) 123-4567</p>
                <p>📍 123 Education Street, Tech City</p>
              </div>
            </div>
            <form className="contact-form" onSubmit={handleContactSubmit}>
              <div className="form-group">
                <input
                  type="text"
                  name="name"
                  placeholder="Your Name"
                  required
                />
              </div>
              <div className="form-group">
                <input
                  type="email"
                  name="email"
                  placeholder="Your Email"
                  required
                />
              </div>
              <div className="form-group">
                <input
                  type="tel"
                  name="phone"
                  placeholder="Your Phone"
                />
              </div>
              <div className="form-group">
                <textarea
                  name="message"
                  placeholder="Your Message"
                  rows="4"
                  required
                ></textarea>
              </div>
              <button type="submit" className="btn btn-primary">Send Message</button>
            </form>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3>EdTech Platform</h3>
              <p>Empowering education through technology</p>
            </div>
            <div className="footer-section">
              <h4>Quick Links</h4>
              <ul>
                <li><Link to="/signup">Sign Up</Link></li>
                <li><Link to="/login">Login</Link></li>
                <li><a href="#contact">Contact</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Features</h4>
              <ul>
                <li>Smart Attendance</li>
                <li>AI Reports</li>
                <li>Parent Communication</li>
                <li>Task Management</li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2024 EdTech Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage; 