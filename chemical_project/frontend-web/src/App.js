import React, { useState, useEffect } from "react";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";
import "./App.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

const API = "http://127.0.0.1:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [dark, setDark] = useState(false);
  const [summary, setSummary] = useState(null);
  const [averages, setAverages] = useState(null);
  const [types, setTypes] = useState(null);
  const [rows, setRows] = useState([]);
  const [history, setHistory] = useState([]);

  /* ---------------- HISTORY ---------------- */
  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API}/api/history/`);
      if (!res.ok) return;
      const data = await res.json();
      setHistory(data);
    } catch (err) {
      console.error("History error:", err);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  /* ---------------- UPLOAD ---------------- */
  const upload = async () => {
    if (!file) {
      alert("Please select a CSV file");
      return;
    }

    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await fetch(`${API}/api/upload/`, {
        method: "POST",
        body: fd,
      });

      const text = await res.text();

      if (!res.ok || !text) {
        alert("Upload failed");
        return;
      }

      const data = JSON.parse(text);

      setSummary(data.summary || null);
      setAverages(data.averages || null);
      setTypes(data.type_distribution || null);
      setRows(data.rows || []);
      fetchHistory();
    } catch (err) {
      console.error("UPLOAD FAILED:", err);
      alert("Upload failed");
    }
  };

  /* ---------------- UI ---------------- */
  return (
    <div className={`page ${dark ? "dark" : ""}`}>
      <button className="mode-toggle" onClick={() => setDark(!dark)}>
        {dark ? "☀ Light Mode" : "🌙 Dark Mode"}
      </button>

      <h1>Chemical Equipment CSV Analyzer</h1>

      {/* Upload */}
      <div className="upload-card">
        <input
          type="file"
          id="file"
          hidden
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <label htmlFor="file" className="file-btn">
          Choose CSV File
        </label>
        <span>{file ? file.name : "No file selected"}</span>
        <button onClick={upload}>Upload</button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="card">
          <h2>Summary</h2>
          <div className="summary-grid">
            <div>Total Equipment<br /><b>{summary.total_equipment}</b></div>
            <div>Avg Flowrate<br /><b>{summary.avg_flowrate}</b></div>
            <div>Max Pressure<br /><b>{summary.max_pressure}</b></div>
            <div>
              Temp Range<br />
              <b>{summary.temperature_range?.join(" – ")}</b>
            </div>
          </div>
        </div>
      )}

      {/* ===== CHARTS ROW (BAR + PIE) ===== */}
      {averages && types && (
        <div className="card">
          <h2>Visual Analytics</h2>

          <div className="charts-row">
            {/* Bar Chart */}
            <div className="chart-box">
              <Bar
                data={{
                  labels: ["Flowrate", "Pressure", "Temperature"],
                  datasets: [
                    {
                      label: "Averages",
                      data: [
                        averages.flowrate,
                        averages.pressure,
                        averages.temperature,
                      ],
                      backgroundColor: ["#4CAF50", "#2196F3", "#FF9800"],
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                }}
              />
            </div>

            {/* Pie Chart */}
            <div className="chart-box">
              <Pie
                data={{
                  labels: Object.keys(types),
                  datasets: [
                    {
                      data: Object.values(types),
                      backgroundColor: [
                        "#42A5F5",
                        "#66BB6A",
                        "#FFA726",
                        "#AB47BC",
                        "#EC407A",
                      ],
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                }}
              />
            </div>
          </div>
        </div>
      )}
      <button
  style={{
    marginTop: "20px",
    padding: "12px 20px",
    backgroundColor: "#16a34a",
    color: "white",
    borderRadius: "8px",
    fontWeight: "bold",
    border: "none",
    cursor: "pointer"
  }}
  onClick={() => {
    window.open("http://127.0.0.1:8000/api/report/pdf/", "_blank");
  }}
>
  Download Report as PDF
</button>


      {/* Equipment Table */}
      {rows.length > 0 && (
        <div className="card">
          <h2>Equipment Details</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Type</th>
                <th>Flowrate</th>
                <th>Pressure</th>
                <th>Temperature</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.name}</td>
                  <td>{r.type}</td>
                  <td>{r.flowrate}</td>
                  <td>{r.pressure}</td>
                  <td>{r.temperature}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* History */}
      <div className="card">
        <h2>Past 5 Sample Details</h2>
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Total</th>
              <th>Avg Flowrate</th>
              <th>Max Pressure</th>
              <th>Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h) => (
              <tr key={h.id}>
                <td>{h.filename}</td>
                <td>{h.total_equipment}</td>
                <td>{h.avg_flowrate}</td>
                <td>{h.max_pressure}</td>
                <td>{new Date(h.uploaded_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
