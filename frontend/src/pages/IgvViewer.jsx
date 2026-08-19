import { useRef, useState, useEffect } from "react";
import { Link } from "react-router-dom";
import igv from "igv";
import { useAuth } from "../contexts/AuthContext";
import { getUploadedFiles, downloadFile } from "../api/files";

const SUPPORTED_EXTENSIONS = {
  gbk:   [".gbk", ".gb", ".genbank"],
  fasta:  [".fasta", ".fa", ".fna"],
  fastq:  [".fastq", ".fastq.gz", ".fq", ".fq.gz"],
};

const TYPE_BADGE = {
  gbk:   { label: "GBK",   color: "#2563eb", bg: "#dbeafe" },
  fasta:  { label: "FASTA", color: "#15803d", bg: "#dcfce7" },
  fastq:  { label: "FASTQ", color: "#b45309", bg: "#fef3c7" },
};

function getFileType(filename) {
  if (!filename) return null;
  const lower = filename.toLowerCase();
  for (const [type, exts] of Object.entries(SUPPORTED_EXTENSIONS)) {
    if (exts.some((ext) => lower.endsWith(ext))) return type;
  }
  return null;
}

function extractLocusName(gbkText) {
  const match = gbkText.match(/^LOCUS\s+(\S+)/m);
  return match ? match[1] : "sequence";
}

function gbkToFasta(gbkText, locusName) {
  const originMatch = gbkText.match(/ORIGIN([\s\S]*?)\/\//);
  if (!originMatch) return null;
  const seq = originMatch[1].replace(/[\d\s]/g, "").toUpperCase();
  return { fasta: `>${locusName}\n${seq}`, length: seq.length };
}

function parseFastaHeader(fastaText) {
  const lines = fastaText.split("\n");
  const name = lines[0].replace(">", "").split(/\s+/)[0];
  const seq = lines.slice(1).join("").replace(/\s/g, "");
  return { name, length: seq.length };
}

export default function IgvViewer() {
  const { token } = useAuth();
  const igvDiv = useRef(null);
  const browserRef = useRef(null);

  const [supportedFiles, setSupportedFiles] = useState([]);
  const [filesLoading, setFilesLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [loadedFile, setLoadedFile] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchFiles() {
      const files = await getUploadedFiles(token);
      setSupportedFiles(files.filter((f) => getFileType(f.original_filename) !== null));
      setFilesLoading(false);
    }
    if (token) fetchFiles();
  }, [token]);

  async function loadGbk(text, filename) {
    const locusName = extractLocusName(text);
    const result = gbkToFasta(text, locusName);
    if (!result) throw new Error("Could not find sequence (ORIGIN section) in this GBK file.");

    const { fasta, length } = result;
    const fastaUrl = URL.createObjectURL(new Blob([fasta], { type: "text/plain" }));
    const gbkUrl   = URL.createObjectURL(new Blob([text], { type: "text/plain" }));

    return igv.createBrowser(igvDiv.current, {
      locus: `${locusName}:1-${length}`,
      genome: { id: locusName, name: locusName, fastaURL: fastaUrl, indexed: false },
      tracks: [{
        name: filename,
        url: gbkUrl,
        format: "gbk",
        type: "annotation",
        displayMode: "EXPANDED",
        color: "#2563eb",
      }],
    });
  }

  async function loadFasta(text, filename) {
    const { name, length } = parseFastaHeader(text);
    const fastaUrl = URL.createObjectURL(new Blob([text], { type: "text/plain" }));

    return igv.createBrowser(igvDiv.current, {
      locus: `${name}:1-${length}`,
      genome: { id: name, name: filename, fastaURL: fastaUrl, indexed: false },
    });
  }

  async function loadIntoIgv(uploadId, filename) {
    if (!igvDiv.current) return;

    const fileType = getFileType(filename);

    // FASTQ = raw reads, needs alignment to a reference first — not viewable directly
    if (fileType === "fastq") {
      setSelectedId(uploadId);
      setError(
        "FASTQ files contain raw sequencing reads. To visualize in IGV they first need to be aligned to a reference genome (BAM format). Raw FASTQ display is not supported yet."
      );
      return;
    }

    setLoading(true);
    setError(null);
    setLoadedFile(null);
    setSelectedId(uploadId);

    const blob = await downloadFile(token, uploadId);
    if (!blob) {
      setError("Failed to download the file from the server.");
      setLoading(false);
      return;
    }

    const text = await blob.text();

    if (browserRef.current) {
      igv.removeBrowser(browserRef.current);
      browserRef.current = null;
    }
    igvDiv.current.innerHTML = "";

    try {
      const browser =
        fileType === "gbk"
          ? await loadGbk(text, filename)
          : await loadFasta(text, filename);

      browserRef.current = browser;
      setLoadedFile(filename);
    } catch (err) {
      console.error("IGV load error:", err);
      setError(err.message || "Failed to render the file. Check the browser console for details.");
    }

    setLoading(false);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2 style={{ marginBottom: "4px" }}>IGV Genome Viewer</h2>
      <p style={{ color: "#64748b", fontSize: "14px", marginBottom: "24px" }}>
        Select an uploaded sequence file to visualize. GBK shows sequence + gene annotations. FASTA shows sequence only.
      </p>

      {/* FILE LIST */}
      <div style={{ marginBottom: "20px", border: "1px solid #e2e8f0", borderRadius: "8px", overflow: "hidden" }}>
        <div style={{ padding: "12px 16px", backgroundColor: "#f8fafc", borderBottom: "1px solid #e2e8f0", fontWeight: "600", fontSize: "14px", color: "#475569" }}>
          Your Sequence Files
        </div>

        {filesLoading ? (
          <p style={{ padding: "16px", color: "#64748b", fontSize: "14px" }}>Loading files...</p>
        ) : supportedFiles.length === 0 ? (
          <div style={{ padding: "16px", fontSize: "14px", color: "#64748b" }}>
            No sequence files uploaded yet.{" "}
            <Link to="/uploads" style={{ color: "#2563eb" }}>Go to Uploads</Link>{" "}
            to add a GBK or FASTA file.
          </div>
        ) : (
          supportedFiles.map((file) => {
            const type  = getFileType(file.original_filename);
            const badge = TYPE_BADGE[type];
            return (
              <div
                key={file.upload_id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "12px 16px",
                  borderBottom: "1px solid #f1f5f9",
                  backgroundColor: selectedId === file.upload_id ? "#eff6ff" : "transparent",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  <span style={{ padding: "2px 8px", borderRadius: "12px", fontSize: "11px", fontWeight: "700", color: badge.color, backgroundColor: badge.bg }}>
                    {badge.label}
                  </span>
                  <span style={{ fontSize: "14px", color: "#0f172a" }}>
                    {file.original_filename}
                  </span>
                </div>
                <button
                  onClick={() => loadIntoIgv(file.upload_id, file.original_filename)}
                  disabled={loading}
                  style={{
                    padding: "6px 14px",
                    backgroundColor: selectedId === file.upload_id ? "#1d4ed8" : "#2563eb",
                    color: "#ffffff",
                    border: "none",
                    borderRadius: "6px",
                    fontSize: "13px",
                    fontWeight: "500",
                    cursor: loading ? "not-allowed" : "pointer",
                    opacity: loading ? 0.6 : 1,
                  }}
                >
                  {selectedId === file.upload_id && loading ? "Loading..." : "View"}
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* STATUS */}
      {loadedFile && !loading && (
        <p style={{ marginBottom: "12px", fontSize: "14px", color: "#16a34a", fontWeight: "500" }}>
          ✓ Viewing: {loadedFile}
        </p>
      )}
      {error && (
        <p style={{ marginBottom: "12px", fontSize: "14px", color: "#991b1b" }}>{error}</p>
      )}

      {/* IGV CONTAINER */}
      <div
        ref={igvDiv}
        style={{ border: "1px solid #e2e8f0", borderRadius: "8px", minHeight: "500px", backgroundColor: "#ffffff" }}
      />
    </div>
  );
}
