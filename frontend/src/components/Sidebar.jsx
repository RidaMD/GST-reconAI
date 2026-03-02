import React from 'react';
import { Activity, Network, FileText, ShieldAlert } from 'lucide-react';

const Sidebar = ({
    activeTab,
    setActiveTab,
    isSidebarOpen,
    setIsSidebarOpen
}) => {
    return (
        <aside className={isSidebarOpen ? "sidebar-expanded" : "sidebar-collapsed"}>
            <div className="sidebar-header">
                <Activity className="app-icon" size={28} style={{ flexShrink: 0 }} />
                {isSidebarOpen && (
                    <div>
                        <h1 className="app-title" style={{ fontSize: '16px' }}>GST ReconAI</h1>
                    </div>
                )}
                <button className="toggle-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
                    <Network size={20} />
                </button>
            </div>

            <div className="nav-tabs">
                <button
                    className={`nav-tab ${activeTab === 'graph' ? 'active' : ''}`}
                    onClick={() => setActiveTab('graph')}
                    title="Knowledge Graph"
                >
                    <Network size={18} /> {isSidebarOpen && "Knowledge Graph"}
                </button>
                <button
                    className={`nav-tab ${activeTab === 'financial' ? 'active' : ''}`}
                    onClick={() => setActiveTab('financial')}
                    title="Financial Risk Scorer"
                >
                    <FileText size={18} /> {isSidebarOpen && "Financial Risk Scorer"}
                </button>
                <button
                    className={`nav-tab ${activeTab === 'audit' ? 'active' : ''}`}
                    onClick={() => setActiveTab('audit')}
                    title="Automate NLP Audit"
                >
                    <FileText size={18} /> {isSidebarOpen && "Automate NLP Audit"}
                </button>
                <button
                    className={`nav-tab ${activeTab === 'predict' ? 'active' : ''}`}
                    onClick={() => setActiveTab('predict')}
                    title="Vendor Risk Predictor"
                >
                    <ShieldAlert size={18} /> {isSidebarOpen && "Vendor Risk Predictor"}
                </button>
            </div>

            <div className="sidebar-scrollable">
                {activeTab === 'graph' && isSidebarOpen && (
                    <div className="panel info-panel">
                        <h3 className="panel-title">Knowledge Graph</h3>
                        <p className="help-text">
                            Interactive visualization of GST supply chain, tracking relationships between taxpayers, invoices, and returns to map end-to-end compliance flows.
                        </p>
                    </div>
                )}

                {activeTab === 'financial' && isSidebarOpen && (
                    <div className="panel info-panel">
                        <h3 className="panel-title">Financial Risk</h3>
                        <p className="help-text">
                            Tabular view of invoices ranked by financial exposure and structural compliance risk. Select an invoice ID to run a thorough AI audit.
                        </p>
                    </div>
                )}

                {activeTab === 'audit' && isSidebarOpen && (
                    <div className="panel info-panel">
                        <h3 className="panel-title">Audit Engine</h3>
                        <p className="help-text">
                            The NLP Engine utilizes Langchain and OpenAI to transcribe the raw paths into easily readable compliance reports.
                        </p>
                    </div>
                )}

                {activeTab === 'predict' && isSidebarOpen && (
                    <div className="panel info-panel">
                        <h3 className="panel-title">Predictive Engine</h3>
                        <p className="help-text">
                            By tracking behavioral signatures inside the Knowledge Graph, the ML Engine aggregates risk to predict future vendor non-compliance BEFORE payments.
                        </p>
                    </div>
                )}
            </div>
        </aside>
    );
};

export default Sidebar;
