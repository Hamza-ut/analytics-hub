export default function Footer() {
  return (
    <footer
      style={{
        padding: "15px",
        backgroundColor: "#f8f9fa",
        color: "#8a8888",
        textAlign: "center",
        fontSize: "14px",
        borderTop: "1px solid #dee2e6",
      }}
    >
      <p>© 2026 Biofoundry Project</p>
      <p>
        <a
          href="https://digibio.ut.ee/biofoundry/"
          target="_blank"
          rel="noreferrer"
        >
          Website
        </a>{" "}
        |{" "}
        <a
          href="https://gitlab.cs.ut.ee/estonian-biofoundry"
          target="_blank"
          rel="noreferrer"
        >
          GitLab
        </a>{" "}
        |{" "}
        <a
          href="https://www.instagram.com/digibio.est/"
          target="_blank"
          rel="noreferrer"
        >
          Instagram
        </a>
      </p>
    </footer>
  );
}
