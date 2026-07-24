import React, { useState, useEffect, useRef } from 'react';
import './EmployeeUpload.css';

function EmployeeUpload() {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusInfo, setStatusInfo] = useState({
    status: 'idle',
    active_file: null,
    rows: 0,
    columns: 0,
    upload_time: null,
    validation_passed: false,
    processing_time_ms: 0
  });

  const [employees, setEmployees] = useState([]);
  const [totalEmployees, setTotalEmployees] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const fileInputRef = useRef(null);
  const limit = 8;

  // Load status and employees on mount
  useEffect(() => {
    fetchStatus();
    fetchEmployees(1, searchQuery);
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch('http://localhost:8000/upload/status');
      if (res.ok) {
        const data = await res.json();
        setStatusInfo(data);
      }
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  const fetchEmployees = async (page = 1, search = '') => {
    try {
      const url = `http://localhost:8000/employees?page=${page}&limit=${limit}&search=${encodeURIComponent(search)}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setEmployees(data.data || []);
        setTotalEmployees(data.total || 0);
        setCurrentPage(page);
      }
    } catch (err) {
      console.error('Error fetching employees:', err);
    }
  };

  // Drag & drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    setErrorMessage('');
    setSuccessMessage('');
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      validateAndSetFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    setErrorMessage('');
    setSuccessMessage('');
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const validateAndSetFile = (selectedFile) => {
    const ext = selectedFile.name.split('.').pop().toLowerCase();
    if (ext !== 'csv' && ext !== 'xlsx') {
      setErrorMessage('Unsupported file type. Only CSV and XLSX are accepted.');
      setFile(null);
      return;
    }
    setFile(selectedFile);
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    setUploading(true);
    setErrorMessage('');
    setSuccessMessage('');
    setProgress(10);

    const formData = new FormData();
    formData.append('file', file);

    // Simulate progress while uploading
    const interval = setInterval(() => {
      setProgress((prev) => (prev < 90 ? prev + 15 : prev));
    }, 150);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      clearInterval(interval);
      setProgress(100);

      const result = await response.json();
      
      if (!response.ok) {
        const detail = result.detail;
        const message = typeof detail === 'object'
          ? [detail.message, ...(detail.issues || [])].filter(Boolean).join(' ')
          : detail;
        throw new Error(message || 'Failed to parse file.');
      }

      setSuccessMessage('Upload Successful');
      setFile(null);
      
      // Reload active data
      await fetchStatus();
      await fetchEmployees(1, searchQuery);
    } catch (err) {
      clearInterval(interval);
      setErrorMessage(err.message || 'Error occurred during file ingestion.');
    } finally {
      setUploading(false);
      setTimeout(() => setProgress(0), 1000);
    }
  };

  const handleRestore = async () => {
    if (window.confirm("Are you sure you want to delete the uploaded dataset and restore the synthetic demo data?")) {
      try {
        const res = await fetch('http://localhost:8000/upload', { method: 'DELETE' });
        if (res.ok) {
          setSuccessMessage('Demo data restored successfully');
          setErrorMessage('');
          setFile(null);
          await fetchStatus();
          await fetchEmployees(1, searchQuery);
        } else {
          const errData = await res.json();
          setErrorMessage(errData.detail || 'Failed to restore demo data');
        }
      } catch (err) {
        setErrorMessage('Failed to connect to backend server.');
      }
    }
  };

  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    fetchEmployees(1, query);
  };

  const handlePageChange = (newPage) => {
    fetchEmployees(newPage, searchQuery);
  };

  const totalPages = Math.ceil(totalEmployees / limit);

  return (
    <div className="employee-upload tab-content animate-fade-in">
      <div className="upload-header glass-panel">
        <div className="header-info">
          <h2>Employee Dataset Ingestion</h2>
          <p className="tab-desc">Upload custom HR records to analyze onboarding workflows, IT equipment checkpoints, and SaaS integrations.</p>
        </div>
        <div className="status-badge">
          {statusInfo.status === 'active' ? (
            <span className="badge active-badge">
              <span className="pulse-dot" /> Uploaded Dataset Active
            </span>
          ) : (
            <span className="badge demo-badge">Synthetic Demo Data Active</span>
          )}
        </div>
      </div>

      <div className="upload-layout">
        {/* Left Side: Upload dropzone */}
        <div className="upload-section glass-panel">
          <h3>File Ingestion Channel</h3>
          <div
            className={`dropzone ${isDragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={triggerFileInput}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              accept=".csv,.xlsx"
              onChange={handleFileChange}
            />
            <div className="dropzone-content">
              <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
              {file ? (
                <div className="file-details">
                  <p className="file-name">{file.name}</p>
                  <p className="file-size">{(file.size / 1024).toFixed(1)} KB</p>
                </div>
              ) : (
                <div>
                  <p className="primary-text">Drag & Drop employee dataset file here</p>
                  <p className="secondary-text">or <span className="browse-link">Browse File</span> (CSV or XLSX)</p>
                </div>
              )}
            </div>
          </div>

          {progress > 0 && (
            <div className="progress-container">
              <div className="progress-bar-wrapper">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
              </div>
              <span className="progress-label">Parsing & Validating {progress}%</span>
            </div>
          )}

          <div className="upload-actions">
            <button
              className="primary-btn"
              disabled={!file || uploading}
              onClick={handleUpload}
            >
              Ingest Dataset
            </button>
            {statusInfo.status === 'active' && (
              <button className="danger-btn" onClick={handleRestore} disabled={uploading}>
                Restore Demo Data
              </button>
            )}
          </div>

          {successMessage && (
            <div className="alert success-alert animate-fade-in">
              <div className="alert-title">✓ Upload Successful</div>
              <div className="alert-content">
                <p>Rows Imported: <strong>{statusInfo.rows}</strong></p>
                <p>Columns Imported: <strong>{statusInfo.columns}</strong></p>
                <p>Validation Passed: <strong>Passed</strong></p>
                <p>Processing Time: <strong>{statusInfo.processing_time_ms} ms</strong></p>
              </div>
            </div>
          )}

          {errorMessage && (
            <div className="alert error-alert animate-fade-in">
              <div className="alert-title">✗ Ingestion Failed</div>
              <p className="alert-desc">{errorMessage}</p>
            </div>
          )}
        </div>

        {/* Right Side: Upload metadata / validation stats */}
        <div className="info-section glass-panel">
          <h3>Ingestion Metadata</h3>
          <div className="metadata-grid">
            <div className="meta-item">
              <span className="meta-label">Active Source File</span>
              <span className="meta-val">{statusInfo.active_file || 'Synthetic Demo Data'}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Total Employee Rows</span>
              <span className="meta-val">{statusInfo.rows || totalEmployees}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Schema Columns</span>
              <span className="meta-val">{statusInfo.columns || 4}</span>
            </div>
            <div className="meta-item">
              <span className="meta-label">Last Ingested Date</span>
              <span className="meta-val">{statusInfo.upload_time || 'N/A (Default)'}</span>
            </div>
          </div>

          <div className="guidelines-box">
            <h4>Dataset Specifications</h4>
            <ul>
              <li>Must contain at least <strong>employee_id</strong> and <strong>employee_name</strong> columns.</li>
              <li>Expected columns like <strong>joining_date</strong>, <strong>laptop_issued</strong>, <strong>access_granted</strong>, and tool IDs will be mapped automatically.</li>
              <li>Date fields are automatically formatted to YYYY-MM-DD.</li>
              <li>Missing details are filled programmatically using the imputation pipeline.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Employee Table Preview */}
      <div className="preview-section glass-panel">
        <div className="preview-header">
          <h3>Employee Records Preview</h3>
          <div className="search-bar">
            <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              type="text"
              placeholder="Search by ID, name, department..."
              value={searchQuery}
              onChange={handleSearchChange}
            />
          </div>
        </div>

        {employees.length === 0 ? (
          <div className="empty-state">
            <p>No employee records match the search filter.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="employee-table">
              <thead>
                <tr>
                  <th>Employee ID</th>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Designation</th>
                  <th>Joining Date</th>
                  <th>Status</th>
                  <th>Laptop</th>
                  <th>Access</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.employee_id}>
                    <td><span className="code-font">{emp.employee_id}</span></td>
                    <td><strong>{emp.employee_name}</strong></td>
                    <td>{emp.department}</td>
                    <td>{emp.designation}</td>
                    <td>{emp.joining_date}</td>
                    <td>
                      <span className={`status-tag ${emp.onboarding_status === 'completed' ? 'status-complete' : 'status-pending'}`}>
                        {emp.onboarding_status || 'completed'}
                      </span>
                    </td>
                    <td>{emp.laptop_issued ? '✓ Issued' : '✗ Pending'}</td>
                    <td>{emp.access_granted ? '✓ Granted' : '✗ Denied'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="page-btn"
              disabled={currentPage === 1}
              onClick={() => handlePageChange(currentPage - 1)}
            >
              Previous
            </button>
            <span className="page-info">
              Page <strong>{currentPage}</strong> of {totalPages}
            </span>
            <button
              className="page-btn"
              disabled={currentPage === totalPages}
              onClick={() => handlePageChange(currentPage + 1)}
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default EmployeeUpload;
