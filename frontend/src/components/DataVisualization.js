import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import jsPDF from 'jspdf';
import 'jspdf-autotable';
import { datasetAPI } from '../api';
import './DataVisualization.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

function DataVisualization({ data }) {
  const [advancedStats, setAdvancedStats] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filteredData, setFilteredData] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    flowrateMin: '',
    flowrateMax: '',
    pressureMin: '',
    pressureMax: '',
    tempMin: '',
    tempMax: '',
    sortBy: 'id',
    sortOrder: 'asc'
  });

  // Fetch advanced statistics on component mount
  useEffect(() => {
    const fetchAdvancedStats = async () => {
      try {
        const response = await datasetAPI.getAdvancedStats(data.dataset_id);
        setAdvancedStats(response.data);
      } catch (error) {
        console.error('Error fetching advanced stats:', error);
      }
    };

    if (data.dataset_id) {
      fetchAdvancedStats();
    }
  }, [data.dataset_id]);

  // Handle export in different formats
  const handleExport = async (format) => {
    try {
      const response = await datasetAPI.exportData(data.dataset_id, format);
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const extensions = { csv: 'csv', json: 'json', excel: 'xlsx' };
      link.setAttribute('download', `dataset_${data.dataset_id}.${extensions[format]}`);
      
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      // Close the dropdown after export
      setIsDropdownOpen(false);
    } catch (error) {
      console.error(`Error exporting as ${format}:`, error);
      alert(`Failed to export data as ${format.toUpperCase()}`);
      setIsDropdownOpen(false);
    }
  };

  // Apply filters
  const applyFilters = async () => {
    try {
      const params = new URLSearchParams();
      
      if (filters.type) params.append('type', filters.type);
      if (filters.flowrateMin) params.append('flowrate_min', filters.flowrateMin);
      if (filters.flowrateMax) params.append('flowrate_max', filters.flowrateMax);
      if (filters.pressureMin) params.append('pressure_min', filters.pressureMin);
      if (filters.pressureMax) params.append('pressure_max', filters.pressureMax);
      if (filters.tempMin) params.append('temp_min', filters.tempMin);
      if (filters.tempMax) params.append('temp_max', filters.tempMax);
      if (filters.sortBy) params.append('sort_by', filters.sortBy);
      if (filters.sortOrder) params.append('sort_order', filters.sortOrder);

      const response = await datasetAPI.filterEquipment(data.dataset_id, params.toString());
      
      setFilteredData(response.data.results);
    } catch (error) {
      console.error('Error applying filters:', error);
      alert('Failed to apply filters');
    }
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      type: '',
      flowrateMin: '',
      flowrateMax: '',
      pressureMin: '',
      pressureMax: '',
      tempMin: '',
      tempMax: '',
      sortBy: 'id',
      sortOrder: 'asc'
    });
    setFilteredData(null);
  };

  // Update filter state
  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const generatePDF = () => {
    const doc = new jsPDF();
    
    // Title
    doc.setFontSize(18);
    doc.text('Chemical Equipment Analysis Report', 14, 20);
    
    // Dataset info
    doc.setFontSize(12);
    doc.text(`Dataset: ${data.dataset_name}`, 14, 35);
    doc.text(`Date: ${new Date(data.uploaded_at).toLocaleDateString()}`, 14, 42);
    doc.text(`Total Equipment: ${data.total_count}`, 14, 49);
    
    // Summary statistics
    doc.setFontSize(14);
    doc.text('Summary Statistics', 14, 60);
    doc.setFontSize(11);
    doc.text(`Average Flowrate: ${data.averages.flowrate}`, 14, 68);
    doc.text(`Average Pressure: ${data.averages.pressure}`, 14, 75);
    doc.text(`Average Temperature: ${data.averages.temperature}`, 14, 82);
    
    // Equipment type distribution
    doc.setFontSize(14);
    doc.text('Equipment Type Distribution', 14, 95);
    const typeTableData = data.type_distribution.map(item => [
      item.equipment_type,
      item.count
    ]);
    doc.autoTable({
      startY: 100,
      head: [['Equipment Type', 'Count']],
      body: typeTableData,
    });
    
    // Equipment details table
    doc.addPage();
    doc.setFontSize(14);
    doc.text('Equipment Details', 14, 20);
    
    const equipmentTableData = data.equipment_list.map(item => [
      item.equipment_name,
      item.equipment_type,
      item.flowrate.toFixed(2),
      item.pressure.toFixed(2),
      item.temperature.toFixed(2)
    ]);
    
    doc.autoTable({
      startY: 25,
      head: [['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']],
      body: equipmentTableData,
      styles: { fontSize: 8 },
    });
    
    // Save PDF
    doc.save(`equipment_report_${data.dataset_id}.pdf`);
  };

  // Prepare chart data for averages
  const averagesChartData = {
    labels: ['Flowrate', 'Pressure', 'Temperature'],
    datasets: [
      {
        label: 'Average Values',
        data: [data.averages.flowrate, data.averages.pressure, data.averages.temperature],
        backgroundColor: [
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 99, 132, 0.6)',
          'rgba(255, 206, 86, 0.6)',
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',
          'rgba(255, 99, 132, 1)',
          'rgba(255, 206, 86, 1)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // Prepare chart data for type distribution
  const typeDistributionData = {
    labels: data.type_distribution.map(item => item.equipment_type),
    datasets: [
      {
        label: 'Equipment Count',
        data: data.type_distribution.map(item => item.count),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
          'rgba(255, 159, 64, 0.6)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return (
    <div className="data-visualization">
      <div className="viz-header">
        <h2>📊 {data.dataset_name}</h2>
        <p className="edit-info">💡 <em>Tip: Re-upload CSV to visualize different data variations</em></p>
        <div className="header-actions">
          <button onClick={generatePDF} className="btn-pdf">
            📄 PDF Report
          </button>
          <div className={`export-dropdown ${isDropdownOpen ? 'open' : ''}`}>
            <button className="btn-export" onClick={() => setIsDropdownOpen(!isDropdownOpen)}>💾 Export Data</button>
            <div className="export-menu">
              <button onClick={() => handleExport('csv')}>📊 CSV</button>
              <button onClick={() => handleExport('json')}>📋 JSON</button>
              <button onClick={() => handleExport('excel')}>📈 Excel</button>
            </div>
          </div>
          <button 
            onClick={() => setShowFilters(!showFilters)} 
            className="btn-filter"
          >
            🔍 {showFilters ? 'Hide' : 'Show'} Filters
          </button>
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="filter-panel">
          <h3>🎯 Filter Equipment</h3>
          <div className="filter-grid">
            <div className="filter-group">
              <label>Equipment Type:</label>
              <input 
                type="text" 
                placeholder="e.g., Pump, Valve" 
                value={filters.type}
                onChange={(e) => handleFilterChange('type', e.target.value)}
              />
            </div>
            
            <div className="filter-group">
              <label>Flowrate Range:</label>
              <div className="range-inputs">
                <input 
                  type="number" 
                  placeholder="Min" 
                  value={filters.flowrateMin}
                  onChange={(e) => handleFilterChange('flowrateMin', e.target.value)}
                />
                <span>to</span>
                <input 
                  type="number" 
                  placeholder="Max" 
                  value={filters.flowrateMax}
                  onChange={(e) => handleFilterChange('flowrateMax', e.target.value)}
                />
              </div>
            </div>
            
            <div className="filter-group">
              <label>Pressure Range:</label>
              <div className="range-inputs">
                <input 
                  type="number" 
                  placeholder="Min" 
                  value={filters.pressureMin}
                  onChange={(e) => handleFilterChange('pressureMin', e.target.value)}
                />
                <span>to</span>
                <input 
                  type="number" 
                  placeholder="Max" 
                  value={filters.pressureMax}
                  onChange={(e) => handleFilterChange('pressureMax', e.target.value)}
                />
              </div>
            </div>
            
            <div className="filter-group">
              <label>Temperature Range:</label>
              <div className="range-inputs">
                <input 
                  type="number" 
                  placeholder="Min" 
                  value={filters.tempMin}
                  onChange={(e) => handleFilterChange('tempMin', e.target.value)}
                />
                <span>to</span>
                <input 
                  type="number" 
                  placeholder="Max" 
                  value={filters.tempMax}
                  onChange={(e) => handleFilterChange('tempMax', e.target.value)}
                />
              </div>
            </div>
            
            <div className="filter-group">
              <label>Sort By:</label>
              <select 
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              >
                <option value="id">ID</option>
                <option value="equipment_name">Name</option>
                <option value="equipment_type">Type</option>
                <option value="flowrate">Flowrate</option>
                <option value="pressure">Pressure</option>
                <option value="temperature">Temperature</option>
              </select>
            </div>
            
            <div className="filter-group">
              <label>Order:</label>
              <select 
                value={filters.sortOrder}
                onChange={(e) => handleFilterChange('sortOrder', e.target.value)}
              >
                <option value="asc">Ascending</option>
                <option value="desc">Descending</option>
              </select>
            </div>
          </div>
          
          <div className="filter-actions">
            <button onClick={applyFilters} className="btn-apply">
              ✓ Apply Filters
            </button>
            <button onClick={resetFilters} className="btn-reset">
              ✕ Reset
            </button>
          </div>
        </div>
      )}

      {/* Advanced Statistics Section */}
      {advancedStats && advancedStats.overall_statistics && (
        <div className="advanced-stats-section">
          <h3>📈 Advanced Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <h4>Flowrate Analysis</h4>
              <div className="stat-details">
                <p><strong>Min:</strong> {advancedStats.overall_statistics.flowrate_min?.toFixed(2)}</p>
                <p><strong>Max:</strong> {advancedStats.overall_statistics.flowrate_max?.toFixed(2)}</p>
                <p><strong>Avg:</strong> {advancedStats.overall_statistics.flowrate_avg?.toFixed(2)}</p>
                <p><strong>Std Dev:</strong> {advancedStats.overall_statistics.flowrate_std?.toFixed(2)}</p>
              </div>
            </div>
            
            <div className="stat-card">
              <h4>Pressure Analysis</h4>
              <div className="stat-details">
                <p><strong>Min:</strong> {advancedStats.overall_statistics.pressure_min?.toFixed(2)}</p>
                <p><strong>Max:</strong> {advancedStats.overall_statistics.pressure_max?.toFixed(2)}</p>
                <p><strong>Avg:</strong> {advancedStats.overall_statistics.pressure_avg?.toFixed(2)}</p>
                <p><strong>Std Dev:</strong> {advancedStats.overall_statistics.pressure_std?.toFixed(2)}</p>
              </div>
            </div>
            
            <div className="stat-card">
              <h4>Temperature Analysis</h4>
              <div className="stat-details">
                <p><strong>Min:</strong> {advancedStats.overall_statistics.temperature_min?.toFixed(2)}</p>
                <p><strong>Max:</strong> {advancedStats.overall_statistics.temperature_max?.toFixed(2)}</p>
                <p><strong>Avg:</strong> {advancedStats.overall_statistics.temperature_avg?.toFixed(2)}</p>
                <p><strong>Std Dev:</strong> {advancedStats.overall_statistics.temperature_std?.toFixed(2)}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="summary-cards">
        <div className="summary-card">
          <div className="card-icon">📦</div>
          <div className="card-content">
            <h3>Total Equipment</h3>
            <p className="card-value">{data.total_count}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-icon">💧</div>
          <div className="card-content">
            <h3>Avg Flowrate</h3>
            <p className="card-value">{data.averages.flowrate}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-icon">⚡</div>
          <div className="card-content">
            <h3>Avg Pressure</h3>
            <p className="card-value">{data.averages.pressure}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="card-icon">🌡️</div>
          <div className="card-content">
            <h3>Avg Temperature</h3>
            <p className="card-value">{data.averages.temperature}</p>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="charts-container">
        <div className="chart-box">
          <h3>Average Parameters</h3>
          <div className="chart-wrapper">
            <Bar data={averagesChartData} options={chartOptions} />
          </div>
        </div>
        
        <div className="chart-box">
          <h3>Equipment Type Distribution</h3>
          <div className="chart-wrapper">
            <Pie data={typeDistributionData} options={chartOptions} />
          </div>
        </div>
      </div>

      {/* Equipment Table */}
      <div className="equipment-table-container">
        <h3>Equipment Details {filteredData && <span className="filter-indicator">(Filtered: {filteredData.length} items)</span>}</h3>
        <div className="table-wrapper">
          <table className="equipment-table">
            <thead>
              <tr>
                <th>Equipment Name</th>
                <th>Type</th>
                <th>Flowrate</th>
                <th>Pressure</th>
                <th>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {(filteredData || data.equipment_list).map((item) => (
                <tr key={item.id}>
                  <td>{item.equipment_name}</td>
                  <td><span className="type-badge">{item.equipment_type}</span></td>
                  <td>{item.flowrate.toFixed(2)}</td>
                  <td>{item.pressure.toFixed(2)}</td>
                  <td>{item.temperature.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default DataVisualization;
