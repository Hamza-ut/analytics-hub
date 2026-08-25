import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { fetchTimepointConfig, fetchTimepointResults } from "../api/results";

import styles from "./Practice.module.css";

export default function Practice() {
  const { token } = useAuth();
  const projectId = "prj_9c1456";
  const [config, setConfig] = useState(null);
  const [resultsData, setResultsData] = useState(null);

  const [selectedGroupFilter, setSelectedGroupFilter] = useState("ALL");

  useEffect(() => {
    if (token && projectId) {
      fetchTimepointConfig(token, projectId).then((res) => {
        setConfig(res);
      });

      fetchTimepointResults(token, projectId).then((res) => {
        setResultsData(res); // Store the FULL object containing `filename`
      });
    }
  }, [token, projectId]);

  // Extract the results array cleanly
  const results =
    resultsData?.result_json || (Array.isArray(resultsData) ? resultsData : []);

  // Safety check while loading API
  if (!results) {
    return <div>Loading results...</div>;
  }

  // Helper function to extract grouping label dynamically
  const getGroupFields = (item) => {
    const fixedKeys = [
      "ideal_time_window",
      "composite_score",
      "rank",
      "snr",
      "correlation",
      "cv",
      "dynamic_range",
      "smoothness",
    ];

    return Object.keys(item)
      .filter((k) => !fixedKeys.includes(k))
      .map((k) => item[k])
      .join(" | ");
  };

  const FilterGroupFields = [
    "ALL",
    ...Array.from(new Set(results.map((item) => getGroupFields(item)))),
  ];

  // Find the Rank #1 recommendation for EACH unique group field
  const topRecommendationsPerGroup = Array.from(
    new Set(results.map((item) => getGroupFields(item))),
  )
    .map((groupName) => {
      // Find all items matching this group
      const groupItems = results.filter(
        (item) => getGroupFields(item) === groupName,
      );

      // Return the item with rank 1 (or default to the first one)
      return (
        groupItems.find((item) => Number(item.rank) === 1) || groupItems[0]
      );
    })
    .filter((item) => {
      // Respect the active top filter bar selection if one is picked
      if (selectedGroupFilter !== "ALL") {
        return getGroupFields(item) === selectedGroupFilter;
      }
      return true;
    });

  return (
    <div>
      <h2>Results</h2>

      {/* Run Configuration Box */}
      {config && (
        <div className={styles.configBox}>
          <h3>Run Configuration</h3>
          <p>
            <strong>File:</strong> {resultsData?.filename || "—"}
          </p>
          <p>
            <strong>Group Fields:</strong>{" "}
            {config.group_fields?.join(", ") || "—"}
          </p>
          <p>
            <strong>Dose Field:</strong> {config.dose_field || "—"}
          </p>
          <p>
            <strong>OD Field:</strong> {config.od_field || "—"}
          </p>
          <p>
            <strong>Time Field:</strong> {config.time_field || "—"}
          </p>
        </div>
      )}

      <div className={styles.sectionDivider} />
      {/* Top Recommended Time Windows (Summary) */}
      <h3>Top Recommended Time Windows</h3>

      <div className={styles.cardsGrid}>
        {topRecommendationsPerGroup.map((item, index) => {
          const groupFields = getGroupFields(item);

          return (
            <div key={index} className={styles.summaryCard}>
              <div className={styles.cardGroupHeader}>{groupFields}</div>

              <div className={styles.cardMainMetric}>
                <span className={styles.timeLabel}>Window:</span>
                <span className={styles.timeValue}>
                  {item.ideal_time_window}
                </span>
              </div>

              <div className={styles.cardSubMetric}>
                <span>Score:</span>
                <strong>{parseFloat(item.composite_score).toFixed(1)}</strong>
              </div>
            </div>
          );
        })}
      </div>

      <div className={styles.sectionDivider} />

      {/* Filter Buttons */}
      <div className={styles.filterContainer}>
        <strong>Filter:</strong>

        {FilterGroupFields.map((cond) => (
          <button
            key={cond}
            onClick={() => setSelectedGroupFilter(cond)}
            className={` ${selectedGroupFilter === cond ? styles.filterBtn + " " + styles.active : styles.filterBtn}`}
          >
            {cond}
          </button>
        ))}
      </div>
      <p className={styles.helperText}>
        * In case of multiple group fields, they are separated by " | "
      </p>

      <br />

      <table className={styles.resultsTable}>
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
          {results.map((item, index) => {
            const groupFields = getGroupFields(item);

            if (
              selectedGroupFilter !== "ALL" &&
              groupFields !== selectedGroupFilter
            ) {
              return null;
            }

            // Simple class assignment based on rank
            const rankNum = Number(item.rank);
            let rankClass = "";
            if (rankNum === 1) rankClass = styles.rank1;
            if (rankNum === 2) rankClass = styles.rank2;
            if (rankNum === 3) rankClass = styles.rank3;

            return (
              <tr key={index} className={rankClass}>
                <td>#{rankNum}</td>
                <td>{groupFields}</td>
                <td>{item.ideal_time_window}</td>
                <td>{parseFloat(item.composite_score).toFixed(2)}</td>
                <td>{parseFloat(item.snr).toFixed(2)}</td>
                <td>{parseFloat(item.correlation).toFixed(2)}</td>
                <td>{parseFloat(item.cv).toFixed(2)}</td>
                <td>{parseFloat(item.dynamic_range).toFixed(2)}</td>
                <td>{parseFloat(item.smoothness).toFixed(2)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
