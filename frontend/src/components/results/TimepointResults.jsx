import React, { useEffect, useState, useContext } from "react";
import { useParams } from "react-router-dom";
import { AuthContext } from "../../contexts/AuthContext";
import { fetchProjectResults } from "../../api/results";

export function TimepointResults({
  projectId: propProjectId,
  authToken: propToken,
}) {
  // Support either props OR route params/context automatically
  const params = useParams();
  const context = useContext(AuthContext);

  const projectId = propProjectId || params.projectId;
  const token = propToken || context?.token;

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCondition, setSelectedCondition] = useState("ALL");

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const data = await fetchProjectResults(token, projectId);
      if (Array.isArray(data)) {
        setResults(data);
      } else {
        setResults([]);
      }
      setLoading(false);
    }

    if (token && projectId) {
      loadData();
    }
  }, [token, projectId]);

  if (loading) {
    return (
      <div style={styles.paddingContainer}>Loading pipeline results...</div>
    );
  }

  if (!results || results.length === 0) {
    return (
      <div style={styles.paddingContainer}>
        No results found for this project.
      </div>
    );
  }

  // Extract unique list of conditions for filter buttons
  const conditions = [
    "ALL",
    ...Array.from(new Set(results.map((r) => r.condition).filter(Boolean))),
  ];

  // Filter dataset by condition
  const filteredResults =
    selectedCondition === "ALL"
      ? results
      : results.filter((r) => r.condition === selectedCondition);

  // Grab Rank #1 items across conditions for highlight cards
  const topRankings = results.filter((r) => r.rank === 1);

  return (
    <div style={styles.container}>
      {/* 1. TOP HIGHLIGHTS */}
      <h3 style={styles.header}>Top Recommended Time Windows</h3>
      <div style={styles.cardGrid}>
        {topRankings.map((item, idx) => (
          <div key={idx} style={styles.card}>
            <div style={styles.cardTag}>{item.condition}</div>
            <div style={styles.cardWindow}>{item.ideal_time_window} </div>
            <div style={styles.cardScore}>
              Score:{" "}
              <strong>{((item.composite_score || 0) * 100).toFixed(1)}%</strong>
            </div>
            {item.details && (
              <div style={styles.cardSubtext}>
                SNR: {item.details.snr?.toFixed(2)} | Corr:{" "}
                {item.details.correlation?.toFixed(2)}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 2. FILTER BUTTONS */}
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

      {/* 3. MAIN DATA TABLE */}
      <div style={styles.tableWrapper}>
        <table style={styles.table}>
          <thead>
            <tr style={styles.tableHeader}>
              <th style={styles.th}>Rank</th>
              <th style={styles.th}>Group Field/s</th>
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
                  <span
                    style={
                      row.rank === 1 ? styles.badgeRankOne : styles.badgeRank
                    }
                  >
                    #{row.rank}
                  </span>
                </td>
                <td style={styles.td}>
                  <strong>{row.condition}</strong>
                </td>
                <td style={styles.td}>{row.ideal_time_window}</td>
                <td style={styles.td}>
                  {((row.composite_score || 0) * 100).toFixed(2)}%
                </td>
                <td style={styles.td}>{row.details?.cv?.toFixed(4) ?? "-"}</td>
                <td style={styles.td}>{row.details?.snr?.toFixed(3) ?? "-"}</td>
                <td style={styles.td}>
                  {row.details?.correlation?.toFixed(4) ?? "-"}
                </td>
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
