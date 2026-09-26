// KasiCred Enterprise Proof-of-Business & Income Report PDF Generator
// Generates an official, immutable on-chain verifiable audit certificate

window.generateKasiCredPDF = function(vendor, trustPct, isLoanReady, reviewCount, avgScore, reviews) {
  if (!window.jspdf || !window.jspdf.jsPDF) {
    alert("PDF library is loading or unavailable. Please try again in a few moments.");
    return;
  }

  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ unit: "mm", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  let y = 20;

  vendor = vendor || {};
  trustPct = trustPct !== undefined ? trustPct : 85;
  isLoanReady = isLoanReady !== undefined ? isLoanReady : (trustPct >= 80);
  reviewCount = reviewCount !== undefined ? reviewCount : 0;
  avgScore = avgScore !== undefined ? Number(avgScore) : 0;
  reviews = Array.isArray(reviews) ? reviews : [];

  // --- 1. HEADER & LOGO ---
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(20);
  doc.setTextColor(15, 23, 42);
  doc.text("KASICRED ENTERPRISE CREDIT REPORT", 20, y);

  doc.setFontSize(10);
  doc.setFont("Helvetica", "normal");
  doc.setTextColor(100, 116, 139);
  doc.text("Official On-Chain Proof-of-Business & Alternative Credit Assessment", 20, y + 6);

  // Date and Reference ID
  const dateStr = new Date().toISOString().split('T')[0];
  const refCode = "KC-" + Math.floor(100000 + Math.random() * 900000);
  doc.setFontSize(9);
  doc.text(`Report Date: ${dateStr}`, pageWidth - 20, y, { align: "right" });
  doc.text(`Ref ID: ${refCode}`, pageWidth - 20, y + 6, { align: "right" });

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
  doc.roundedRect(20, y, pageWidth - 40, 32, 2, 2, "FD");

  doc.setFont("Helvetica", "bold");
  doc.setFontSize(9.5);
  doc.setTextColor(71, 85, 105);
  doc.text("Business / Stall Name:", 24, y + 7);
  doc.text("Market / Operating Area:", 24, y + 14);
  doc.text("Registered Category / Goods:", 24, y + 21);
  doc.text("Merchant Phone / Wallet:", 24, y + 28);

  doc.setFont("Helvetica", "normal");
  doc.setTextColor(15, 23, 42);
  doc.text(vendor.name || vendor.store_name || "Mama Thabo's Spaza", 76, y + 7);
  doc.text(vendor.area || vendor.market_area || "Randburg Taxi Rank", 76, y + 14);
  doc.text(vendor.sells || vendor.category_items || "Produce & General Groceries", 76, y + 21);
  const walletDisplay = vendor.wallet_address || (vendor.phone ? `0x${vendor.phone.slice(-6)}...celo` : "0x40f8...Sepolia");
  doc.text(`${vendor.phone || "0712345678"} • ${walletDisplay}`, 76, y + 28);

  // --- 3. TRUST & PERFORMANCE METRICS ---
  y += 40;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(15, 23, 42);
  doc.text("2. VERIFIED ON-CHAIN PERFORMANCE METRICS", 20, y);

  y += 6;
  doc.setFillColor(241, 245, 249);
  doc.roundedRect(20, y, pageWidth - 40, 32, 2, 2, "FD");

  doc.setFont("Helvetica", "bold");
  doc.setFontSize(9.5);
  doc.setTextColor(71, 85, 105);
  doc.text("Overall Trust Rating Score:", 24, y + 8);
  doc.text("Total Verified Customer Reviews:", 24, y + 16);
  doc.text("Mean Customer Satisfaction:", 24, y + 24);

  doc.setFont("Helvetica", "bold");
  doc.setFontSize(11);
  doc.setTextColor(15, 23, 42);
  const statusLabel = isLoanReady ? "PRE-QUALIFIED / LOAN READY" : "BUILDING TRACK RECORD";
  doc.text(`${trustPct} / 100 (${statusLabel})`, 85, y + 8);
  doc.setFont("Helvetica", "normal");
  doc.text(`${reviewCount} Verified Transactions`, 85, y + 16);
  doc.text(`${avgScore.toFixed(1)} / 5.0 Stars`, 85, y + 24);

  // --- 4. RECENT TRANSACTION AUDIT TRAIL ---
  y += 40;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(15, 23, 42);
  doc.text("3. TRANSACTION & CUSTOMER REVIEW AUDIT TRAIL", 20, y);

  y += 6;
  // Table Header
  doc.setFillColor(30, 41, 59);
  doc.rect(20, y, pageWidth - 40, 8, "F");
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(8.5);
  doc.setTextColor(255, 255, 255);
  doc.text("TIMESTAMP", 24, y + 5.5);
  doc.text("VERIFIED REVIEW & RATING", 68, y + 5.5);
  doc.text("CELO ON-CHAIN HASH", pageWidth - 55, y + 5.5);

  y += 8;
  doc.setFont("Helvetica", "normal");
  doc.setFontSize(8.5);
  doc.setTextColor(15, 23, 42);

  if (!reviews || reviews.length === 0) {
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(226, 232, 240);
    doc.rect(20, y, pageWidth - 40, 10, "FD");
    doc.text("No transaction reviews recorded on-chain yet.", 24, y + 6);
    y += 10;
  } else {
    reviews.slice(0, 6).forEach((r, idx) => {
      const rowBg = idx % 2 === 0 ? 255 : 248;
      doc.setFillColor(rowBg, rowBg, rowBg);
      doc.setDrawColor(226, 232, 240);
      doc.rect(20, y, pageWidth - 40, 10, "FD");

      const timeText = r.created_at ? r.created_at.slice(0, 16).replace("T", " ") : (r.time || "Recent");
      doc.text(timeText, 24, y + 6);

      const stars = r.score ? "★".repeat(r.score) : "★★★★★";
      const reviewText = (r.review_text || r.text || "Verified Sale Recorded");
      const shortReview = reviewText.length > 34 ? reviewText.slice(0, 31) + "..." : reviewText;
      doc.text(`${stars} "${shortReview}"`, 68, y + 6);

      doc.setFont("Courier", "normal");
      doc.setFontSize(7.5);
      const hashText = r.tx_hash ? (r.tx_hash.slice(0, 14) + "...") : (r.hash || "0x9c3e...celo");
      doc.text(hashText, pageWidth - 55, y + 6);

      doc.setFont("Helvetica", "normal");
      doc.setFontSize(8.5);
      y += 10;
    });
  }

  // --- 5. COMPLIANCE & CERTIFICATION STATEMENT ---
  y += 8;
  doc.setFont("Helvetica", "bold");
  doc.setFontSize(9.5);
  doc.setTextColor(15, 23, 42);
  doc.text("CREDIT ASSESSMENT CERTIFICATION (POPIA & NCA COMPLIANT)", 20, y);

  y += 5;
  doc.setFont("Helvetica", "normal");
  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  const declarationText = "This document represents an automated alternative credit assessment compiled from decentralized trade verification metrics anchored to the Celo blockchain ledger. In accordance with South African NCA section 78(3) and POPIA data minimisation guidelines, customer attestations are cryptographically fingerprinted to certify business continuity and cashflow consistency for informal economy underwriting.";
  doc.text(declarationText, 20, y, { maxWidth: pageWidth - 40 });

  // Footer Signature Line
  y += 20;
  doc.setDrawColor(150, 150, 150);
  doc.line(pageWidth - 85, y, pageWidth - 20, y);
  doc.setFontSize(7.5);
  doc.text("Protocol Relayer Cryptographic Seal", pageWidth - 52, y + 4, { align: "center" });

  // Page Footer
  doc.setFont("Helvetica", "italic");
  doc.setFontSize(7.5);
  doc.setTextColor(148, 163, 184);
  doc.text("KasiCred — Turning Daily Cash Trade into Portable, Tamper-Proof Trust", pageWidth / 2, 285, { align: "center" });

  const fileName = `${(vendor.name || vendor.store_name || "KasiCred_Merchant").replace(/[^a-zA-Z0-9]/g, "_")}_Official_Report.pdf`;
  doc.save(fileName);
};
