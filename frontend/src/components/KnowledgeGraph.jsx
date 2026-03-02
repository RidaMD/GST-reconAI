import React from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { linkColorMap } from '../constants';

const KnowledgeGraph = ({
    graphRef,
    graphData,
    nodeCanvasObject,
    handleNodeClick,
    activeTab
}) => {
    return (
        <div style={{ display: activeTab === 'graph' ? 'block' : 'none', height: '100%', width: '100%' }}>
            <ForceGraph2D
                ref={graphRef}
                graphData={graphData}
                nodeId="id"
                nodeLabel="name"
                nodeCanvasObject={nodeCanvasObject}
                linkColor={link => linkColorMap[link.label] || '#94a3b8'}
                linkWidth={1.5}
                linkDirectionalArrowLength={4}
                linkDirectionalArrowRelPos={1}
                linkDirectionalParticles={2}
                linkDirectionalParticleWidth={2}
                linkDirectionalParticleColor={link => linkColorMap[link.label] || '#94a3b8'}
                backgroundColor="#f8fafc"
                onNodeClick={handleNodeClick}
                linkCanvasObjectMode={() => 'after'}
                linkCanvasObject={(link, ctx, globalScale) => {
                    let label = link.label;
                    if (!label) return;

                    const start = link.source;
                    const end = link.target;

                    if (typeof start !== 'object' || typeof end !== 'object') return;

                    const x = start.x + (end.x - start.x) / 2;
                    const y = start.y + (end.y - start.y) / 2;

                    const fontSize = 10 / globalScale;
                    ctx.font = `${fontSize}px Inter`;

                    const textWidth = ctx.measureText(label).width;
                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);

                    ctx.fillStyle = 'rgba(248, 250, 252, 0.8)';
                    ctx.fillRect(x - bckgDimensions[0] / 2, y - bckgDimensions[1] / 2, ...bckgDimensions);

                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = linkColorMap[link.label] || '#94a3b8';
                    ctx.fillText(label, x, y);
                }}
            />
        </div>
    );
};

export default KnowledgeGraph;
