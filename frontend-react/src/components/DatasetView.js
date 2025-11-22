import React, {useEffect, useState, useRef} from 'react';
import axios from 'axios';
import { API_BASE } from '../config';

// chart.js + react-chartjs-2
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

export default function DatasetView({dataset}){
  const [summary, setSummary] = useState({});
  const [rows, setRows] = useState([]);
  useEffect(()=>{ if(dataset) fetchSummary(); }, [dataset]);
  async function fetchSummary(){
    const res = await axios.get(`${API_BASE}/datasets/${dataset.id}/summary/`);
    setSummary(res.data.summary || {});
  // Request a large page_size to retrieve all rows in a single call.
  // The backend supports pagination; using a large number is a pragmatic
  // way to get the full dataset for viewing. If your dataset is huge you
  // may prefer server-side paging or a download/export feature.
  const r = await axios.get(`${API_BASE}/datasets/${dataset.id}/rows/?page_size=100000`);
  setRows(r.data.rows || []);
  }

  // Determine numeric columns (keys from summary)
  const numericCols = Object.keys(summary || {});

  // Chart for rows (line) - keep in case needed
  const chartCols = numericCols.slice(0,2);
  const chartDataRows = {
    labels: rows.map((_,i)=> String(i+1)),
    datasets: chartCols.map((col, idx) => ({
      label: col,
      data: rows.map(r => {
        const v = r[col];
        const n = typeof v === 'number' ? v : parseFloat(v);
        return Number.isFinite(n) ? n : null;
      }),
      borderColor: idx === 0 ? '#1f77b4' : '#ff7f0e', // blue / orange
      backgroundColor: idx === 0 ? 'rgba(255, 255, 255, 0.15)' : 'rgba(255,127,14,0.15)',
      tension: 0.2,
      fill: false,
      spanGaps: true,
    }))
  };

  // Chart for summary (bars): mean, median, min, max per parameter
  const summaryKeys = numericCols;
  const statsKeys = ['mean','median','min','max'];
  const colors = { mean: '#1f77b4', median: '#ff7f0e', min: '#2ca02c', max: '#d62728' };
  const chartDataSummary = {
    labels: summaryKeys,
    datasets: statsKeys.map(key => ({
      label: key,
      data: summaryKeys.map(param => {
        const v = summary[param] && summary[param][key];
        return typeof v === 'number' ? v : (v ? Number(v) : null);
      }),
      backgroundColor: colors[key],
      borderColor: colors[key],
    }))
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { labels: { color: '#ffffff' } },
      title: { display: false }
    },
    scales: {
      x: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255,255,255,0.06)' } },
      y: { ticks: { color: '#ffffff' }, grid: { color: 'rgba(255,255,255,0.06)' } }
    }
  };
  // ref + click handler state for showing clicked value
  const barChartRef = useRef(null);
  const [clickedPoint, setClickedPoint] = useState(null);

  // extend chartOptions with onClick handler to show clicked value
  const chartOptionsWithClick = Object.assign({}, chartOptions, {
    onClick: (evt, elements) => {
      if (elements && elements.length > 0) {
        const el = elements[0];
        const datasetIndex = el.datasetIndex;
        const index = el.index;
        const label = chartDataSummary.labels[index];
        const datasetLabel = chartDataSummary.datasets[datasetIndex].label;
        const value = chartDataSummary.datasets[datasetIndex].data[index];
        setClickedPoint({ label, datasetLabel, value });
      }
    }
  });
  return (
    <div style={{marginTop:12}}>
      <h4 style={{color:'#ffffff'}}>{dataset.name}</h4>

      <div style={{display:'flex', gap:12}}>
        <div style={{flex:1}}>
          {/* Given Data (all rows) */}
          <div style={{marginBottom:12, background:'#0b0b0b', padding:12, borderRadius:6}}>
            <h5 style={{color:'#ffffff', marginTop:0}}>Given Data ({rows.length} rows)</h5>
            {rows.length > 0 ? (
              <div style={{overflowX:'auto'}}>
                <table style={{width:'100%', borderCollapse:'collapse', color:'#ffffff'}}>
                  <thead>
                    <tr>
                      {Object.keys(rows[0]).map(k => (
                        <th key={k} style={{border:'1px solid rgba(255,255,255,0.06)', padding:6, textAlign:'left'}}>{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row,i) => (
                      <tr key={i}>
                        {Object.keys(rows[0]).map((k,ii) => (
                          <td key={ii} style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{String(row[k])}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{color:'#ffffff'}}>No rows available</div>
            )}
          </div>

          {/* Output Table (numeric summary) */}
          <div style={{marginBottom:24, background:'#0b0b0b', padding:12, borderRadius:6}}>
            <h5 style={{color:'#ffffff', marginTop:0}}>Output Table (summary statistics)</h5>
            {Object.keys(summary || {}).length > 0 ? (
              <div style={{overflowX:'auto'}}>
                <table style={{width:'100%', borderCollapse:'collapse', color:'#ffffff'}}>
                  <thead>
                    <tr>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6, textAlign:'left'}}>Parameter</th>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6}}>count</th>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6}}>mean</th>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6}}>median</th>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6}}>min</th>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6}}>max</th>
                      <th style={{border:'1px solid rgba(0, 0, 0, 0.06)', padding:6}}>std</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.keys(summary).map(param => {
                      const s = summary[param] || {};
                      return (
                        <tr key={param}>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{param}</td>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{s.count ?? ''}</td>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{s.mean ?? ''}</td>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{s.median ?? ''}</td>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{s.min ?? ''}</td>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{s.max ?? ''}</td>
                          <td style={{border:'1px solid rgba(255,255,255,0.04)', padding:6}}>{s.std ?? ''}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div style={{color:'#ffffff'}}>No numeric summary available</div>
            )}
          </div>
        </div>

        <div style={{flex:1}}>
          {/* Right column: Output Chart (summary stats) */}
          {summaryKeys.length > 0 ? (
            <div style={{marginBottom:12, background:'#0b0b0b', padding:12, borderRadius:6}}>
              <h5 style={{color:'#ffffff', marginTop:0}}>Output Chart — mean / median / min / max per parameter</h5>
              <Bar ref={barChartRef} data={chartDataSummary} options={chartOptionsWithClick} />
              <div style={{marginTop:8}}>
                {statsKeys.map(k => (
                  <span key={k} style={{marginRight:12, color:'#ffffff'}}>
                    <span style={{display:'inline-block', width:12, height:6, background: colors[k], marginRight:6}}></span>
                    {k}
                  </span>
                ))}
              </div>
              {clickedPoint && (
                <div style={{marginTop:8, color:'#ffffff'}}>
                  <strong>Selected:</strong> {clickedPoint.datasetLabel} for {clickedPoint.label} = {clickedPoint.value}
                </div>
              )}
            </div>
          ) : (
            <div style={{color:'#ffffff'}}><strong>No numeric columns to chart</strong></div>
          )}
        </div>
      </div>

      {/* single Output Table kept in left column; duplicate removed */}
    </div>
  );
}
