import React, { useState } from 'react';
import { authAPI } from '../api';
import './UserProfile.css';

function UserProfile({ user, onClose, onLogout }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // Profile update state
  const [profileData, setProfileData] = useState({
    email: user?.user?.email || '',
    username: user?.user?.username || user?.username || ''
  });

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setError('New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);
    try {
      await authAPI.changePassword({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      });

      setMessage('Password changed successfully!');
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');

    setLoading(true);
    try {
      await authAPI.updateProfile({
        email: profileData.email
      });

      setMessage('Profile updated successfully!');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      return;
    }

    if (!window.confirm('This will permanently delete all your data. Are you absolutely sure?')) {
      return;
    }

    setLoading(true);
    try {
      await authAPI.deleteAccount();

      alert('Account deleted successfully');
      onLogout();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="profile-modal-overlay" onClick={onClose}>
      <div className="profile-modal" onClick={(e) => e.stopPropagation()}>
        <div className="profile-header">
          <h2>👤 User Profile</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        {message && <div className="success-message">{message}</div>}
        {error && <div className="error-message">{error}</div>}

        <div className="profile-tabs">
          <button 
            className={`tab-btn ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            📋 Profile Info
          </button>
          <button 
            className={`tab-btn ${activeTab === 'password' ? 'active' : ''}`}
            onClick={() => setActiveTab('password')}
          >
            🔐 Change Password
          </button>
          <button 
            className={`tab-btn ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            ⚙️ Settings
          </button>
        </div>

        <div className="profile-content">
          {/* Profile Info Tab */}
          {activeTab === 'profile' && (
            <form onSubmit={handleProfileUpdate} className="profile-form">
              <div className="profile-info-card">
                <div className="profile-avatar">
                  <div className="avatar-circle">
                    {(profileData.username || 'U').charAt(0).toUpperCase()}
                  </div>
                </div>
                <h3>{profileData.username}</h3>
              </div>

              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={profileData.username}
                  disabled
                  className="disabled-input"
                />
                <small>Username cannot be changed</small>
              </div>

              <div className="form-group">
                <label>Email Address</label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                  placeholder="Enter your email"
                  required
                />
                <small>Used for password recovery and notifications</small>
              </div>

              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Updating...' : '💾 Update Profile'}
              </button>
            </form>
          )}

          {/* Change Password Tab */}
          {activeTab === 'password' && (
            <form onSubmit={handlePasswordChange} className="profile-form">
              <div className="form-group">
                <label>Current Password</label>
                <input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                  placeholder="Enter current password"
                  required
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>New Password</label>
                <input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                  placeholder="Enter new password"
                  minLength="8"
                  required
                  disabled={loading}
                />
                <small>Minimum 8 characters</small>
              </div>

              <div className="form-group">
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                  placeholder="Confirm new password"
                  minLength="8"
                  required
                  disabled={loading}
                />
              </div>

              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Changing...' : '🔐 Change Password'}
              </button>
            </form>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="settings-content">
              <div className="settings-section">
                <h3>🔔 Notifications</h3>
                <div className="setting-item">
                  <label>
                    <input type="checkbox" defaultChecked />
                    Email notifications for new datasets
                  </label>
                </div>
                <div className="setting-item">
                  <label>
                    <input type="checkbox" defaultChecked />
                    Email notifications for reports
                  </label>
                </div>
              </div>

              <div className="settings-section">
                <h3>🎨 Appearance</h3>
                <div className="setting-item">
                  <label>Theme</label>
                  <select>
                    <option>Light Mode</option>
                    <option>Dark Mode (Coming Soon)</option>
                  </select>
                </div>
              </div>

              <div className="settings-section">
                <h3>📊 Data Management</h3>
                <div className="setting-item">
                  <label>Default Dataset View</label>
                  <select>
                    <option>Table View</option>
                    <option>Chart View</option>
                    <option>Both</option>
                  </select>
                </div>
              </div>

              <div className="settings-section danger-zone">
                <h3>⚠️ Danger Zone</h3>
                <p>Once you delete your account, there is no going back. Please be certain.</p>
                <button 
                  className="btn-danger" 
                  onClick={handleDeleteAccount}
                  disabled={loading}
                >
                  🗑️ Delete Account
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserProfile;
