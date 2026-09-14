// pdf generator
// 
window.generateKasiCredPDF = function(vendor, trustPct, isLoanReady, reviewCount, avgScore, reviews) {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ unit: "mm", format: "a4" });

  const pageWidth = doc.internal.pageSize.getWidth(); 
  let y = 20;

  // --- 1 HEADER ---
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(15, 23, 42);
  doc.text("KASICRED ENTERPRISE CREDIT REPORT", 20, y);

  doc.setFontSize(10);
  doc.setFont("Helvetica", "normal");
  doc.setTextColor(100, 116, 139);
  doc.text("Official On-Chain Proof-of-Business & Alternative Credit Assessment", 20, y + 6);

  // Reference / Date ID on the right
  const dateStr = new Date().toISOString().split('T')[0];
  doc.setFontSize(9);
  doc.text(`Report Date: ${dateStr}`, pageWidth - 20, y, { align: "right" });
  doc.text(`Ref ID: KC-${Math.floor(100000 + Math.random() * 900000)}`, pageWidth - 20, y + 6, { align: "right" });

  y += 12;
  doc.setDrawColor(203, 213, 225); 
  doc.setLineWidth(0.5);
  doc.line(20, y, pageWidth - 20, y);

  // --- 2. VENDOR ENTITY PROFILE ---
  y += 10;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(15, 23, 42);
  doc.text("1. REGISTERED BUSINESS ENTITY PROFILE", 20, y);

  y += 6;
  doc.setFillColor(248, 250, 252); 
  doc.setDrawColor(226, 232, 240);
  doc.roundedRect(20, y, pageWidth - 40, 26, 2, 2, "FD");

  doc.setFont("Helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(71, 85, 105);
  doc.text("Business / Stall Name:", 24, y + 7);
  doc.text("Market / Operating Area:", 24, y + 14);
  doc.text("Registered Category:", 24, y + 21);

  doc.setFont("Helvetica", "normal");
  doc.setTextColor(15, 23, 42);
  doc.text(vendor.name || "N/A", 70, y + 7);
  doc.text(vendor.area || "N/A", 70, y + 14);
  doc.text(vendor.sells || "N/A", 70, y + 21);

  // --- 3. TRUST & CREDITWORTHINESS METRICS ---
  y += 34;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(12);
  doc.text("2. VERIFIED ON-CHAIN PERFORMANCE METRICS", 20, y);

  y += 6;
  doc.setFillColor(241, 245, 249);
  doc.roundedRect(20, y, pageWidth - 40, 32, 2, 2, "FD");

  // Left Column Metrics
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(71, 85, 105);
  doc.text("Overall Trust Rating Score:", 24, y + 8);
  doc.text("Total Verified Sales Volume:", 24, y + 16);
  doc.text("Mean Customer Feedback:", 24, y + 24);

  doc.setFont("Helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(15, 23, 42);
  doc.text(`${trustPct} / 100 (${isLoanReady ? "PRE-QUALIFIED / LOAN READY" : "BUILDING TRACK RECORD"})`, 85, y + 8);
  doc.setFont("Helvetica", "normal");
  doc.text(`${reviewCount} Verified Transactions`, 85, y + 16);
  doc.text(`${avgScore.toFixed(1)} / 5.0 Stars`, 85, y + 24);

  // --- 4. RECENT TRANSACTION AUDIT TRAIL ---
  y += 40;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(12);
  doc.text("3. TRANSACTION & CUSTOMER REVIEW AUDIT TRAIL", 20, y);

  y += 6;
  // Table Header
  doc.setFillColor(30, 41, 59);
  doc.rect(20, y, pageWidth - 40, 8, "F");
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(9);
  doc.setTextColor(255, 255, 255);
  doc.text("TIMESTAMP", 24, y + 5.5);
  doc.text("VERIFIED REVIEW & METRIC", 70, y + 5.5);
  doc.text("ON-CHAIN HASH", pageWidth - 55, y + 5.5);

  y += 8;
  doc.setFont("Helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(15, 23, 42);

  if (!reviews || reviews.length === 0) {
    doc.setFillColor(255, 255, 255);
    doc.rect(20, y, pageWidth - 40, 10, "FD");
    doc.text("No transaction reviews recorded on-chain yet.", 24, y + 6);
    y += 10;
  } else {
    reviews.slice(0, 6).forEach((r, idx) => {
      const rowBg = idx % 2 === 0 ? 255 : 248;
      doc.setFillColor(rowBg, rowBg, rowBg);
      doc.setDrawColor(226, 232, 240);
      doc.rect(20, y, pageWidth - 40, 10, "FD");

      doc.text(r.created_at || "Recent", 24, y + 6);
      doc.text(`"${r.review_text || "Verified Sale Recorded"}"`, 70, y + 6);
      doc.setFont("Courier", "normal");
      doc.setFontSize(8);
      doc.text(r.tx_hash ? r.tx_hash.slice(0, 14) + "..." : "Celo-Verified", pageWidth - 55, y + 6);
      doc.setFont("Helvetica", "normal");
      doc.setFontSize(9);

      y += 10;
    });
  }

  // --- 5. COMPLIANCE & CERTIFICATION STATEMENT ---
  y += 12;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(10);
  doc.setTextColor(15, 23, 42);
  doc.text("CREDIT ASSESSMENT CERTIFICATION", 20, y);

  y += 5;
  doc.setFont("Helvetica", "normal");
  doc.setFontSize(8.5);
  doc.setTextColor(100, 116, 139);
  const declarationText = "This document represents an automated alternative credit report compiled from decentralized trade verification metrics anchored on the Celo blockchain ledger. The data certifies immutable customer reviews and transactional consistency designed to support financial inclusion and credit appraisal for informal economy enterprises.";
  doc.text(declarationText, 20, y, { maxWidth: pageWidth - 40 });

  // Footer Signature Line
  y += 24;
  doc.setDrawColor(150, 150, 150);
  doc.line(pageWidth - 80, y, pageWidth - 20, y);
  doc.setFontSize(8);
  doc.text("Authorized Protocol Verification Stamp", pageWidth - 50, y + 4, { align: "center" });

  // Page Footer
  doc.setFont("Helvetica", "italic");
  doc.setFontSize(8);
  doc.setTextColor(148, 163, 184);
  doc.text("KasiCred — Turning Daily Cash Trade into Portable, Tamper-Proof Trust", pageWidth / 2, 285, { align: "center" });

  // Save PDF
  doc.save(`${(vendor.name || "Enterprise").replace(/\s+/g, "_")}_Official_Credit_Report.pdf`);
};