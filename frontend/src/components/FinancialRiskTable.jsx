import React from 'react';
import { ExternalLink } from 'lucide-react';

const FinancialRiskTable = ({
    mismatches,
    generateAudit,
    setActiveTab,
    auditLoading
}) => {
    return (
        <div className="tab-pane financial-pane">
            <div style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h2 className="section-title" style={{ margin: 0 }}>Financial Risk Scorer</h2>
                    <div style={{ backgroundColor: '#f1f5f9', padding: '6px 12px', borderRadius: '8px', fontSize: '0.85rem', color: '#475569', fontWeight: 600 }}>
                        Showing {mismatches.length} Invoices
                    </div>
                </div>
                <div className="table-wrapper" style={{ overflow: 'visible' }}>
                    <table className="data-table" style={{ width: '100%', borderCollapse: 'separate', borderSpacing: 0 }}>
                        <thead>
                            <tr>
                                <th style={{ width: '10%' }}>Invoice</th>
                                <th style={{ width: '25%' }}>Supplier</th>
                                <th style={{ width: '15%' }}>Taxable Value</th>
                                <th style={{ width: '12%' }}>Tax</th>
                                <th style={{ width: '23%' }}>Compliance Status</th>
                                <th style={{ width: '8%', textAlign: 'center' }}>Risk</th>
                                <th style={{ width: '7%', textAlign: 'center' }}>Score</th>
                            </tr>
                        </thead>
                        <tbody>
                            {(() => {
                                const riskPriority = { 'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'CLEAN': 0 };
                                return [...mismatches].sort((a, b) => {
                                    const priorityA = riskPriority[a.risk_level] || 0;
                                    const priorityB = riskPriority[b.risk_level] || 0;
                                    if (priorityA !== priorityB) return priorityB - priorityA;
                                    return b.risk_score - a.risk_score;
                                }).map(m => (
                                    <tr key={m.invoice_id}>
                                        <td className="fw-500" style={{ color: '#475569' }}>{m.invoice_id}</td>
                                        <td>
                                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                                <span style={{ fontWeight: 600, color: '#334155' }}>{m.supplier_name}</span>
                                                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{m.supplier_gstin}</span>
                                            </div>
                                        </td>
                                        <td style={{ fontWeight: 600, color: '#334155' }}>₹{m.amount_invoice.toLocaleString('en-IN')}</td>
                                        <td style={{ color: '#64748b' }}>₹{m.gst_invoice.toLocaleString('en-IN')}</td>
                                        <td>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                                                {m.root_cause.split(' | ').map((tag, idx) => {
                                                    const tagClass = tag.toLowerCase().includes('match') ? 'tag-match' :
                                                        tag.toLowerCase().includes('excess') ? 'tag-excess' :
                                                            tag.toLowerCase().includes('under') ? 'tag-under' :
                                                                tag.toLowerCase().includes('not filed') ? 'tag-unfiled' : 'tag-mismatch';
                                                    return (
                                                        <span key={idx} className={`mismatch-tag ${tagClass}`}>
                                                            {tag}
                                                        </span>
                                                    );
                                                })}
                                            </div>
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            <span className={`badge risk-${m.risk_level.toLowerCase()}`}>{m.risk_level}</span>
                                        </td>
                                        <td style={{ fontWeight: 700, color: '#1e293b', textAlign: 'center' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px' }}>
                                                <span>{m.risk_score.toString().replace(/\.0$/, '')}</span>
                                                <button
                                                    className="btn-icon"
                                                    title="Generate AI Audit Report"
                                                    onClick={() => {
                                                        generateAudit(m.invoice_id);
                                                        setActiveTab('audit');
                                                    }}
                                                    disabled={auditLoading}
                                                >
                                                    <ExternalLink size={14} />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            })()}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default FinancialRiskTable;
