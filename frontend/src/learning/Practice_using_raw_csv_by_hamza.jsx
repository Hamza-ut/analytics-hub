import { useState } from "react";
import valloRaw from "./timepoint_vallo_result.csv?raw";
import sfRaw from "./timepoint_sf_result.csv?raw";

export default function Practice() {
  const [activeDataset, setActiveDataset] = useState(null);
  const [selectedGroupFilter, setSelectedGroupFilter] = useState("ALL");

  const currentRawData =
    activeDataset === "vallo"
      ? valloRaw
      : activeDataset === "sf"
        ? sfRaw
        : null;

  const convertedRawData = currentRawData
    ? currentRawData.trim().split("\n")
    : [];

  const FilterGroupFields = [
    "ALL",
    ...Array.from(
      new Set(
        convertedRawData.slice(1).map((line) => {
          const cells = line.split(",");
          return cells.slice(0, -8).join(" | ");
        }),
      ),
    ),
  ];

  return (
    <div>
      <h2>test result conf</h2>

      <button
        onClick={() => setActiveDataset("vallo")}
        style={{
          backgroundColor: activeDataset === "vallo" ? "#1E6738" : "#f5f5f5",
        }}
      >
        timepoint_vallo
      </button>

      <br />
      <br />
      <button
        onClick={() => setActiveDataset("sf")}
        style={{
          backgroundColor: activeDataset === "sf" ? "#1E6738" : "#f5f5f5",
        }}
      >
        timepoint_sf
      </button>

      <br />

      {/* CARD DISPLAY */}
      <h3>Top Recommended Time Windows</h3>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
          gap: "12px",
          marginBottom: "20px",
        }}
      >
        {convertedRawData
          .slice(1)
          .filter((line) => line.split(",").at(-7) === "1")
          .map((line, idx) => {
            const cells = line.split(",");
            const groupFields = cells.slice(0, -8).join(" | ");
            const ideal_time_window = cells.at(-8);
            const composite_score = parseFloat(cells.at(-6)) || 0;

            return (
              <div
                key={idx}
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: "8px",
                  padding: "12px 16px",
                  backgroundColor: "#ffffff",
                  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
                }}
              >
                <div
                  style={{
                    fontSize: "12px",
                    fontWeight: "700",
                    color: "#2563eb",
                    marginBottom: "4px",
                  }}
                >
                  {groupFields}
                </div>
                <div
                  style={{
                    fontSize: "16px",
                    fontWeight: "700",
                    color: "#0f172a",
                  }}
                >
                  {ideal_time_window}
                </div>
                <div
                  style={{
                    fontSize: "13px",
                    color: "#16a34a",
                    marginTop: "4px",
                  }}
                >
                  Score: <strong>{(composite_score * 100).toFixed(1)}%</strong>
                </div>
              </div>
            );
          })}
      </div>

      {/* Filter Buttons */}
      <div
        style={{
          marginBottom: "16px",
          display: "flex",
          gap: "8px",
          flexWrap: "wrap",
        }}
      >
        <strong>Filter Groups:</strong>
        {FilterGroupFields.map((cond) => (
          <button
            key={cond}
            onClick={() => setSelectedGroupFilter(cond)}
            style={{
              padding: "4px 8px",
              cursor: "pointer",
              backgroundColor:
                selectedGroupFilter === cond ? "#2563eb" : "#ffffff",
              color: selectedGroupFilter === cond ? "#ffffff" : "#000000",
              border: "1px solid #ccc",
              borderRadius: "4px",
            }}
          >
            {cond}
          </button>
        ))}
      </div>

      <br />

      <table
        style={{
          border: "1px solid #ccc",
          borderCollapse: "collapse",
          width: "100%",
          textAlign: "left",
        }}
      >
        <thead>
          <tr>
            <th>Rank</th>
            <th>Group Field(s)</th>
            <th>Ideal Time Window</th>
            <th>Composite Score</th>
            <th>SNR</th>
            <th>Correlation</th>
            <th>CV</th>
            <th>Dynamic Range</th>
            <th>Smoothness</th>
          </tr>
        </thead>

        <tbody>
          {convertedRawData.slice(1).map((line, index) => {
            const cells = line.split(",");

            // Fixed metrics read from the END of the row
            const smoothness = cells.at(-1);
            const dynamic_range = cells.at(-2);
            const cv = cells.at(-3);
            const correlation = cells.at(-4);
            const snr = cells.at(-5);
            const composite_score = cells.at(-6);
            const rank = cells.at(-7);
            const ideal_time_window = cells.at(-8);

            // Everything before the last 8 items goes to group field/s
            const groupFields = cells.slice(0, -8).join(" | ");

            if (
              selectedGroupFilter !== "ALL" &&
              groupFields !== selectedGroupFilter
            ) {
              return null;
            }

            // Convert rank string to number
            const rankNum = Number(rank);

            // Set 3 distinct colors for top 3 ranks
            let rowBackgroundColor = "transparent";

            if (rankNum === 1) {
              rowBackgroundColor = "#dcfce7"; // Darkest green (Rank 1)
            } else if (rankNum === 2) {
              rowBackgroundColor = "#e2f7e8"; // Medium lighter green (Rank 2)
            } else if (rankNum === 3) {
              rowBackgroundColor = "#f0fdf4"; // Ultra-light green from TimepointResults (Rank 3)
            }

            return (
              <tr key={index} style={{ backgroundColor: rowBackgroundColor }}>
                <td>#{rankNum}</td>
                <td>{groupFields}</td>
                <td>{ideal_time_window}</td>
                <td>{parseFloat(composite_score).toFixed(2)}</td>
                <td>{parseFloat(snr).toFixed(2)}</td>
                <td>{parseFloat(correlation).toFixed(2)}</td>
                <td>{parseFloat(cv).toFixed(2)}</td>
                <td>{parseFloat(dynamic_range).toFixed(2)}</td>
                <td>{parseFloat(smoothness).toFixed(2)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
