import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";
import { fetchTimepointConfig, fetchTimepointResults } from "../../api/results";

export function TimepointResults({
  projectId: propProjectId,
  authToken: propToken,
}) {
  // Support either props (from ProjectDetail) OR route params/context (standalone route)
  const params = useParams();
  const context = useAuth();

  const projectId = propProjectId || params.projectId;
  const token = propToken || context?.token;

  const [results, setResults] = useState([]);
  const [resultsMeta, setResultsMeta] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCondition, setSelectedCondition] = useState("ALL");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const [configData, resultsData] = await Promise.all([
        fetchTimepointConfig(token, projectId),
        fetchTimepointResults(token, projectId),
      ]);
      setConfig(configData);
      // Results come back as { id, result_json: [...], ran_at, filename, ... }
      if (resultsData && Array.isArray(resultsData.result_json)) {
        setResults(resultsData.result_json);
        setResultsMeta({ ran_at: resultsData.ran_at, filename: resultsData.filename });
      } else {
        setResults([]);
      }
      setLoading(false);
    }

    if (token && projectId) {
      loadData();
    }
  }, [token, projectId]);

  // Group fields are dynamic — each one is its own column in the result row.
  // We find ALL keys that aren't known metrics, then join their values for display.
  const KNOWN_KEYS = new Set([
    "cv", "snr", "rank", "smoothness", "correlation",
    "dynamic_range", "composite_score", "ideal_time_window",
  ]);
  const conditionKeys =
    results.length > 0
      ? Object.keys(results[0]).filter((k) => !KNOWN_KEYS.has(k))
      : [];

  const getLabel = (row) => conditionKeys.map((k) => row[k]).join(" | ");

  if (loading) {
    return <div style={styles.paddingContainer}>Loading pipeline results...</div>;
  }

  if (results.length === 0) {
    return <div style={styles.paddingContainer}>No results found for this project.</div>;
  }

  const conditions = [
    "ALL",
    ...Array.from(new Set(results.map((r) => getLabel(r)).filter(Boolean))),
  ];

  const filteredResults =
    selectedCondition === "ALL"
      ? results
      : results.filter((r) => getLabel(r) === selectedCondition);

  const topRankings = results.filter((r) => r.rank === 1);

  return (
    <div style={styles.container}>

      {/* CONFIG SUMMARY */}
      {config && (
        <div style={styles.configBox}>
          <h4 style={styles.configTitle}>Run Configuration</h4>
          <div style={styles.configGrid}>
            <div>
              <span style={styles.configLabel}>File</span>
              {resultsMeta?.filename || config.file}
            </div>
            <div>
              <span style={styles.configLabel}>Group Fields</span>
              {config.group_fields?.join(", ")}
            </div>
            <div>
              <span style={styles.configLabel}>Dose Field</span>
              {config.dose_field}
            </div>
            <div>
              <span style={styles.configLabel}>OD Field</span>
              {config.od_field}
            </div>
            <div>
              <span style={styles.configLabel}>Time Field</span>
              {config.time_field}
            </div>
            {resultsMeta?.ran_at && (
              <div>
                <span style={styles.configLabel}>Ran At</span>
                {new Date(resultsMeta.ran_at).toLocaleString()}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TOP HIGHLIGHTS */}
      <h3 style={styles.header}>Top Recommended Time Windows</h3>
      <div style={styles.cardGrid}>
        {topRankings.map((item, idx) => (
          <div key={idx} style={styles.card}>
            <div style={styles.cardTag}>{getLabel(item)}</div>
            <div style={styles.cardWindow}>{item.ideal_time_window}</div>
            <div style={styles.cardScore}>
              Score: <strong>{((item.composite_score || 0) * 100).toFixed(1)}%</strong>
            </div>
            <div style={styles.cardSubtext}>
              SNR: {item.snr?.toFixed(2)} | Corr: {item.correlation?.toFixed(2)}
            </div>
          </div>
        ))}
      </div>

      {/* FILTER BUTTONS */}
      <div style={styles.filterBar}>
        <strong style={{ fontSize: "14px" }}>Filter Groups:</strong>
        {conditions.map((cond) => (
          <button
            key={cond}
            onClick={() => setSelectedCondition(cond)}
            style={{
              ...styles.filterBtn,
              ...(selectedCondition === cond ? styles.filterBtnActive : {}),
            }}
          >
            {cond}
          </button>
        ))}
      </div>

      {/* MAIN DATA TABLE */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.tableHeader}>
              <th style={styles.th}>Rank</th>
              <th style={styles.th}>Group</th>
              <th style={styles.th}>Ideal Time Window</th>
              <th style={styles.th}>Composite Score</th>
              <th style={styles.th}>CV</th>
              <th style={styles.th}>SNR</th>
              <th style={styles.th}>Correlation</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((row, index) => (
              <tr
                key={index}
                style={{
                  ...styles.tr,
                  backgroundColor: row.rank === 1 ? "#f0fdf4" : "transparent",
                }}
              >
                <td style={styles.td}>
                  <span style={row.rank === 1 ? styles.badgeRankOne : styles.badgeRank}>
                    #{row.rank}
                  </span>
                </td>
                <td style={styles.td}>
                  <strong>{getLabel(row)}</strong>
                </td>
                <td style={styles.td}>{row.ideal_time_window}</td>
                <td style={styles.td}>
                  {((row.composite_score || 0) * 100).toFixed(2)}%
                </td>
                <td style={styles.td}>{row.cv?.toFixed(4) ?? "-"}</td>
                <td style={styles.td}>{row.snr?.toFixed(3) ?? "-"}</td>
                <td style={styles.td}>{row.correlation?.toFixed(4) ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const styles = {
  container: { fontFamily: "sans-serif", marginTop: "16px" },
  paddingContainer: { padding: "20px", color: "#64748b", textAlign: "center" },

  configBox: {
    backgroundColor: "#f8fafc",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    padding: "16px 20px",
    marginBottom: "24px",
  },
  configTitle: {
    margin: "0 0 12px 0",
    fontSize: "14px",
    fontWeight: "700",
    color: "#475569",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },
  configGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    gap: "8px",
    fontSize: "13px",
    color: "#334155",
  },
  configLabel: {
    fontWeight: "600",
    color: "#64748b",
    marginRight: "6px",
  },

  header: { margin: "0 0 12px 0", fontSize: "18px", color: "#0f172a" },
  cardGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
    gap: "12px",
    marginBottom: "20px",
  },
  card: {
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    padding: "12px 16px",
    backgroundColor: "#ffffff",
    boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
  },
  cardTag: {
    fontSize: "12px",
    fontWeight: "700",
    color: "#2563eb",
    marginBottom: "4px",
  },
  cardWindow: { fontSize: "16px", fontWeight: "700", color: "#0f172a" },
  cardScore: { fontSize: "13px", color: "#16a34a", marginTop: "4px" },
  cardSubtext: { fontSize: "11px", color: "#64748b", marginTop: "4px" },
  filterBar: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "16px",
    flexWrap: "wrap",
  },
  filterBtn: {
    padding: "6px 12px",
    borderRadius: "16px",
    border: "1px solid #cbd5e1",
    backgroundColor: "#ffffff",
    cursor: "pointer",
    fontSize: "13px",
  },
  filterBtnActive: {
    backgroundColor: "#2563eb",
    color: "#ffffff",
    borderColor: "#2563eb",
  },
  tableWrapper: {
    overflowX: "auto",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    textAlign: "left",
    fontSize: "14px",
  },
  tableHeader: {
    backgroundColor: "#f8fafc",
    borderBottom: "1px solid #e2e8f0",
  },
  th: { padding: "10px 14px", fontWeight: "600", color: "#475569" },
  tr: { borderBottom: "1px solid #f1f5f9" },
  td: { padding: "10px 14px", color: "#334155" },
  badgeRankOne: {
    padding: "2px 8px",
    backgroundColor: "#dcfce7",
    color: "#15803d",
    borderRadius: "12px",
    fontWeight: "700",
    fontSize: "12px",
  },
  badgeRank: {
    padding: "2px 8px",
    backgroundColor: "#f1f5f9",
    color: "#64748b",
    borderRadius: "12px",
    fontWeight: "600",
    fontSize: "12px",
  },
};

export default TimepointResults;
