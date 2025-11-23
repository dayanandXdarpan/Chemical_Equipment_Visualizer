import React, { useState } from 'react';
import './CSVDataEditor.css';

function CSVDataEditor({ data, onSave, onCancel }) {
  const [editedData, setEditedData] = useState(data);
  const [editingCell, setEditingCell] = useState(null);

  if (!data || data.length === 0) {
    return null;
  }

  const columns = Object.keys(data[0]);

  const handleCellChange = (rowIndex, column, value) => {
    const newData = [...editedData];
    newData[rowIndex] = {
      ...newData[rowIndex],
      [column]: value
    };
    setEditedData(newData);
  };

  const handleDeleteRow = (rowIndex) => {
    const newData = editedData.filter((_, index) => index !== rowIndex);
    setEditedData(newData);
  };

  const handleAddRow = () => {
    const newRow = {};
    columns.forEach(col => {
      newRow[col] = '';
    });
    setEditedData([...editedData, newRow]);
  };

  const handleSave = () => {
    // Validate data before saving
    const hasEmptyRequired = editedData.some(row => 
      columns.some(col => !row[col] || row[col].toString().trim() === '')
    );

    if (hasEmptyRequired) {
      if (!window.confirm('Some cells are empty. Continue anyway?')) {
        return;
      }
    }

    onSave(editedData);
  };

  return (
    <div className="csv-editor-modal">
      <div className="csv-editor-container">
        <div className="csv-editor-header">
          <h2>📝 Review & Edit Imported Data</h2>
          <p>Total Rows: <strong>{editedData.length}</strong> | Columns: <strong>{columns.length}</strong></p>
        </div>

        <div className="csv-editor-body">
          <div className="table-wrapper">
            <table className="csv-table">
              <thead>
                <tr>
                  <th className="row-number">#</th>
                  {columns.map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                  <th className="actions-col">Actions</th>
                </tr>
              </thead>
              <tbody>
                {editedData.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    <td className="row-number">{rowIndex + 1}</td>
                    {columns.map((col) => (
                      <td
                        key={`${rowIndex}-${col}`}
                        className={editingCell?.row === rowIndex && editingCell?.col === col ? 'editing' : ''}
                        onDoubleClick={() => setEditingCell({ row: rowIndex, col })}
                      >
                        {editingCell?.row === rowIndex && editingCell?.col === col ? (
                          <input
                            type="text"
                            value={row[col] || ''}
                            onChange={(e) => handleCellChange(rowIndex, col, e.target.value)}
                            onBlur={() => setEditingCell(null)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') setEditingCell(null);
                              if (e.key === 'Escape') {
                                setEditingCell(null);
                                // Restore original value
                                setEditedData(data);
                              }
                            }}
                            autoFocus
                            className="cell-input"
                          />
                        ) : (
                          <span className="cell-value">{row[col]}</span>
                        )}
                      </td>
                    ))}
                    <td className="actions-col">
                      <button
                        onClick={() => handleDeleteRow(rowIndex)}
                        className="btn-delete-row"
                        title="Delete row"
                      >
                        🗑️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="csv-editor-footer">
          <div className="footer-left">
            <button onClick={handleAddRow} className="btn-add-row">
              ➕ Add Row
            </button>
            <p className="hint">💡 Double-click any cell to edit</p>
          </div>

          <div className="footer-right">
            <button onClick={onCancel} className="btn-cancel">
              ❌ Cancel
            </button>
            <button onClick={() => setEditedData(data)} className="btn-reset">
              🔄 Reset
            </button>
            <button onClick={handleSave} className="btn-save">
              ✅ Save & Visualize ({editedData.length} rows)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CSVDataEditor;
