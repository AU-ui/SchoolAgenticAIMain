import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        // Store token and user data
        localStorage.setItem('token', data.data.token);
        localStorage.setItem('user', JSON.stringify(data.data.user));
        
        // Show welcome message
        const user = data.data.user;
        alert(`Welcome back, ${user.firstName} ${user.lastName}!`);
        
        // Navigate based on role
        switch (user.role) {
          case 'superadmin':
          case 'admin':
            navigate('/admin-dashboard');
            break;
          case 'teacher':
            navigate('/teacher-dashboard');
            break;
          case 'parent':
            navigate('/parent-dashboard');
            break;
          case 'student':
            navigate('/student-dashboard');
            break;
          default:
            navigate('/dashboard');
        }
      } else {
        setErrors({ submit: data.message || 'Login failed. Please check your credentials.' });
      }
    } catch (error) {
      console.error('Login error:', error);
      setErrors({ submit: 'Network error. Please check your connection.' });
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role) => {
    setLoading(true);
    
    const demoCredentials = {
      superadmin: { email: 'superadmin@edtech.com', password: 'admin123' },
      teacher: { email: 'teacher@demo.edu', password: 'teacher123' },
      parent: { email: 'parent@demo.edu', password: 'parent123' },
      student: { email: 'student@demo.edu', password: 'student123' }
    };

    const credentials = demoCredentials[role];
    if (!credentials) {
      setLoading(false);
      return;
    }

    setFormData(credentials);
    
    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.data.token);
        localStorage.setItem('user', JSON.stringify(data.data.user));
        
        const user = data.data.user;
        alert(`Welcome to demo mode, ${user.firstName} ${user.lastName}!`);
        navigate('/dashboard');
      } else {
        setErrors({ submit: 'Demo login failed. Please try regular login.' });
      }
    } catch (error) {
      console.error('Demo login error:', error);
      setErrors({ submit: 'Demo login failed. Please try regular login.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <Link to="/" className="logo">
            <h1>EdTech Platform</h1>
          </Link>
          <p>Welcome back! Please sign in to your account.</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {errors.submit && (
            <div className="error-message">
              {errors.submit}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={errors.email ? 'error' : ''}
              placeholder="Enter your email address"
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <div className="password-input">
              <input
                type={showPassword ? 'text' : 'password'}
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={errors.password ? 'error' : ''}
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            {errors.password && <span className="error-text">{errors.password}</span>}
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-large"
            disabled={loading}
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Login Section */}
        <div className="demo-section">
          <h3>Try Demo Accounts</h3>
          <div className="demo-buttons">
            <button
              type="button"
              className="btn btn-demo"
              onClick={() => handleDemoLogin('superadmin')}
              disabled={loading}
            >
              👑 Super Admin
            </button>
            <button
              type="button"
              className="btn btn-demo"
              onClick={() => handleDemoLogin('teacher')}
              disabled={loading}
            >
              👨‍🏫 Teacher
            </button>
            <button
              type="button"
              className="btn btn-demo"
              onClick={() => handleDemoLogin('parent')}
              disabled={loading}
            >
              👨‍👩‍👧‍👦 Parent
            </button>
            <button
              type="button"
              className="btn btn-demo"
              onClick={() => handleDemoLogin('student')}
              disabled={loading}
            >
              👨‍🎓 Student
            </button>
          </div>
        </div>

        <div className="login-footer">
          <p>
            Don't have an account? <Link to="/signup">Sign up here</Link>
          </p>
          <p>
            <Link to="/">← Back to Home</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login; 