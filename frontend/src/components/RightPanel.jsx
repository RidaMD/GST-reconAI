import React from 'react';
import { Search, Info, LayoutGrid, ChevronLeft, ChevronRight } from 'lucide-react';
import { colorMap, linkColorMap } from '../constants';

const RightPanel = ({
    searchQuery,
    handleSearch,
    selectedNode,
    getNodeSummary,
    graphData,
    isRightPanelOpen,
    setIsRightPanelOpen
}) => {
    if (!isRightPanelOpen) {
        return (
            <aside className="right-panel-collapsed">
                <button
                    className="toggle-btn"
                    onClick={() => setIsRightPanelOpen(true)}
                    title="Expand Details"
                    style={{ margin: '20px auto', display: 'block', background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                >
                    <ChevronLeft size={24} />
                </button>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '24px', marginTop: '20px' }}>
                    <Search size={22} color="#94a3b8" />
                    <Info size={22} color="#94a3b8" />
                    <LayoutGrid size={22} color="#94a3b8" />
                </div>
            </aside>
        );
    }

    return (
        <aside className="right-panel">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <h3 className="panel-title" style={{ margin: 0 }}>Dashboard Details</h3>
                <button
                    className="toggle-btn"
                    onClick={() => setIsRightPanelOpen(false)}
                    title="Collapse Panel"
                    style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                >
                    <ChevronRight size={24} />
                </button>
            </div>

            {/* SEARCH COMPONENT */}
            <div className="panel">
                <h2 className="panel-title">Node Search</h2>
                <div className="search-box">
                    <Search size={18} className="search-icon" />
                    <input
                        type="text"
                        placeholder="Search InvoiceID, GSTIN..."
                        value={searchQuery}
                        onChange={handleSearch}
                        className="search-input"
                    />
                </div>
            </div>

            {/* NODE PROPERTIES COMPONENT */}
            <div className="panel properties-panel">
                <h3 className="panel-title">Node Details</h3>
                {selectedNode ? (
                    <div className="property-list">
                        {/* Company & URN Header */}
                        <div style={{ marginBottom: '20px', borderBottom: '2px solid #f1f5f9', paddingBottom: '16px' }}>
                            <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700, marginBottom: '6px', letterSpacing: '0.05em' }}>
                                Target Identity
                            </div>
                            <h2 style={{ margin: 0, fontSize: '1.4rem', color: '#0f172a', fontWeight: 800, lineHeight: 1.2 }}>
                                {selectedNode.label === 'GSTIN' && selectedNode.legal_name
                                    ? selectedNode.legal_name
                                    : (selectedNode.name || selectedNode.supplier_name || "GST Entity")}
                            </h2>
                            <div style={{ fontSize: '0.9rem', color: '#64748b', marginTop: '8px', fontWeight: 500 }}>
                                URN: <span style={{ color: '#0284c7', fontWeight: 700, fontFamily: 'monospace' }}>{selectedNode.gstin || selectedNode.invoice_id || selectedNode.id}</span>
                            </div>
                        </div>

                        <div className="node-summary-box" style={{
                            borderLeft: `5px solid ${colorMap[selectedNode.label] || '#94a3b8'}`
                        }}>
                            {getNodeSummary(selectedNode)}
                        </div>

                        <div>
                            {Object.keys(selectedNode).filter(k => !['id', 'x', 'y', 'vx', 'vy', 'index', 'risk', 'color', 'fx', 'fy', '__indexColor', 'risk_level', 'root_cause', 'name', 'supplier_name', 'gstin'].includes(k)).map(key => (
                                <div className="property-item" key={key}>
                                    <span className="property-key">{key}:</span>
                                    <span className="property-val">{String(selectedNode[key])}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="empty-state">
                        <Info size={24} color="#94a3b8" />
                        <p>Click any node in the graph to view properties.</p>
                    </div>
                )}
            </div>

            {/* METRICS COMPONENT */}
            <div className="panel">
                <h3 className="panel-title">Graph Layout</h3>
                <div className="metrics-row">
                    <div className="metric-box">
                        <div className="metric-val" style={{ color: '#0ea5e9' }}>{graphData.nodes.length}</div>
                        <div className="metric-label">Nodes</div>
                    </div>
                    <div className="metric-box">
                        <div className="metric-val" style={{ color: '#10b981' }}>{graphData.links.length}</div>
                        <div className="metric-label">Edges</div>
                    </div>
                </div>
            </div>

            {/* LEGEND COMPONENT */}
            <div className="panel" style={{ flex: 'none', display: 'flex', flexDirection: 'column' }}>
                <h3 className="panel-title">Graph Legend</h3>
                <div className="legend-content">
                    <div style={{ marginBottom: '20px' }}>
                        <h4 style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '10px', fontWeight: 800, letterSpacing: '0.05em' }}>Nodes</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                            {Object.entries(colorMap).map(([label, color]) => (
                                <div key={label} style={{ display: 'flex', alignItems: 'center' }}>
                                    <span style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: color, marginRight: '8px', flexShrink: 0, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}></span>
                                    <span style={{ fontSize: '13px', color: '#334155', fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div>
                        <h4 style={{ fontSize: '11px', color: '#64748b', textTransform: 'uppercase', marginBottom: '10px', fontWeight: 800, letterSpacing: '0.05em' }}>Edges</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                            {Object.entries(linkColorMap).map(([label, color]) => (
                                <div key={label} style={{ display: 'flex', alignItems: 'center' }}>
                                    <span style={{ width: '16px', height: '3px', borderRadius: '2px', backgroundColor: color, marginRight: '8px', flexShrink: 0 }}></span>
                                    <span style={{ fontSize: '13px', color: '#334155', fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default RightPanel;
