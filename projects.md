# AISOC Capstone Projects

📅 **November 1 – 30, 2025**

🧠 Get guidance from AISOC team throughout the project phase.

🏆 Compete for **$3,000 in cash prizes**.

## Timeline
- Nov 1–2: Team formation & Project kick off, with detailed instructions.
- Nov 3–22: Implementation Phase
- Nov 22–28: Pitch Preparation Phase
- Nov 29–30: Internal pitching sessions & shortlisting of top 10 teams for Demo Day

## Project Categories

### 1. Biomedical Science
#### AI for Molecular Science
**Objective**: LLMs, RAG pipelines, biomolecular data from HuggingFace, and biomolecular knowledge bases (such as UniProt, OncoKB, etc). What can you build?

**Scope**: This is an open-ended project that seeks creativity in identifying and tackling problems in molecular science using AI. Whether it is protein structure analysis and visualization using [AlphaFold](https://alphafoldserver.com/) & [Uniprot](https://www.uniprot.org/), or functional analysis of biomolecules using [Mol-Instructions dataset](https://huggingface.co/datasets/zjunlp/Mol-Instructions), or novel use of the latest Python packages that bridge molecular biology and machine learning, we want to see it all!

**Eligibile Tracks:** Applied AI, Production AI, LLM Engineering

**Team Structure:** Each team must include at least 1 member from Production AI.

**Instructions and Guidelines:** Coming shortly

### Semi-Supervised Gene Signature Classification
**Objective**: Build and deploy a machine learning system that classifies gene signatures. Optionally can be extended to a full-scale generative AI application with RAG over biomolecular databases.

**Dataset:** The dataset for this project is from the [MLRW 2022 : AI Driven Biomedical Hackathon](https://www.kaggle.com/competitions/mlrw-biomedicalhackathon/data) on Kaggle. It consists of multiomics data samples which were studied in gene expression signature experiments. There are 2 target variables in the data, `ctrl` and `pert` which are one-hot encoded (0 or 1). These columns indicate whether a sample is control or perturbation and they identify if an experiment as worked for sure. There are in total 20000 samples whose metadata is given. However, manual curated labels are given for 600 out of 20000. You need to use these 600 labels as a starting point to label the remaining training data and improve your model.

**Scope**: This project seeks solutions to a very specific problem that is useful in understanding underlying molecular causes of disease, effects of drugs. This project is primarily a machine learning project but can be extended with RAG over biomolecular data sources and genomic databases to ground the results, provide additional insights or draw useful scientific connections (be as creative as possible). Your solution should primarily include a simple frontend where a user uploads a molecular sample and the classified gene signature is returned. If the solution scope expands to include RAG, return the insights and results fetched by your retrieval pipeline (this can be as a static output or over interactive chat).

**Eligibile Tracks:** Machine Learning, Production AI, Applied AI (optional), LLM Engineering (optional)

**Team Structure:** Each team must include members from both the Machine Learning and Production AI tracks. If your solution includes generative AI, then 1 member from either Applied AI or LLM Engineering must be added to your team.

**Instructions and Guidelines:** Coming shortly

### 2. Finance
#### Market Intelligence
**Objective**: Build an intelligent application that retrieves and analyzes financial market data to provide investors with market insights, predictive intelligence or decision support. Investors need grounded, explainable answers that combine facts (filings/news) with intelligent signals and clean visual explanations (backtests, risk, etc). This project integrates retrieval, modeling, and visualization.

**Scope**: This is an open-ended project that seeks creativity in identifying and tackling problems faced by investor in financial markets. A variety of use cases across the stock & crypto markets can be explored including, but not limited to, on-chain analysis, price prediction, investment recommendations, and automated trading. A wide range of data sources including structured and unstructured market data (news, filings, fundamentals) can also be used for this project. Traditional machine learning (including time series & classification) can be integrated for signal generation, risk prediction, etc. Your solution should implement multi-agent RAG pipelines with planning, reasoning and retrieval capailities, and shoild include an interactive interface that provides visualizations and explanations of insights, predictions or decisions made by the AI system.

**Eligibile Tracks:** Applied AI, ProductiAI, Machine Learning (optional)

**Team Structure:** Each team must include at least 1 member from the Applied AI track and 1 from Production AI. If your solution uses machine learning, then 1 member from the ML track must be included.

**Instructions and Guidelines:** Coming shortly

#### Fraud Intelligence
**Objective**: Build a fraud decisioning system that consists of a ML system that is trained on financial transaction records and a real-time decisioning engine that interpretes the ML predictions and returns a decision on every incoming transaction (ALLOW, REJECT, PEND) with low latency.

**Dataset:** The dataset for this project is the [Financial Transactions Dataset: Analytics](https://www.kaggle.com/datasets/computingvictor/transactions-fraud-datasets/data) from Kaggle. It consists of transaction records, customer information and card data from a banking institution, spanning across the 2010s decade. 

**Scope**: This project seeks solutions to a very specific problem, namely fraud detection and decisioning. Your solution should include a simple frontend where a user can initiate a payment transaction and the decision is returned.

**Eligibile Tracks:** Machine Learning, Production AI

**Team Structure:** Each team must include members from both the Machine Learning and Production AI tracks.

**Instructions and Guidelines:** Coming shortly

### 3. Environment
**Objective:** Build an AI system that detects and explains emerging local crises (natural disasters, floods, disease outbreaks, infrastructure failures) by combining RAG over heterogeneous sources (news, government alerts, OSM, HDX docs), with interactive visualizations (map + timeline + resource allocation recommendations).

**Scope**: Open-ended. Let's see your creativity!

**Eligibile Tracks:** Applied AI, Production AI, LLM Engineering (optional)

**Team Structure:** Each team must include members from both the Applied AI and Production AI tracks.

**Instructions and Guidelines:** Coming shortly

## Demo Day
Get a chance to demo your project to a large audience at Synopsis AI Conference in December (details coming soon!).

## Prizes
Compete for a prize pool of **$3,000**. Non-Dedicated plan members are eligible for **Next 10 awards** (honourable mentions).
- 🥇 **1st place** – $1,000
- 🥈 **2nd place** – $750
- 🥉 **3rd place** – $500
- ⭐ **Next 10** – $750 ($75 each)

## Terms of Participation

### 1. Voluntary Participation

Participation in the **AISOC Capstone (“the Capstone)** is entirely voluntary and subject to these Terms and Conditions (“Terms”), as well as any additional rules, criteria, or requirements outlined for specific project topics. By participating, you acknowledge and agree that participation does not guarantee selection, success, or eligibility for prizes.

### 2. Eligibility and Qualification

To participate, individuals or teams must meet all the established eligibility requirements for the Capstone. Failure to meet these requirements or to comply with any rule or guideline may result in disqualification at the discretion of AISOC. AISOC reserves the right to verify eligibility and compliance at any stage of the Capstone.

### 3. Originality and Licensing of Submissions

All submissions must:

* Be original work created by the participant(s).
* Not infringe on the intellectual property (including but not limited to copyrights, patents, and trademarks) or any other rights of any third party.
* Be open-source and made available under the **MIT License**, unless otherwise specified for a particular project topic.

By submitting your work, you affirm that you hold all necessary rights to grant the licenses and permissions described herein and that your submission complies with all applicable laws and regulations.

**Retention of IP:** Participants generally retain the intellectual property rights to their original project work, subject to the open-source license granted.

### 4. Use of Submitted Material

By participating and submitting a project, you grant **AISOC**, its affiliates, partners, and sponsors a **non-exclusive, worldwide, royalty-free, perpetual license** to publicly promote, display, reproduce, modify, publish, and use the submission (in whole or in part) for:

* Promotional, educational, or marketing purposes;
* Display on AISOC websites, social media platforms, or events; and
* Demonstration or showcase purposes in connection with AISOC programs and initiatives.

AISOC may publicly promote or share submitted projects, including team names and participant information, as part of promotional campaigns, documentation, or showcases, with proper credit to the creators. You acknowledge and agree that no further compensation or permission is required for such use.

### 5. Publicity and Media Release

By participating, you consent to the use of your name, likeness, voice, photograph, and biographical information by AISOC for publicity and promotional purposes in connection with AISOC programs and initiatives, without further compensation or notice, unless prohibited by law.

### 6. Prizes and Award Policy

AISOC cannot guarantee entry or success in securing prizes based on your participation alone. Prizes are awarded solely based on the evaluation criteria outlined for the Capstone and the specific project topic. AISOC and its judging partners' decisions regarding eligibility, judging, and prize distribution are **final and binding**. All participants who qualify for a prize must successfully complete any required verification process (e.g., identity, eligibility, license compliance).

AISOC and its partners reserve the right to distribute all prizes within **60 days** following the conclusion of the program. This period allows for the proper processing, verification, evaluation, and disbursement necessary to award prizes appropriately and ensure fair distribution. Any delay outside this period will be communicated to the winners.

All decisions regarding prize allocation are final and at the sole discretion of AISOC.

### 7. Changes to the Capstone

AISOC reserves the right to modify, suspend, or terminate the Capstone or these Terms at any time, for any reason, with or without prior notice. Whenever feasible, AISOC will endeavour to notify participants of any significant changes to the Capstone structure, rules, schedule, or prizes within a reasonable timeframe.

### 8. Limitation of Liability

AISOC, its affiliates, and partners are not liable for any indirect, incidental, or consequential damages, losses, or injuries resulting from participation in the Capstone or reliance on any materials provided therein. By participating, you agree to indemnify and hold AISOC harmless from any and all claims, liabilities, injuries, losses, or damages arising from or in connection with your participation in the Capstone or the acceptance, possession, or use of any prize.

### 9. Data Privacy

Personal information collected during registration and participation will be handled in accordance with applicable data protection laws locally and globally. Participants agree to the collection and use of their data for purposes related to the administration of the Capstone.

### 10. Acknowledgement and Acceptance

By submitting a project or otherwise participating in the AISOC Capstone, you acknowledge that you have read, understood, and agree to these Terms of Participation, including all related rules and project-specific terms published by AISOC.

