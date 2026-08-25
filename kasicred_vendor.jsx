const { useState } = React;

const ratingsFeed = [
  { stars: 5, amount: 45, time: "2m ago", hash: "0x8f2a1c" },
  { stars: 4, amount: 20, time: "1h ago", hash: "0x3c1e94" },
  { stars: 5, amount: 60, time: "3h ago", hash: "0xa71bd0" },
  { stars: 5, amount: 15, time: "Yesterday", hash: "0x0e44f2" },
  { stars: 3, amount: 30, time: "Yesterday", hash: "0x9b2c77" },
];

const weeklyBars = [4, 6, 5, 8, 7, 9, 6];

function Stars({ n }) {
  return (
    <span style={{ letterSpacing: 1 }}>
      {"★".repeat(n)}
      <span style={{ opacity: 0.25 }}>{"★".repeat(5 - n)}</span>
    </span>
  );
}

export default function KasiCredVendor() {
  const [tab, setTab] = useState("signup");
  const [form, setForm] = useState({ name: "", area: "", phone: "", sells: "" });
  const [submitted, setSubmitted] = useState(false);

  const update = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <div
      style={{
        fontFamily: "Inter, system-ui, sans-serif",
        background: "#14171A",
        color: "#F5F0E6",
        minHeight: 480,
        padding: "28px 20px",
        borderRadius: 16,
        maxWidth: 420,
        margin: "0 auto",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');
        .kc-display { font-family: 'Space Grotesk', sans-serif; }
        .kc-mono { font-family: 'IBM Plex Mono', monospace; }
        .kc-input {
          width: 100%; box-sizing: border-box; background: #1E2226; border: 1px solid #2B3036;
          color: #F5F0E6; padding: 11px 12px; border-radius: 8px; font-size: 14px; margin-top: 6px;
          outline: none; transition: border-color 0.15s;
        }
        .kc-input:focus { border-color: #F2A93B; }
        .kc-label { font-size: 12px; opacity: 0.65; margin-top: 14px; display: block; }
        .kc-btn {
          width: 100%; background: #F2A93B; color: #14171A; border: none; padding: 13px;
          border-radius: 8px; font-weight: 600; font-size: 14px; margin-top: 20px; cursor: pointer;
        }
        .kc-btn:hover { opacity: 0.92; }
        .kc-tab {
          background: none; border: none; color: #F5F0E6; opacity: 0.5; font-size: 13px;
          padding: 6px 0; cursor: pointer; border-bottom: 2px solid transparent;
        }
        .kc-tab.active { opacity: 1; border-color: #F2A93B; }
      `}</style>

      <div className="kc-display" style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.5 }}>
        Kasi<span style={{ color: "#F2A93B" }}>Cred</span>
      </div>
      <div style={{ fontSize: 12.5, opacity: 0.6, marginTop: 2, marginBottom: 20 }}>
        Build your trust. Bank your sales.
      </div>

      <div style={{ display: "flex", gap: 20, borderBottom: "1px solid #2B3036" }}>
        <button className={`kc-tab ${tab === "signup" ? "active" : ""}`} onClick={() => setTab("signup")}>
          SIGN UP
        </button>
        <button className={`kc-tab ${tab === "dashboard" ? "active" : ""}`} onClick={() => setTab("dashboard")}>
          DASHBOARD
        </button>
      </div>

      {tab === "signup" && !submitted && (
        <div style={{ marginTop: 4 }}>
          <label className="kc-label">Vendor / stall name</label>
          <input className="kc-input" value={form.name} onChange={update("name")} placeholder="e.g. Mama Thandi's Kitchen" />

          <label className="kc-label">Market or area</label>
          <input className="kc-input" value={form.area} onChange={update("area")} placeholder="e.g. Bree Street Market, Jozi" />

          <label className="kc-label">Phone number</label>
          <input className="kc-input" value={form.phone} onChange={update("phone")} placeholder="+27 ..." />

          <label className="kc-label">What do you sell?</label>
          <input className="kc-input" value={form.sells} onChange={update("sells")} placeholder="e.g. Vetkoek, airtime, sweets" />

          <button className="kc-btn" onClick={() => setSubmitted(true)}>
            Create my ledger
          </button>
          <div style={{ fontSize: 11, opacity: 0.45, marginTop: 12, lineHeight: 1.5 }}>
            No app download. No wallet. Ratings and sales are verified on-chain —
            your area name is kept, never your exact location.
          </div>
        </div>
      )}

      {tab === "signup" && submitted && (
        <div style={{ marginTop: 40, textAlign: "center" }}>
          <div style={{ fontSize: 40 }}>✅</div>
          <div className="kc-display" style={{ fontSize: 16, fontWeight: 700, marginTop: 10 }}>
            Ledger created
          </div>
          <div style={{ fontSize: 13, opacity: 0.6, marginTop: 6 }}>
            Print your QR code and start collecting verified sales.
          </div>
          <button className="kc-btn" onClick={() => setTab("dashboard")}>
            View my dashboard
          </button>
        </div>
      )}

      {tab === "dashboard" && (
        <div style={{ marginTop: 18 }}>
          <div style={{ fontSize: 13, opacity: 0.6 }}>Dumela, {form.name || "Vendor"} 👋</div>

          {/* Receipt-style trust score card */}
          <div
            style={{
              marginTop: 14,
              background:
                "repeating-linear-gradient(to bottom, transparent 0 6px, #14171A 6px 12px), #1E2226",
              backgroundPosition: "0 0, 0 0",
              border: "1px dashed #3A4046",
              borderRadius: 4,
              padding: "18px 16px",
              position: "relative",
            }}
          >
            <div className="kc-mono" style={{ fontSize: 10.5, opacity: 0.5, letterSpacing: 1 }}>
              KASICRED TRUST RECEIPT · #0A3F
            </div>
            <div className="kc-display" style={{ fontSize: 34, fontWeight: 700, color: "#F2A93B", marginTop: 4 }}>
              84<span style={{ fontSize: 16, fontWeight: 500, opacity: 0.6 }}> /100</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
              <span style={{ fontSize: 11.5, opacity: 0.6 }}>Trust score</span>
              <span
                style={{
                  fontSize: 10,
                  fontWeight: 600,
                  color: "#14171A",
                  background: "#1B7A6E",
                  padding: "3px 8px",
                  borderRadius: 999,
                }}
              >
                LOAN READY
              </span>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 14, fontSize: 12.5 }}>
              <span style={{ opacity: 0.65 }}>Verified sales</span>
              <span className="kc-mono">128</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 12.5 }}>
              <span style={{ opacity: 0.65 }}>Avg rating</span>
              <span className="kc-mono">4.6 ★</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 12.5 }}>
              <span style={{ opacity: 0.65, color: "#1B7A6E" }}>This week</span>
              <span className="kc-mono" style={{ color: "#1B7A6E" }}>+6 sales</span>
            </div>
          </div>

          {/* weekly bars */}
          <div style={{ display: "flex", alignItems: "flex-end", gap: 6, height: 44, marginTop: 16 }}>
            {weeklyBars.map((v, i) => (
              <div
                key={i}
                style={{
                  flex: 1,
                  height: `${(v / 9) * 100}%`,
                  background: i === weeklyBars.length - 1 ? "#F2A93B" : "#2B3036",
                  borderRadius: 3,
                }}
              />
            ))}
          </div>
          <div style={{ fontSize: 10.5, opacity: 0.4, marginTop: 4 }}>sales, last 7 days</div>

          <div style={{ fontSize: 12, opacity: 0.7, marginTop: 22, marginBottom: 8, fontWeight: 600 }}>
            Recent verified ratings
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {ratingsFeed.map((r, i) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  background: "#1E2226",
                  borderRadius: 8,
                  padding: "9px 12px",
                  fontSize: 12.5,
                }}
              >
                <div>
                  <Stars n={r.stars} />
                  <span style={{ opacity: 0.5, marginLeft: 8 }}>R{r.amount} sale</span>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ opacity: 0.45, fontSize: 11 }}>{r.time}</div>
                  <div className="kc-mono" style={{ opacity: 0.35, fontSize: 10 }}>
                    {r.hash}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <button className="kc-btn" style={{ background: "#1B7A6E", color: "#F5F0E6" }}>
            Download proof-of-business PDF
          </button>
        </div>
      )}
    </div>
  );
}
