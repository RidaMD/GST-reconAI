import { useEffect, useState, useRef, useCallback } from 'react';
import axios from 'axios';
import html2pdf from 'html2pdf.js';
import './App.css';

// Components
import NlpAudit from './components/NlpAudit';
import PredictiveVendorRisk from './components/PredictiveVendorRisk';
import LandingPage from './components/LandingPage';
import Sidebar from './components/Sidebar';
import KnowledgeGraph from './components/KnowledgeGraph';
import FinancialRiskTable from './components/FinancialRiskTable';
import RightPanel from './components/RightPanel';

// Constants
import { colorMap } from './constants';

function App() {
  const [isAppStarted, setIsAppStarted] = useState(false);
  const [activeTab, setActiveTab] = useState('graph');
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(true);

  // Graph State
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [graphLoading, setGraphLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchFocusedNode, setSearchFocusedNode] = useState(null);

  // Data State
  const [mismatches, setMismatches] = useState([]);
  const [vendorRisk, setVendorRisk] = useState([]);

  // Upload State
  const [files, setFiles] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');

  // Audit State
  const [auditLoading, setAuditLoading] = useState(false);
  const [currentAudit, setCurrentAudit] = useState(null);

  const graphRef = useRef();
  const pdfRef = useRef(null);

  useEffect(() => {
    if (isAppStarted) {
      fetchData();
    }
  }, [isAppStarted]);

  const fetchData = async () => {
    setGraphLoading(true);
    try {
      const [graphRes, mismatchesRes] = await Promise.all([
        axios.get('http://localhost:8000/graph-data'),
        axios.get('http://localhost:8000/mismatches')
      ]);
      setGraphData(graphRes.data);

      const mmData = Array.isArray(mismatchesRes.data) ? mismatchesRes.data : (mismatchesRes.data.mismatches || []);
      setMismatches(mmData);

      const vendorMap = {};
      mmData.forEach(m => {
        if (!vendorMap[m.supplier_gstin]) {
          vendorMap[m.supplier_gstin] = {
            supplier_gstin: m.supplier_gstin,
            supplier_name: m.supplier_name,
            total_risk: 0,
            anomalies: 0,
            high_count: 0
          };
        }
        vendorMap[m.supplier_gstin].total_risk += m.risk_score;
        vendorMap[m.supplier_gstin].anomalies += 1;
        if (m.risk_level === 'High Risk' || m.risk_level === 'Critical Risk' || m.risk_level === 'CRITICAL') {
          vendorMap[m.supplier_gstin].high_count += 1;
        }
      });
      const vendorArray = Object.values(vendorMap).sort((a, b) => b.total_risk - a.total_risk);
      setVendorRisk(vendorArray);

    } catch (err) {
      console.error("Fetch Data Error:", err);
    }
    setGraphLoading(false);
  };

  useEffect(() => {
    if (graphRef.current && !graphLoading && activeTab === 'graph' && isAppStarted) {
      graphRef.current.d3Force('charge').strength(-800);
      graphRef.current.d3Force('link').distance(120);
    }
  }, [graphLoading, graphData, activeTab, isAppStarted]);

  const handleNodeClick = useCallback(node => {
    setSelectedNode(node);
    setSearchFocusedNode(node.id);
    graphRef.current.centerAt(node.x, node.y, 1000);
    graphRef.current.zoom(8, 2000);
  }, []);

  const handleSearch = (e) => {
    const q = e.target.value;
    setSearchQuery(q);

    if (q.length > 2) {
      const foundItem = graphData.nodes.find(n =>
        n.name?.toLowerCase().includes(q.toLowerCase()) ||
        n.id?.toLowerCase().includes(q.toLowerCase())
      );

      if (foundItem) {
        setSearchFocusedNode(foundItem.id);
        setSelectedNode(foundItem);
        graphRef.current.centerAt(foundItem.x, foundItem.y, 1000);
        graphRef.current.zoom(8, 2000);
      } else {
        setSearchFocusedNode(null);
      }
    } else {
      setSearchFocusedNode(null);
    }
  };

  const getNodeSummary = (node) => {
    if (!node) return null;
    if (node.label === 'Invoice') {
      const amount = node.amount?.toLocaleString('en-IN') || '0';
      const riskText = node.root_cause === 'Clean' ? 'is perfectly clean and compliant' : `has been flagged for: ${node.root_cause}`;
      return `Invoice ${node.invoice_id} was issued on ${node.date} for ₹${amount}. Our graph engine indicates this transaction ${riskText}.`;
    }
    if (node.label === 'GSTIN') {
      return `GST Registration number ${node.gstin} registered in the state of ${node.state}. It serves as a node for tracking issued and received invoices.`;
    }
    if (node.label === 'Taxpayer') {
      return `Legal entity name: ${node.name}. This taxpayer is operating in the ${node.sector} sector and holds one or more GST registrations.`;
    }
    if (node.label === 'GSTR1') {
      return `GSTR-1 return for ${node.month}. Status: ${node.filing_status}${node.delay_days > 0 ? ` (Delayed by ${node.delay_days} days)` : ''}.`;
    }
    return `Selected ${node.label} node: ${node.name || node.id}. View the properties below for technical details.`;
  };

  const handleInitialFileUpload = async (e) => {
    e.preventDefault();
    if (!files) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      setUploadStatus('Uploading Data to Neo4j...');
      await axios.post('http://localhost:8000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus('Success! Generating Graph Knowledge Base...');
      setTimeout(() => {
        setIsAppStarted(true);
        setUploadStatus('');
      }, 1500);
    } catch (err) {
      console.error(err);
      setUploadStatus('Error uploading files. Is the backend running?');
    }
  };

  const handleSkipUpload = () => {
    setIsAppStarted(true);
  };

  const generateAudit = async (invoice_id) => {
    setAuditLoading(true);
    setCurrentAudit(null);
    try {
      const res = await axios.get(`http://localhost:8000/audit-report/${invoice_id}`);
      setCurrentAudit({
        id: invoice_id,
        markdown: res.data.report_markdown
      });
    } catch (err) {
      console.error("Audit generation failed", err);
      setCurrentAudit({ id: invoice_id, markdown: "**Error:** Failed to generate LLM report. Ensure OPENAI_API_KEY is correct in backend." });
    }
    setAuditLoading(false);
  };

  const downloadPDF = () => {
    const element = pdfRef.current;
    const opt = {
      margin: 1,
      filename: `Audit_Report_${currentAudit.id}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
  };

  const nodeCanvasObject = useCallback((node, ctx, globalScale) => {
    const r = node.risk === 'high' ? 12 : node.risk === 'medium' ? 8 : 4;
    const isSearchFocused = node.id === searchFocusedNode;
    const isSelected = selectedNode && node.id === selectedNode.id;

    ctx.beginPath();
    ctx.arc(node.x, node.y, isSearchFocused ? r + 4 : r, 0, 2 * Math.PI, false);

    if (node.risk === 'high' || node.risk === 'Critical Risk' || node.risk === 'High Risk') ctx.fillStyle = '#ef4444';
    else if (node.risk === 'medium' || node.risk === 'Medium Risk') ctx.fillStyle = '#eab308';
    else ctx.fillStyle = colorMap[node.label] || '#4b5563';

    ctx.fill();

    if (isSearchFocused || isSelected) {
      ctx.lineWidth = 2 / globalScale;
      ctx.strokeStyle = '#0284c7';
      ctx.stroke();
    }

    if (globalScale > 0.8 || isSearchFocused || isSelected) {
      const fontSize = 16 / globalScale;
      ctx.font = `600 ${fontSize}px Inter`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#1e293b';

      const label = node.name || node.id;
      const textY = node.y + (r + 4) + (fontSize / 2);
      ctx.fillText(label, node.x, textY);

      const textWidth = ctx.measureText(label).width;
      ctx.beginPath();
      ctx.moveTo(node.x - textWidth / 2, textY + fontSize / 2.5);
      ctx.lineTo(node.x + textWidth / 2, textY + fontSize / 2.5);
      ctx.strokeStyle = '#1e293b';
      ctx.lineWidth = 1 / globalScale;
      ctx.stroke();
    }
  }, [searchFocusedNode, selectedNode]);

  if (!isAppStarted) {
    return (
      <LandingPage
        handleInitialFileUpload={handleInitialFileUpload}
        handleSkipUpload={handleSkipUpload}
        setFiles={setFiles}
        files={files}
        uploadStatus={uploadStatus}
      />
    );
  }

  return (
    <div className="dashboard-container">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isSidebarOpen={isSidebarOpen}
        setIsSidebarOpen={setIsSidebarOpen}
      />

      <main className="main-content-area">
        {graphLoading && (
          <div className="loading-overlay">
            <div className="spinner"></div>
            <p>Scanning knowledge graph and resolving paths...</p>
          </div>
        )}

        {!graphLoading && (
          <KnowledgeGraph
            graphRef={graphRef}
            graphData={graphData}
            nodeCanvasObject={nodeCanvasObject}
            handleNodeClick={handleNodeClick}
            activeTab={activeTab}
          />
        )}

        {activeTab === 'financial' && (
          <FinancialRiskTable
            mismatches={mismatches}
            generateAudit={generateAudit}
            setActiveTab={setActiveTab}
            auditLoading={auditLoading}
          />
        )}

        {activeTab === 'audit' && (
          <NlpAudit
            auditLoading={auditLoading}
            currentAudit={currentAudit}
            downloadPDF={downloadPDF}
            pdfRef={pdfRef}
          />
        )}

        {activeTab === 'predict' && (
          <PredictiveVendorRisk vendorRisk={vendorRisk} />
        )}
      </main>

      {activeTab === 'graph' && (
        <RightPanel
          searchQuery={searchQuery}
          handleSearch={handleSearch}
          selectedNode={selectedNode}
          getNodeSummary={getNodeSummary}
          graphData={graphData}
          isRightPanelOpen={isRightPanelOpen}
          setIsRightPanelOpen={setIsRightPanelOpen}
        />
      )}
    </div>
  );
}

export default App;
