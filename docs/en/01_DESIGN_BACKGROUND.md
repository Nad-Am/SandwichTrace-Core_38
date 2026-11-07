# 1. DESIGN_BACKGROUND.md — Design Background

> **English** | [简体中文](../zh-CN/01_DESIGN_BACKGROUND.md)

## 1.1 Project Background

With the growth of decentralized exchanges (DEXs) on Ethereum, Automated Market Makers (AMMs) have become foundational infrastructure for on-chain token swaps.

Uniswap V2-style AMMs determine execution prices deterministically from liquidity pool reserves. When a user submits a swap transaction, pool reserves can shift before the transaction is executed. In an open transaction ordering environment, an adversary can exploit transaction ordering by placing transactions immediately before and after a target user's swap, forming a **Sandwich Attack**.

A canonical sandwich attack consists of three ordered transactions within a block:

1. **Front-run (`A`)**: The attacker executes prior to the victim, shifting the liquidity pool state and execution price.
2. **Victim (`B`)**: The victim executes the swap and suffers unfavorable slippage.
3. **Back-run (`C`)**: The attacker trades in the opposite direction immediately after the victim, capturing the price differential.

## 1.2 Problem Formulation

This project addresses the following core question:

> How can we deterministically identify transaction triplets matching canonical sandwich attack invariants from finalized block ordering, DEX Swap events, and transaction initiator metadata, while producing reproducible and explainable detection results?

Key sub-problems include:

- How to filter candidate attack combinations from intra-block transactions?
- How to verify actor consistency between the front-run and back-run transactions?
- How to distinguish true sandwich attacks from benign trades and boundary edge cases?
- How to express detection outputs through strongly typed schemas?
- How to evaluate detection Precision, Recall, and F1 against labeled ground-truth datasets?

## 1.3 Project Objectives

The current MVP builds a standalone, offline-verifiable Python detection core that:

- Loads normalized transaction and event payloads from local JSON fixtures.
- Identifies canonical sandwich triplets within a single liquidity pool and block.
- Outputs structured match records alongside deterministic rule trigger reasons.
- Computes the Quote Token gross profit signal in raw integer units.
- Evaluates Precision, Recall, and F1 against separated Ground Truth labels.

## 1.4 Core Value

This project focuses on post-hoc deterministic auditing and benchmark evaluation rather than real-time Mempool interception:

- Automatically identifies executed canonical sandwich triplets.
- Provides structured, reproducible evidence for on-chain security auditing.
- Supplies candidate forensic records for victim trade post-mortems.
- Establishes an extensible baseline for MEV pattern research and defense evaluation.

*Note: The current MVP does not perform asset recovery, live transaction blocking, or full archival trace forensics.*
