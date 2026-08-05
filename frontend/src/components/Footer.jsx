export default function Footer() {
  return (
    <footer
      style={{
        marginTop: "auto",
        padding: "20px",
        backgroundColor: "#f8f9fa",
        color: "#6c757d",
        textAlign: "center",
        fontSize: "14px",
        borderTop: "1px solid #dee2e6",
      }}
    >
      <p style={{ margin: "0 0 8px 0" }}>
        © {new Date().getFullYear()} Biofoundry Project, University of Tartu.
      </p>

      <div style={{ display: "flex", justifyContent: "center", gap: "15px" }}>
        <a
          href="https://digibio.ut.ee/biofoundry/"
          target="_blank"
          rel="noreferrer"
          style={{ color: "#0d6efd", textDecoration: "none" }}
        >
          Website
        </a>
        <span>•</span>
        <a
          href="https://gitlab.cs.ut.ee/estonian-biofoundry"
          target="_blank"
          rel="noreferrer"
          style={{ color: "#0d6efd", textDecoration: "none" }}
        >
          GitLab
        </a>
        <span>•</span>
        <a
          href="https://www.instagram.com/digibio.est/"
          target="_blank"
          rel="noreferrer"
          style={{ color: "#0d6efd", textDecoration: "none" }}
        >
          Instagram
        </a>
      </div>
    </footer>
  );
}
