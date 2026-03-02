import React from 'react';
import { Download, FileText } from 'lucide-react';
import { marked } from 'marked';

export default function NlpAudit({ auditLoading, currentAudit, downloadPDF, pdfRef }) {
    return (
        <div className="tab-pane audit-pane" style={{ padding: '24px', display: 'flex', justifyContent: 'center' }}>
            <div className="preview-side" style={{ flex: '0 1 800px', margin: '0 auto' }}>
                {auditLoading ? (
                    <div className="empty-preview">
                        <div className="spinner"></div><p>Langchain LLM is analyzing path topology...</p>
                    </div>
                ) : currentAudit ? (
                    <div className="report-container">
                        <div className="report-header">
                            <h3>AI Audit Generation Complete</h3>
                            <button className="btn-download" onClick={downloadPDF}>
                                <Download size={16} /> Download PDF
                            </button>
                        </div>
                        {/* HTML2PDF Target Div */}
                        <div className="markdown-preview" ref={pdfRef} dangerouslySetInnerHTML={{ __html: marked(currentAudit.markdown) }}>
                        </div>
                    </div>
                ) : (
                    <div className="empty-preview">
                        <FileText size={48} color="#cbd5e1" />
                        <h3>No Report Generated</h3>
                        <p>Go to the Financial Risk Scorer tab and select an invoice to invoke the LangChain Analyst.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
