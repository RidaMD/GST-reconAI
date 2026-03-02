import React from 'react';
import { Activity, Upload, CheckCircle, AlertTriangle } from 'lucide-react';

const LandingPage = ({
    handleInitialFileUpload,
    handleSkipUpload,
    setFiles,
    files,
    uploadStatus
}) => {
    return (
        <div className="landing-container">
            <div className="landing-card">
                <Activity size={56} color="#0ea5e9" className="landing-icon" />
                <h1>GST ReconAI</h1>
                <p className="landing-subtitle">Upload your GST details (GSTR-1, GSTR-2B, Invoices, e-Invoices) as CSV to build the Knowledge Graph.</p>

                <form onSubmit={handleInitialFileUpload} className="upload-form landing-upload">
                    <label className="upload-dropzone landing-dropzone">
                        <Upload size={36} color="#0ea5e9" />
                        <span className="drop-main">Target .csv files to ingest</span>
                        <span className="drop-sub">Drag and drop or click to browse</span>
                        <input
                            type="file"
                            multiple
                            accept=".csv"
                            onChange={(e) => setFiles(e.target.files)}
                            className="hidden-input"
                        />
                    </label>
                    {files && <div className="file-count">{files.length} file(s) selected</div>}

                    <div className="landing-actions">
                        <button
                            disabled={!files || uploadStatus.includes('Uploading')}
                            type="submit"
                            className="btn-primary landing-btn"
                        >
                            Generate Knowledge Graph Dashboard
                        </button>
                        <button
                            type="button"
                            onClick={handleSkipUpload}
                            className="btn-secondary landing-btn"
                        >
                            Skip & Use Existing DB Data
                        </button>
                    </div>
                </form>

                {uploadStatus && (
                    <div className={`landing-status ${uploadStatus.includes('Error') ? 'error' : 'success'}`}>
                        {uploadStatus.includes('Error') ? <AlertTriangle size={18} /> : <CheckCircle size={18} />}
                        <span>{uploadStatus}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default LandingPage;
