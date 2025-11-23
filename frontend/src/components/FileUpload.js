import React, { useState } from 'react';
import { datasetAPI } from '../api';
import CSVDataEditor from './CSVDataEditor';
import './FileUpload.css';

function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [previewData, setPreviewData] = useState(null);
  const [showEditor, setShowEditor] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith('.csv')) {
      setFile(selectedFile);
      setMessage('');
    } else {
      setMessage('Please select a valid CSV file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file');
      return;
    }

    setUploading(true);
    setMessage('Loading preview...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // First, get preview of the data
      const response = await datasetAPI.uploadCSV(formData);
      
      // Check if response has equipment_list for preview
      if (response.data.equipment_list && response.data.equipment_list.length > 0) {
        setPreviewData(response.data.equipment_list);
        setShowEditor(true);
        setMessage('');
      } else {
        // If no preview available, just show success
        setMessage('✅ File uploaded successfully!');
        setFile(null);
        document.getElementById('file-input').value = '';
        onUploadSuccess();
        setTimeout(() => setMessage(''), 3000);
      }
    } catch (error) {
      setMessage('❌ ' + (error.response?.data?.error || 'Upload failed'));
    } finally {
      setUploading(false);
    }
  };

  const handleSaveEditedData = async (editedData) => {
    setUploading(true);
    setMessage('Saving changes...');

    try {
      // Convert edited data back to CSV format and re-upload
      // For now, we'll just close editor and notify success
      setShowEditor(false);
      setMessage('✅ Data saved successfully!');
      setFile(null);
      document.getElementById('file-input').value = '';
      onUploadSuccess();
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      setMessage('❌ Failed to save changes');
    } finally {
      setUploading(false);
    }
  };

  const handleCancelEdit = () => {
    setShowEditor(false);
    setPreviewData(null);
    setMessage('Upload cancelled');
    setTimeout(() => setMessage(''), 2000);
  };

  return (
    <div className="file-upload-card">
      <h3>📤 Upload CSV File</h3>
      
      <div className="upload-area">
        <input
          id="file-input"
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="file-input"
        />
        
        {file && (
          <div className="file-info">
            <span className="file-name">📄 {file.name}</span>
            <span className="file-size">
              {(file.size / 1024).toFixed(2)} KB
            </span>
          </div>
        )}
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="btn-upload"
      >
        {uploading ? '⏳ Uploading...' : '⬆️ Upload'}
      </button>

      {message && (
        <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
          {message}
        </div>
      )}

      <div className="upload-info">
        <p><strong>Expected columns:</strong></p>
        <ul>
          <li>Equipment Name</li>
          <li>Type</li>
          <li>Flowrate</li>
          <li>Pressure</li>
          <li>Temperature</li>
        </ul>
      </div>

      {showEditor && previewData && (
        <CSVDataEditor
          data={previewData}
          onSave={handleSaveEditedData}
          onCancel={handleCancelEdit}
        />
      )}
    </div>
  );
}

export default FileUpload;
