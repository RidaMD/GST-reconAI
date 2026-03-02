import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function PredictiveVendorRisk({ vendorRisk }) {
    return (
        <div className="tab-pane predict-pane">
            <div className="header-box">
                <h2>Predictive Vendor Compliance Models</h2>
                <p>Aggregating Graph Patterns (Late filings, broken upstreams, critical multi-hops) to forecast future supplier behavior and protect your ITC eligibility.</p>
            </div>
            <div className="cards-grid">
                {vendorRisk.slice(0, 10).map((v, i) => (
                    <div className="vendor-card" key={v.supplier_gstin}>
                        <div className="vc-header">
                            <span className="rank-badge">#{i + 1} Threat</span>
                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                <h4 style={{ margin: 0 }}>{v.supplier_name || "Unknown Company"}</h4>
                                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>{v.supplier_gstin}</span>
                            </div>
                        </div>
                        <div className="vc-metrics">
                            <div className="v-stat">
                                <span className="v-label">Total Risk Score</span>
                                <span className="v-val threat-high">{v.total_risk.toFixed(1)}</span>
                            </div>
                            <div className="v-stat">
                                <span className="v-label">Graph Anomalies</span>
                                <span className="v-val">{v.anomalies}</span>
                            </div>
                        </div>
                        <div className="vc-footer">
                            <AlertTriangle size={14} color="#ef4444" />
                            <span>Prediction: {v.total_risk > 150 ? "Strongly advise withholding future ITC payments." : "Caution recommended for future transactions."} High historical defect rate.</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
