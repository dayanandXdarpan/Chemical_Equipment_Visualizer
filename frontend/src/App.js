import React, { useState, useEffect } from 'react';
import './App.css';
import Auth from './components/Auth';
import ForgotPassword from './components/ForgotPassword';
import FileUpload from './components/FileUpload';
import DatasetList from './components/DatasetList';
import DataVisualization from './components/DataVisualization';
import UserProfile from './components/UserProfile';
import { datasetAPI } from './api';

function App() {
  const [user, setUser] = useState(null);
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    const username = localStorage.getItem('username');
    if (token && username) {
      setUser({ username, token });
    }
    
    // Load datasets
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const response = await datasetAPI.getDatasets();
      setDatasets(response.data);
    } catch (error) {
      console.error('Error loading datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('token', userData.token);
    localStorage.setItem('username', userData.user.username);
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  };

  const handleUploadSuccess = () => {
    loadDatasets();
  };

  const handleSelectDataset = async (datasetId) => {
    try {
      setLoading(true);
      const response = await datasetAPI.getSummary(datasetId);
      setSelectedDataset(response.data);
    } catch (error) {
      console.error('Error loading dataset:', error);
      alert('Error loading dataset details');
    } finally {
      setLoading(false);
    }
  };

  const handleClearVisualization = () => {
    setSelectedDataset(null);
  };

  const handleDeleteDataset = async (datasetId) => {
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        await datasetAPI.deleteDataset(datasetId);
        loadDatasets();
        if (selectedDataset && selectedDataset.dataset_id === datasetId) {
          setSelectedDataset(null);
        }
      } catch (error) {
        console.error('Error deleting dataset:', error);
        alert('Error deleting dataset');
      }
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-left">
          <img src="/logo.png" alt="Logo" className="app-logo" />
          <h1>🧪 Chemical Equipment Parameter Visualizer</h1>
        </div>
        <div className="header-right">
          {user ? (
            <>
              <button onClick={() => setShowProfile(true)} className="btn-profile" title="User Profile">
                <span className="profile-icon">👤</span>
                <span className="profile-username">{user.username || user.user?.username}</span>
              </button>
              <button onClick={handleLogout} className="btn-logout">Logout</button>
            </>
          ) : null}
        </div>
      </header>

      <main className="App-main">
        {!user ? (
          showForgotPassword ? (
            <ForgotPassword onBack={() => setShowForgotPassword(false)} />
          ) : (
            <Auth 
              onLogin={handleLogin} 
              onForgotPassword={() => setShowForgotPassword(true)}
            />
          )
        ) : (
          <div className="content-container">
            <div className="sidebar">
              <FileUpload onUploadSuccess={handleUploadSuccess} />
              <DatasetList 
                datasets={datasets} 
                onSelectDataset={handleSelectDataset}
                onDeleteDataset={handleDeleteDataset}
                selectedDatasetId={selectedDataset?.dataset_id}
                loading={loading}
              />
            </div>
            
            <div className="main-content">
              {selectedDataset ? (
                <div className="visualization-wrapper">
                  <div className="viz-controls">
                    <button 
                      className="btn-clear-viz" 
                      onClick={handleClearVisualization}
                      title="Clear current visualization and select different data"
                    >
                      🔄 Clear
                    </button>
                  </div>
                  <DataVisualization data={selectedDataset} />
                </div>
              ) : (
                <div className="empty-state">
                  <h2>📊 Welcome to Equipment Visualizer</h2>
                  <p>Upload a CSV file or select a dataset to view analytics</p>
                  <div className="instructions">
                    <h3>How to use:</h3>
                    <ol>
                      <li>Upload a CSV file with equipment data</li>
                      <li>Select a dataset from the history</li>
                      <li>View data tables and charts</li>
                      <li>Download PDF reports</li>
                    </ol>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {showProfile && (
        <UserProfile 
          user={user} 
          onClose={() => setShowProfile(false)}
          onLogout={handleLogout}
        />
      )}

      <footer className="App-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Chemical Equipment Visualizer</h3>
            <p>Hybrid Web + Desktop Application</p>
            <p className="tech-stack">React.js • PyQt5 • Django REST • Pandas</p>
          </div>
          <div className="footer-section">
            <h3>Features</h3>
            <ul>
              <li>📤 CSV Data Upload & Processing</li>
              <li>📊 Interactive Visualizations</li>
              <li>📈 Real-time Analytics</li>
              <li>📄 PDF Report Generation</li>
            </ul>
          </div>
          <div className="footer-section">
            <h3>About</h3>
            <p>Built for chemical equipment data analysis and visualization</p>
            <p>Stores last 5 datasets with complete history</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© 2025 Chemical Equipment Visualizer | Developed by <a href="https://www.dayananddarpan.me/" target="_blank" rel="noopener noreferrer">Dayanand Darpan</a></p>
          <p className="version-info">Version {process.env.REACT_APP_VERSION || '1.1.0.0'}</p>
          <p className="footer-links">
            <a href="https://www.dayananddarpan.me/" target="_blank" rel="noopener noreferrer">🌐 Portfolio</a>
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
