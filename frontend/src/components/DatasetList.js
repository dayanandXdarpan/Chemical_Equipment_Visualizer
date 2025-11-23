import React from 'react';
import './DatasetList.css';

function DatasetList({ datasets, onSelectDataset, onDeleteDataset, selectedDatasetId, loading }) {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="dataset-list-card">
      <h3>📊 Dataset History (Last 5)</h3>
      
      {loading && <div className="loading">Loading...</div>}
      
      {!loading && datasets.length === 0 && (
        <div className="no-datasets">
          No datasets uploaded yet. Upload a CSV file to get started!
        </div>
      )}

      <div className="dataset-list">
        {datasets.map((dataset) => (
          <div
            key={dataset.id}
            className={`dataset-item ${selectedDatasetId === dataset.id ? 'active' : ''}`}
            onClick={() => onSelectDataset(dataset.id)}
          >
            <div className="dataset-header">
              <span className="dataset-name">📄 {dataset.name}</span>
              <button
                className="btn-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteDataset(dataset.id);
                }}
                title="Delete dataset"
              >
                🗑️
              </button>
            </div>
            
            <div className="dataset-info">
              <span className="dataset-date">
                🕒 {formatDate(dataset.uploaded_at)}
              </span>
              <span className="dataset-count">
                📦 {dataset.total_count} items
              </span>
            </div>

            <div className="dataset-stats">
              <div className="stat">
                <span className="stat-label">Avg Flow:</span>
                <span className="stat-value">{dataset.avg_flowrate.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Avg Press:</span>
                <span className="stat-value">{dataset.avg_pressure.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Avg Temp:</span>
                <span className="stat-value">{dataset.avg_temperature.toFixed(2)}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default DatasetList;
