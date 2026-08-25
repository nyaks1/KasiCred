// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KasiCredTrustLedger {
    struct ReviewRecord {
        bytes32 reviewHash;
        uint8 score;
        uint256 timestamp;
    }

    // Mapping from vendor address to review records
    mapping(address => ReviewRecord[]) private vendorReviews;
    mapping(address => uint256) public totalScore;
    mapping(address => uint256) public reviewCount;

    event ReviewCommitted(
        address indexed vendor,
        bytes32 reviewHash,
        uint8 score,
        uint256 timestamp
    );

    function recordReview(address vendor, bytes32 reviewHash, uint8 score) external {
        require(score >= 1 && score <= 5, "Score must be 1-5");
        
        vendorReviews[vendor].push(ReviewRecord({
            reviewHash: reviewHash,
            score: score,
            timestamp: block.timestamp
        }));

        totalScore[vendor] += score;
        reviewCount[vendor] += 1;

        emit ReviewCommitted(vendor, reviewHash, score, block.timestamp);
    }

    function getVendorSummary(address vendor) external view returns (uint256 averageScore, uint256 count) {
        if (reviewCount[vendor] == 0) return (0, 0);
        return ((totalScore[vendor] * 10) / reviewCount[vendor], reviewCount[vendor]);
    }
}