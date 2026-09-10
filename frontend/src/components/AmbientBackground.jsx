import "./AmbientBackground.css";

export default function AmbientBackground() {
  return (
    <div className="ambient" aria-hidden="true">
      <div className="ambient__grid" />
      <div className="ambient__shape ambient__shape--a" />
      <div className="ambient__shape ambient__shape--b" />
      <div className="ambient__shape ambient__shape--c" />
    </div>
  );
}
