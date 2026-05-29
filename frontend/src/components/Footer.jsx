import "./Footer.css";

function Footer() {
  return (
    <footer className="site-footer">
      <hr className="divider" />

      <p>&copy; {new Date().getFullYear()} DigiBio Project</p>

      <p className="footer-links">
        <a href="https://digibio.ut.ee/" target="_blank" rel="noreferrer">
          Website
        </a>

        <span> | </span>

        <a
          href="https://github.com/estonian-biofoundry"
          target="_blank"
          rel="noreferrer"
        >
          GitHub
        </a>

        <span> | </span>

        <a href="https://www.linkedin.com/" target="_blank" rel="noreferrer">
          Linkedin
        </a>

        <span> | </span>

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

export default Footer;
