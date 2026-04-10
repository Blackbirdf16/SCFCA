\documentclass[12pt,a4paper]{report}

% ---------------- Packages ----------------
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{setspace}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{longtable}
\usepackage{booktabs}
\usepackage{array}
\usepackage{enumitem}
\usepackage{amsmath, amssymb}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{fancyhdr}
\usepackage[backend=biber,style=ieee]{biblatex}
\addbibresource{references.bib}

\geometry{margin=2.5cm}
\onehalfspacing
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=black,
    urlcolor=blue
}

% ---------------- Header / Footer ----------------
\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}

% ---------------- Document ----------------
\begin{document}

% ---------------- Title Page ----------------
\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{uni.png}
    \label{fig:placeholder}
\end{figure}

\begin{titlepage}
\centering
{\Large Máster Universitario en Ciberseguridad (2025--2026)}\\[1cm]
{\Large TRABAJO FIN DE MÁSTER }\\[1cm]

{\huge \textbf{Secure Custody Framework for Cryptocurrency Assets (SCFCA)}}\\[0.5cm]

\includegraphics[width=0.40\linewidth]{Narnium_logo.png}\\[1cm]

{\Large Design of a Secure Technical Framework for the Custody, Management, Preservation, and Auditing of Cryptocurrency Assets in Criminal Investigations}\\[2cm]

\textbf{Student:} Lorela Elezaj\\
\textbf{Instructor:} Antonio Maña Gómez \\[2cm]
\vfill
\textbf{Date:} \today

\end{titlepage}

% ---------------- Abstract ----------------
\chapter*{Abstract}
\addcontentsline{toc}{chapter}{Abstract}

This thesis presents the Secure Custody Framework for Cryptocurrency Assets (SCFCA), a
security-oriented technical architecture designed for the institutional custody,
management, preservation, and auditing of confiscated cryptocurrency assets
in criminal investigations.

% ---------------- Keywords ----------------
\chapter*{Keywords}
\addcontentsline{toc}{chapter}{Keywords}

Cryptocurrency custody; institutional governance; RBAC; dual approval;
audit logging; HSM; misuse cases; .

% ---------------- TOC ----------------
\tableofcontents
\listoffigures
\listoftables
\clearpage

% =====================================================
\chapter{Introduction}

\section{Context and Motivation}
The rapid development and widespread adoption of cryptocurrencies and digital assets have profoundly transformed the way economic value is created, transferred, and stored. Alongside their legitimate uses, these technologies have increasingly been exploited in a wide range of criminal activities, including financial fraud, money laundering, organized crime, and corruption. As a result, cryptocurrencies have become not only instruments used in criminal operations, but also direct objects of seizure, confiscation, and judicial administration by state authorities.

Law enforcement agencies and judicial institutions are therefore confronted with new operational and technical challenges. Unlike traditional financial assets, cryptocurrencies are not managed through centralized intermediaries such as banks or custodial institutions. Instead, control over these assets depends entirely on cryptographic mechanisms, and more specifically on the secure management of private keys. The loss, compromise, or misuse of these keys can lead to irreversible financial loss and may undermine the integrity of digital evidence relevant to criminal proceedings.

In Albania, these challenges became particularly evident following a significant institutional turning point in 2019 with the establishment of the Special Structure for Anti-Corruption and Organized Crime (SPAK), as part of the broader Justice Reform process. This structure was created to investigate high-level corruption and organized crime, including cases involving senior public officials and individuals with substantial political or economic influence. In the years that followed, these investigations led to the seizure of assets of considerable financial value, including real estate, bank accounts, and other forms of property, among which cryptocurrency assets also began to appear.

At the time, Albania lacked a specific legal framework regulating cryptocurrencies, a situation that reflected a broader absence of technical infrastructure, operational procedures, and institutional experience related to the custody and management of digital assets. This gap exposed a clear misalignment between the increasingly sophisticated techniques employed by criminal organizations and the technical capabilities available to the institutions responsible for combating them. Even as legislative developments concerning cryptocurrencies were introduced in the period 2024–2025, it became evident that legal regulation alone was insufficient to address the underlying technical and organizational challenges.

In practice, the absence of specialized platforms and standardized technical procedures has led to a reliance on ad hoc solutions or international cooperation with foreign institutions possessing more mature technical capabilities in this domain, such as those operating within other European jurisdictions. While such cooperation can provide temporary support, it does not constitute a sustainable or autonomous solution for national authorities tasked with the long-term management and auditing of confiscated digital assets.

This context highlights a fundamental issue: the need for secure, reliable, and auditable technical mechanisms capable of supporting the custody and management of cryptocurrency assets within institutional environments. The challenge is not inherent to blockchain technology itself, but rather to the way custody is implemented through cryptographic controls, access management, role separation, and security processes. Addressing these challenges is essential to ensure the protection of seized assets, maintain institutional accountability, and preserve the integrity of digital evidence throughout the lifecycle of criminal investigations.


\section{Problem Statement}
Despite the growing involvement of cryptocurrencies in criminal investigations and asset confiscation procedures, state institutions continue to face significant technical and organizational shortcomings in the secure custody and management of seized digital assets. While recent legislative developments have begun to address the legal status of cryptocurrencies, they do not resolve the practical challenges associated with their technical custody, control, and auditability.

Cryptocurrency assets differ fundamentally from traditional financial assets in that ownership and control are determined exclusively by cryptographic private keys. The absence of secure and well-defined mechanisms for private key management exposes confiscated assets to critical risks, including irreversible loss, unauthorized access, and misuse. These risks are further amplified in institutional environments where multiple actors are involved, and where inadequate separation of duties or poorly defined access controls may enable insider threats or abuse of privileges.

In many existing institutional contexts, there is no standardized technical framework governing how confiscated cryptocurrency assets should be registered, stored, accessed, transferred, or audited. Custody procedures are often handled in an ad hoc manner, relying on fragmented tools, manual processes, or external entities. Such approaches lack transparency, are difficult to audit, and do not provide sufficient guarantees of integrity, non-repudiation, or traceability throughout the lifecycle of the assets.

Furthermore, the absence of tamper-evident audit mechanisms and clearly defined role-based responsibilities undermines institutional accountability. Without comprehensive and verifiable audit trails, it becomes difficult to demonstrate that assets have been managed in accordance with legal and procedural requirements, or to reliably attribute actions to specific authorized actors. This represents a critical weakness in contexts where digital assets may constitute both financial value and evidentiary material in ongoing judicial proceedings.

Consequently, the core problem addressed in this work is not the regulation of cryptocurrencies as financial instruments, nor the operation of blockchain networks themselves, but rather the lack of a secure, standardized, and auditable technical framework for the institutional custody and management of confiscated cryptocurrency assets. Addressing this problem requires a systematic approach that integrates cryptographic controls, access management, role separation, and auditability into a coherent custody model suitable for use by state authorities.


\section{Objectives}
The objective of this Master’s Thesis is to design a secure technical framework for the custody, management, preservation, and auditing of cryptocurrency assets within the context of criminal investigations. The work focuses on addressing the technical and cybersecurity challenges associated with the institutional management of confiscated crypto-assets, proposing an architecture capable of mitigating both external and internal threats, ensuring the integrity and availability of assets, and guaranteeing the traceability and auditability of all operations performed.

The proposed framework, referred to as the Secure Custody Framework for Cryptocurrency Assets (SCFCA), is conceived as a technology-agnostic solution intended for use by public authorities or authorized entities responsible for the judicial custody of cryptocurrency assets. The scope of this work does not focus on the development of blockchain technologies themselves, but rather on the design of security mechanisms, cryptographic management, access control, separation of duties, and auditing processes that enable secure and verifiable asset custody in institutional environments.

\subsection{General Objective}
\begin{itemize}
\item Design a reference technical framework that enables public institutions to implement secure,  auditable and resilient systems for the custody, management, preservation, and auditing of cryptocurrency assets in the context of criminal investigations.
\end{itemize}

\subsection{Specific Objectives}
\begin{itemize}
 \item To analyze the technical characteristics and security risks associated with the institutional custody of cryptocurrencies, with particular emphasis on cryptographic key management and internal and external threats.
 \item To identify and model the relevant threats affecting institutional cryptocurrency custody systems through structured threat analysis and misuse scenario modeling, and to map these threats to appropriate security controls.
\item To define a secure custody architecture based on security-by-design principles, separation of duties, access control, and role management.
To propose technical mechanisms for preserving the integrity and availability of cryptocurrency assets, as well as for the controlled execution and validation of institutional transfers.
\item To design a logging and auditing system that guarantees traceability, non-repudiation, and accountability for all operations performed on the assets.
To align the proposed framework with European cybersecurity, governance, and risk management standards and best practices, ensuring its applicability within an institutional European context.
\end{itemize}



% =====================================================
\chapter{State of the Art}

\section{Cryptocurrency Custody Models}
The custody of cryptocurrency assets refers to the mechanisms and processes through which private cryptographic keys are generated, stored, protected, and ultimately used to authorize transactions on blockchain networks. In contrast to traditional financial assets, which are typically managed by centralized intermediaries such as banks or financial institutions, cryptocurrencies operate within decentralized infrastructures. In these environments, ownership and control are defined solely by possession of the corresponding private keys. Whoever controls the key controls the asset.

For this reason, custody models are not merely technical implementations; they directly determine the security, availability, and long-term integrity of digital assets. The design of a custody solution therefore reflects underlying assumptions about trust, risk tolerance, and operational requirements.

Over time, several custody models have emerged in practice, each shaped by different security priorities and usage scenarios. These models are commonly distinguished according to the degree of control retained by the asset holder and the mechanisms adopted to protect private keys. While some approaches prioritize accessibility and operational efficiency, others emphasize isolation and strict protection against unauthorized access. The balance between these dimensions defines the practical trade-offs of each custody model.

\subsection{Hot Wallet Custody}

Hot wallets are custody solutions in which private keys are stored in environments connected to the internet. They are typically used to enable frequent, automated, or near-instant transactions, making them particularly attractive for exchanges, payment platforms, and services that require continuous operational availability.

The main advantage of hot wallets lies in their accessibility. Because the signing infrastructure is online, transactions can be processed quickly and with minimal manual intervention. In commercial settings, this responsiveness is often considered essential.

However, this accessibility introduces a significant security trade-off. Internet connectivity inevitably expands the attack surface. Private keys stored in hot environments may be exposed to malware, exploitation of software vulnerabilities, phishing campaigns targeting privileged users, or unauthorized access to backend systems. Even when advanced security controls are implemented, the residual risk associated with constant network exposure cannot be fully eliminated.

From an institutional perspective—particularly in contexts involving seized or confiscated assets—the use of hot wallets without additional protective layers is difficult to justify. Judicial custody environments typically prioritize integrity, auditability, and resilience over transactional speed. For high-value or legally sensitive assets, the operational convenience of hot storage must therefore be carefully weighed against the elevated risk profile it entails.

\subsection{Cold Storage Custody}

Cold storage refers to custody models in which private keys are generated and stored in environments that remain offline and isolated from network connectivity. By removing direct exposure to the internet, this approach significantly reduces the risk of remote compromise and is widely regarded as one of the most secure methods for protecting cryptocurrency assets.

Cold storage can take different forms, including hardware devices, air-gapped computers, or dedicated systems used exclusively for signing operations. In all cases, the underlying objective is the same: to minimize the attack surface by limiting external access to cryptographic material.

The security benefits of cold storage are substantial, particularly in scenarios where asset preservation is the primary concern. However, this increased protection comes at an operational cost. Transaction authorization typically requires physical access to secure environments, coordinated procedures, and manual validation steps. As a result, execution times may be slower and workflows less flexible compared to online custody solutions.

In institutional settings, especially those involving judicial custody, cold storage is often considered appropriate for long-term asset preservation. Nevertheless, it may not fully address the need for structured approval workflows, traceability mechanisms, and controlled governance processes. While it strengthens cryptographic protection, it does not, by itself, solve organizational or accountability challenges.

\subsection{Custodial Services and Centralized Custody}

Centralized custodial services provide custody on behalf of users by managing private keys within controlled infrastructures. In this model, users relinquish direct control over cryptographic material and rely on the custodian to implement security mechanisms, operational safeguards, and compliance procedures. This approach is common among regulated exchanges and specialized institutional custody providers.

From a technical point of view, centralized custody concentrates both responsibility and risk within a single organizational boundary. Analyses of major cryptocurrency fraud cases and exchange collapses demonstrate that many large-scale losses have resulted not from weaknesses in blockchain protocols, but from failures in centralized custody infrastructures \cite{Scharfman2024}. When private keys are aggregated and managed within a single system, that system becomes a high-value target.

The security of centralized custody therefore depends less on blockchain resilience and more on internal governance, infrastructure hardening, access control enforcement, and operational discipline. As emphasized in modern cryptographic security literature, control over key material ultimately defines control over assets \cite{Aumasson2021}. The trust boundary shifts from protocol-level guarantees to institutional safeguards. Furthermore, infrastructure security practices highlight that centralization increases systemic risk concentration, requiring strict operational controls and monitoring \cite{Vehent2018}.

In institutional contexts involving confiscated assets, reliance on external custodians introduces additional concerns. Questions of jurisdiction, accountability, audit transparency, and long-term autonomy become central. While professional custodians may implement advanced security controls, delegating custody to third parties can complicate evidentiary integrity and institutional responsibility, particularly in judicial environments where traceability and non-repudiation are essential.

\subsection{Hardware-Based Custody}

Hardware-based custody models rely on dedicated devices specifically designed to generate, store, and use cryptographic keys in a secure manner. Unlike purely software-based solutions, these devices isolate key material within protected hardware environments, reducing the risk of extraction through conventional malware or remote compromise.

Common examples include hardware wallets and Hardware Security Modules (HSMs). These devices are engineered to resist physical tampering and unauthorized key access. In many enterprise environments, HSMs are used to enforce strict cryptographic policies, including controlled key generation, secure key storage, and regulated signing operations. By embedding security mechanisms at the hardware level, such systems provide stronger guarantees than general-purpose computing platforms.

The primary advantage of hardware-based custody lies in its ability to enforce security boundaries independently of the host system. Even if the surrounding infrastructure is partially compromised, properly configured hardware devices can prevent direct exposure of private keys. This architectural separation significantly strengthens key protection in institutional contexts.

However, hardware-based custody does not eliminate governance risks. The security of the system still depends on access control configuration, role assignment, and operational procedures. If excessive privileges are granted or physical access controls are poorly implemented, the intended security benefits may be weakened. In multi-actor institutional environments, hardware protection must therefore be complemented by structured approval workflows, audit logging, and separation-of-duties mechanisms.

For these reasons, hardware-based custody is widely adopted in governmental and enterprise settings, but its effectiveness ultimately depends on the broader security architecture in which it is embedded.


\section{Digital Asset Governance}

Digital asset governance encompasses the organizational structures, policies, procedures, and technical controls through which digital assets are managed, monitored, and controlled within an institution. In the context of cryptocurrencies, governance extends beyond traditional financial oversight to include cryptographic key management, access control enforcement, accountability mechanisms, and auditability throughout the asset lifecycle.

In institutional environments—particularly those involving law enforcement or judicial authorities—governance is not merely an operational concern but a legal and regulatory necessity. The handling of seized or confiscated cryptocurrency assets must comply with principles of accountability, traceability, and procedural integrity. Actions performed on digital assets may carry legal consequences and evidentiary relevance, which places additional requirements on custody infrastructures.

Within the European regulatory landscape, the governance of crypto-assets has gained increasing formalization. The Markets in Crypto-Assets Regulation (MiCA) \cite{MiCA2023} establishes a harmonized framework for the issuance, custody, and supervision of crypto-assets across the European Union. While MiCA primarily addresses market actors and service providers, its emphasis on transparency, operational responsibility, and supervisory oversight reinforces the necessity of structured custody governance mechanisms. Institutions managing digital assets must therefore demonstrate internal controls, clear allocation of responsibilities, and reliable record-keeping practices.

In parallel, the Digital Operational Resilience Act (DORA) \cite{DORA2022} strengthens requirements for ICT risk management, incident reporting, and operational resilience within financial entities. Although not limited to cryptocurrency services, DORA highlights the importance of infrastructure hardening, monitoring, and continuity planning in systems handling sensitive financial operations. These regulatory developments underscore that digital asset custody cannot rely solely on cryptographic protection; it must also embed resilience and risk management at the architectural level.

A central governance challenge arises from the decentralized nature of blockchain systems. While blockchain networks provide immutability and public verifiability at the ledger level, these guarantees do not extend to off-chain custody processes. Decisions regarding key access, transaction authorization, and workflow approval occur within institutional environments and remain dependent on internal procedures. Governance failures at this layer can undermine the integrity of asset management, regardless of the robustness of the underlying blockchain protocol.

Another critical dimension is auditability. Effective governance requires comprehensive, tamper-evident audit trails capable of linking authorized actors, approved workflows, and executed transactions. Without verifiable logging and non-repudiation mechanisms, institutions may be unable to reconstruct events, demonstrate compliance, or defend the integrity of seized assets in judicial proceedings.

In practice, digital asset governance is therefore inseparable from technical design. Regulatory principles such as least privilege, separation of duties, and operational resilience must be concretely implemented through access control models, approval workflows, logging mechanisms, and infrastructure safeguards. A custody system that fails to integrate these elements risks not only security compromise but also regulatory and institutional non-compliance.

\section{Security Threats in Custody Systems}

Cryptocurrency custody systems are exposed to a broad spectrum of security risks that stem from the fundamental properties of blockchain-based assets. Unlike traditional financial infrastructures, where transactions can often be reversed and institutional controls mediate ownership, cryptocurrency systems rely entirely on cryptographic key control. If a private key is compromised or misused, the resulting asset transfer is typically irreversible. This characteristic makes custody security not merely important, but critical.

External attacks remain one of the most visible threat categories. Over the past decade, several high-profile exchange breaches have demonstrated how vulnerabilities in hot wallet infrastructure, backend systems, or access management mechanisms can result in massive asset losses. Incidents such as the Mt. Gox collapse in 2014 and subsequent large-scale exchange hacks illustrate how insufficient key segregation, inadequate monitoring, and weak internal controls can lead to catastrophic consequences. These events highlight that internet-facing custody components significantly increase the attack surface and must be carefully isolated or minimized.

However, external attacks represent only part of the threat landscape. Insider threats often pose a more subtle and complex risk. Individuals with legitimate system access may abuse privileges, bypass procedural safeguards, or exploit weak separation-of-duties controls. In environments where approval workflows are poorly enforced or logging mechanisms are insufficient, malicious or negligent insiders may initiate unauthorized transfers or manipulate records without immediate detection. Institutional custody systems, especially those involving confiscated assets, are particularly sensitive to such risks because of the legal and reputational implications involved.

Key management failures constitute another critical threat category. Private keys may be improperly generated, inadequately protected, insufficiently backed up, or mishandled during operational procedures. Unlike passwords or traditional credentials, lost or compromised cryptographic keys cannot be reset. Several custody failures in the industry have stemmed not from sophisticated attacks, but from poor operational practices, inadequate redundancy, or unclear governance structures around key access.

Audit and traceability weaknesses further compound these risks. In some historical cases, institutions and exchanges were unable to reconstruct transaction histories or determine responsibility due to incomplete or manipulable logs. Without tamper-evident logging and non-repudiation mechanisms, organizations may struggle to demonstrate procedural compliance or defend against accusations of mismanagement. For systems handling judicially seized assets, such deficiencies could undermine evidentiary integrity in court proceedings.

Finally, organizational and governance failures frequently amplify technical vulnerabilities. The collapse of certain centralized crypto entities has shown that weak internal governance, lack of independent oversight, and concentration of authority can be as damaging as external cyberattacks. The FTX crisis, for example, underscored how governance breakdowns and insufficient internal controls may lead to severe financial and institutional consequences, even in the absence of purely technical compromise.

Taken together, these incidents demonstrate that cryptocurrency custody risks are multidimensional. They encompass technical vulnerabilities, insider misuse, operational failures, and governance deficiencies. Effective custody design therefore requires a holistic approach that integrates cryptographic protection, structured approval mechanisms, role separation, tamper-evident logging, and institutional accountability into a coherent architectural framework. The understanding of these threat categories provides the foundation for the threat modeling and security requirements defined in subsequent chapters.

\section{Gap Analysis}

The review of existing custody models, governance approaches, and security threats reveals a clear mismatch between current industry practices and the specific requirements of institutional environments responsible for managing confiscated cryptocurrency assets.

Most existing custody solutions have been designed for commercial use cases. Exchanges and private custodians typically prioritize liquidity, operational efficiency, and customer-facing services. While many of these platforms implement advanced security mechanisms, their architectural priorities differ fundamentally from those of law enforcement or judicial institutions. In commercial settings, availability and transaction throughput are often emphasized; in institutional custody of seized assets, traceability, procedural integrity, and accountability are equally — if not more — critical.

Hot wallet solutions, for example, provide operational flexibility but expose assets to higher levels of external risk. Cold storage, on the other hand, offers strong protection against remote attacks but does not inherently provide structured multi-actor governance or formalized approval workflows. Hardware-based solutions strengthen key protection, yet they do not automatically enforce institutional separation of duties or prevent misuse of privileged access. In practice, technical safeguards and governance mechanisms are frequently treated as separate concerns rather than as components of a unified framework.

Centralized custodial services introduce an additional layer of dependency. When institutions rely on third-party providers, questions arise regarding jurisdiction, supervisory control, evidentiary responsibility, and long-term autonomy. For confiscated assets that may be subject to legal disputes or court proceedings, such dependencies can complicate accountability and procedural transparency.

Another significant gap lies in the integration of auditability within custody systems. Although blockchain transactions are inherently transparent at the ledger level, institutional decisions—such as who authorized a transfer, under what approval conditions, and through which internal workflow—remain off-chain. Existing solutions rarely provide a structured, tamper-evident linkage between institutional authorization processes and executed blockchain transactions. This disconnect weakens the ability of institutions to demonstrate procedural compliance and reconstruct decision histories.

Furthermore, regulatory developments within the European Union, including MiCA and DORA, emphasize operational resilience, internal controls, and risk management. However, there remains no standardized technical framework specifically tailored to the institutional custody of seized crypto-assets. Institutions often rely on ad hoc combinations of tools, manual procedures, or externally managed solutions, leading to inconsistencies and potential governance weaknesses.

In summary, the current landscape lacks an integrated, security-oriented technical framework designed specifically for institutional custody in criminal investigation contexts. Existing models address isolated aspects of security or governance but do not systematically combine cryptographic protection, structured approval workflows, separation of duties, tamper-evident logging, and regulatory alignment within a single coherent architecture. 

This gap motivates the development of the Secure Custody Framework for Cryptocurrency Assets (SCFCA), which seeks to formalize and integrate these elements into a structured, institution-oriented custody model.

\section{European Regulatory Context for Crypto-Asset Custody}

The regulatory environment surrounding crypto-assets in the European Union has evolved significantly in recent years. Although early cryptocurrency activity operated in largely unregulated spaces, the European legislator has progressively introduced structured frameworks aimed at enhancing transparency, accountability, and operational resilience in digital asset markets.

A major development in this context is the Markets in Crypto-Assets Regulation (MiCA) \cite{MiCA2023}. MiCA establishes a harmonized regulatory framework governing the issuance, offering, and custody of crypto-assets within the European Union. Although its primary focus lies on crypto-asset service providers and market participants, MiCA emphasizes principles that are directly relevant to institutional custody systems, including operational responsibility, safeguarding of client assets, governance transparency, and supervisory oversight.

In parallel, the Digital Operational Resilience Act (DORA) \cite{DORA2022} introduces strengthened requirements for ICT risk management, incident reporting, third-party risk control, and operational continuity across financial entities. DORA reflects a broader recognition that digital infrastructures handling financial assets must demonstrate resilience against cyber threats, internal misuse, and systemic disruptions. Even where institutional custody falls outside strict financial market regulation, the resilience principles embedded in DORA provide a strong reference point for high-assurance system design.

These regulatory developments share a common emphasis on internal controls, separation of responsibilities, traceability of actions, and continuous monitoring. Importantly, they highlight that governance and security are not abstract compliance concepts but architectural requirements. Systems managing crypto-assets must be designed in a manner that enables institutions to demonstrate control over access, authorization workflows, and incident handling procedures.

For institutions involved in criminal investigations and asset confiscation, regulatory alignment carries additional significance. Beyond safeguarding economic value, custody systems must preserve evidentiary integrity, support judicial scrutiny, and withstand external audit. The European regulatory framework therefore reinforces the necessity of embedding structured governance and operational resilience directly into the technical architecture of custody systems.

This regulatory context provides a foundational backdrop for the development of the Secure Custody Framework for Cryptocurrency Assets (SCFCA), which seeks to operationalize governance principles through concrete architectural mechanisms.


% =====================================================
\chapter{Methodology}

\section{Methodological Foundations}

This thesis adopts a design-oriented security engineering methodology grounded in the principles and modeling practices studied in the Master's course \textit{Design and Development of Secure Software}. The work is not driven by coding first; it is driven by security requirements, institutional constraints, and verifiable design decisions.

The methodology follows a model-driven approach inspired by Secure Tropos and structured requirement derivation, with the goal of producing a traceable security architecture for institutional cryptocurrency custody. In particular, the methodology emphasizes:

\begin{itemize}
    \item Integrating security constraints from the earliest design stages
    \item Modeling institutional actors, goals, and dependencies explicitly
    \item Capturing abuse and failure conditions through misuse scenarios
    \item Deriving security requirements systematically from identified risks
    \item Maintaining traceability between threats, requirements, and architectural controls
\end{itemize}

The output of this chapter is therefore a set of engineering artifacts (models, requirements, and traceability links) that support the architectural design and the proof-of-concept validation presented in later chapters.

\section{Security-by-Design and Model-Driven Engineering}

This research follows a security-by-design principle for developing the Secure Custody Framework for Cryptocurrency Assets (SCFCA). The objective is not to deliver a production-ready custody platform, but to design and justify a secure reference architecture suitable for institutional custody in criminal investigations, where auditability, role accountability, and tamper resistance are mandatory.

Security requirements are treated as primary design drivers from the start. The framework is therefore modeled to explicitly address realistic threats such as insider abuse, privilege escalation, unauthorized key usage, custody manipulation, and audit log tampering.

The SCFCA is developed using a top-down, model-driven process that consists of:

\begin{enumerate}
    \item \textbf{Institutional context and actor modeling:} definition of roles, responsibilities, trust assumptions, and separation of duties.
    \item \textbf{Threat identification through misuse scenarios:} modeling how legitimate goals can be abused or bypassed by malicious actors.
    \item \textbf{Requirement derivation:} specification of functional requirements and the corresponding security and non-functional requirements derived from threats and governance constraints.
    \item \textbf{Architectural refinement:} transformation of requirements into architectural components and enforceable controls (e.g., RBAC, dual control, immutable logging).
    \item \textbf{Traceability management:} maintaining explicit links from threats to requirements and from requirements to architectural decisions.
\end{enumerate}

This workflow ensures that security controls are not introduced as ad hoc features. Each control included in the architecture must be justified by a specific threat scenario and mapped to a corresponding requirement, enabling systematic review and later validation.

\section{Threat Analysis Based on Use Cases and Misuse Scenarios}

Threat analysis in this thesis is performed using a misuse-case–driven approach integrated with goal-oriented modeling. Instead of relying only on generic threat taxonomies, threats are identified by analyzing how legitimate custody goals can be disrupted, abused, or bypassed in the SCFCA context.

The analysis distinguishes between two categories of actors:

\begin{itemize}
    \item \textbf{Legitimate institutional actors:} Case Handler, Administrator, and Auditor.
    \item \textbf{Adversarial actors:} External Adversary and Malicious Insider.
\end{itemize}

For each legitimate operational goal (e.g., intake of seized assets, controlled access to wallets, authorization of transfers, and generation of audit evidence), one or more misuse scenarios are defined. These misuse cases represent concrete adversarial objectives such as unauthorized access to custody material, privilege escalation, manipulation of custody actions, audit log tampering, repudiation attempts, and data exfiltration.

Each misuse case is analyzed using the following structure:

\begin{enumerate}
    \item \textbf{Malicious goal:} what the adversary attempts to achieve.
    \item \textbf{Attack path:} how the adversary could realistically pursue the goal within the system and organizational workflow.
    \item \textbf{Mitigation and controls:} security mechanisms that prevent, detect, or limit the impact of the misuse case.
\end{enumerate}

This produces an explicit traceability chain that is maintained throughout the design:

\begin{center}
\textit{Misuse Case} $\rightarrow$ \textit{Threatened Goal} $\rightarrow$ \textit{Security Control} $\rightarrow$ \textit{Formal Requirement}
\end{center}

By linking misuse cases directly to institutional workflows (such as dual-control authorization, separation of duties, and tamper-evident audit logging), the threat analysis avoids abstract threat lists and instead drives concrete requirement derivation. The resulting output of this phase is a structured set of threats and mitigations that directly informs both the requirement specification and the architectural controls defined later in the thesis.

The threat analysis is performed in the following steps:

\begin{enumerate}
    \item Identification of critical assets and custody goals.
    \item Identification of actors, trust assumptions, and adversary capabilities.
    \item Definition of misuse cases targeting specific goals and custody operations.
    \item Mapping of misuse cases to candidate controls (preventive and detective).
    \item Formalization of selected controls as security requirements.
\end{enumerate}

This approach supports defense-in-depth by combining governance mechanisms (dual control and accountability) with technical controls (authentication, authorization, tamper-evident logging, and monitoring), ensuring that security requirements are justified by explicit and realistic risk scenarios.

\section{Model-Driven Architectural Development}

The architecture of the Secure Custody Framework for Cryptocurrency Assets (SCFCA) is developed using a model-driven engineering approach. Visual models are used as the primary mechanism to define system boundaries, responsibilities, trust assumptions, and security controls before implementing any proof-of-concept (PoC) components. This reduces ambiguity and enables systematic traceability from requirements and threats to architectural decisions.

The development workflow combines conceptual modeling and controlled implementation artifacts using the following toolchain:

\begin{itemize}
    \item \textbf{Visual Paradigm:} creation of requirements and architecture models (Secure Tropos and UML).
    \item \textbf{Secure Tropos / goal-oriented modeling:} representation of actor goals, dependencies, and misuse scenarios.
    \item \textbf{UML diagrams:} Use Case, Component, Sequence, and Deployment diagrams to describe functional behavior and structural decomposition.
    \item \textbf{PlantUML (when applicable):} text-based diagram representations to improve reproducibility and change tracking.
    \item \textbf{Version control repository:} management of models, documentation, and traceability artifacts.
    \item \textbf{Visual Studio:} implementation of a minimal PoC to validate selected security properties.
\end{itemize}

\subsection{Modeling Phase (Visual Paradigm)}

All conceptual and architectural models are developed in Visual Paradigm. The modeling phase produces the artifacts required to move from institutional goals and threats to an explicit architecture. In particular, the following models are created:

\begin{itemize}
    \item Actor models (Case Handler, Administrator, Auditor, External Adversary, Malicious Insider)
    \item Use Case and Misuse Case diagrams
    \item Secure Tropos goal models, including dependencies and security constraints
    \item Component diagrams defining system decomposition and responsibility allocation
    \item Trust boundary identification and security-relevant interfaces
    \item Sequence diagrams for key workflows (e.g., custody intake, dual-approval transfer authorization, audit evidence generation)
\end{itemize}

Visual Paradigm is used to enforce modeling consistency and to ensure that security assumptions are explicit. In particular, dependencies between actors, required approvals, and audit responsibilities are modeled directly, so that separation of duties and dual control are reflected structurally in the design rather than treated as informal organizational statements.

\subsection{Requirement-to-Architecture Traceability}

A core outcome of the model-driven approach is traceability. Threats identified through misuse scenarios are translated into security requirements, and each security requirement is mapped to one or more architectural controls (e.g., RBAC enforcement points, dual-control workflows, tamper-evident audit logging, and monitoring hooks).

Traceability is maintained through:

\begin{itemize}
    \item links between misuse cases and the threatened system goals,
    \item mapping of threats to mitigation controls,
    \item formal security requirements derived from the selected mitigations,
    \item architectural components explicitly responsible for enforcing each requirement.
\end{itemize}

This traceability structure is later used during validation to justify that each architectural decision is risk-driven and that critical threats are addressed by enforceable controls rather than by informal assumptions.

\subsection{Repository and Version Control (GitLab)}

All thesis artifacts are managed in a GitLab repository to ensure reproducibility, controlled evolution of the design, and auditable change history. The repository is used to version:

\begin{itemize}
    \item the Overleaf/LaTeX source of the thesis,
    \item exported Visual Paradigm diagrams and supporting documentation,
    \item traceability matrices (threats--requirements--controls),
    \item PlantUML sources (when used),
    \item proof-of-concept source code and configuration files.
\end{itemize}

Using GitLab provides a consistent workflow for iterative refinement and peer/tutor review, while preserving a chronological record of design decisions and security-related changes.

\subsection{Proof-of-Concept Implementation (Visual Studio)}

A minimal proof-of-concept (PoC) is implemented using Visual Studio to demonstrate feasibility of selected security properties derived from the models. The PoC does not aim to implement a full custody system; instead, it focuses on mechanisms that are essential to the SCFCA security claims, such as:

\begin{itemize}
    \item enforcement of role separation and restricted privileges,
    \item dual-control authorization for sensitive operations (e.g., transfer approval),
    \item generation of tamper-evident audit records and traceable custody actions.
\end{itemize}

The PoC is used as validation support: it provides concrete evidence that the modeled controls can be enforced in practice and that key workflows can be implemented without contradicting the security constraints captured in the architecture.

\subsection{Architectural Refinement}

Architectural refinement is performed iteratively. Each iteration starts from updated requirements or newly identified misuse scenarios and results in adjustments to the architecture and its controls. Refinement is therefore driven by traceability:

\begin{itemize}
    \item when a misuse case is added or modified, the affected goals and requirements are updated,
    \item requirements changes trigger updates to the responsible architectural components,
    \item architectural updates are reviewed to ensure they preserve separation of duties, dual control, and audit integrity.
\end{itemize}

This refinement cycle continues until the architecture provides consistent coverage of the prioritized threats and the PoC can validate the feasibility of the most critical controls.

\section{Validation and Proof-of-Concept Strategy}

The validation approach in this thesis aims to confirm that the proposed architecture is internally consistent and that the derived security requirements are enforceable within the modeled custody workflows. Validation is therefore design-centric: it focuses on correctness of security constraints under the defined threat assumptions, rather than on performance, scalability, or production hardening.

A minimal proof-of-concept (PoC) complements the architectural validation by demonstrating feasibility of selected high-risk controls in a controlled implementation setting. The PoC is intentionally limited in scope and is used to provide evidence for key claims such as:

\begin{itemize}
    \item enforcement of separation of duties and role constraints,
    \item dual-control authorization for sensitive actions,
    \item tamper-evident audit logging and traceable custody actions.
\end{itemize}

Validation outputs are treated as traceable artifacts: models, requirement mappings, and PoC observations are all linked to specific threats and requirements to support auditable justification of architectural controls.

\section{Validation Strategy}

Validation is performed through a combination of modeling checks, traceability verification, and targeted PoC tests. The goal is to ensure that: (i) the architecture enforces the security requirements derived from misuse scenarios, and (ii) critical custody workflows cannot be executed in ways that violate governance constraints (e.g., bypassing dual control).

The validation process includes:

\begin{itemize}
    \item model consistency and completeness checks,
    \item verification of requirement-to-component traceability,
    \item review of misuse-case coverage and mitigation adequacy,
    \item PoC-based testing of selected workflows and security properties,
    \item verification of audit log integrity and event traceability.
\end{itemize}

The following subsections describe the concrete validation steps and the evidence collected.

\subsection{Model Consistency Validation (Visual Paradigm)}

Model validation is performed in Visual Paradigm to ensure that diagrams remain consistent across the different modeling views (actors, goals, use/misuse cases, and architecture). The validation checks focus on:

\begin{itemize}
    \item correctness of system boundaries and trust assumptions,
    \item consistency of actor responsibilities and dependencies,
    \item alignment between misuse cases and the threatened goals,
    \item completeness of architectural components responsible for enforcing key requirements.
\end{itemize}

This step prevents contradictions such as security requirements that are not enforceable by any component, or architectural controls that are not justified by an identified risk.

\subsection{Requirement Traceability Verification}

Traceability verification confirms that each high-priority threat leads to at least one security requirement and that each security requirement is implemented as one or more architectural controls. Evidence is maintained through a traceability matrix linking:

\begin{center}
\textit{Threat/Misuse Case} $\rightarrow$ \textit{Security Requirement} $\rightarrow$ \textit{Architectural Control} $\rightarrow$ \textit{Validation Evidence}
\end{center}

This step ensures that security is not treated as an informal claim: architectural decisions must remain justified by explicit threat scenarios and mapped requirements.

\subsection{Proof-of-Concept Implementation Validation (Visual Studio)}

The PoC is validated by implementing a minimal subset of SCFCA workflows and demonstrating that the security constraints are enforceable in practice. The validation focuses on:

\begin{itemize}
    \item role enforcement and privilege restrictions consistent with the RBAC model,
    \item dual-control workflow behavior (e.g., an operation cannot complete without the required approvals),
    \item generation of audit events that represent custody actions in a structured and reviewable form.
\end{itemize}

The PoC is evaluated based on whether it supports the architectural assumptions, not on whether it provides a complete custody feature set.

\subsection{Log Integrity and Traceability Verification}

Audit evidence is validated by verifying that custody actions produce traceable and tamper-evident log records. The validation aims to demonstrate that:

\begin{itemize}
    \item critical actions are logged with sufficient context (who, what, when, and under which authorization),
    \item audit records cannot be modified without detection (tamper evidence),
    \item audit events can be correlated to specific workflows and approvals.
\end{itemize}

Where applicable, the PoC uses integrity mechanisms (e.g., chained hashes or append-only storage semantics) to support the tamper-evident property.

\subsection{Limitations of Validation}

Validation in this thesis is limited to architectural correctness and feasibility demonstration under defined assumptions. The following aspects are explicitly out of scope:

\begin{itemize}
    \item performance and scalability benchmarking,
    \item operational deployment and production hardening,
    \item formal verification of cryptographic protocols,
    \item empirical user studies or organizational process audits.
\end{itemize}

These limitations are consistent with the thesis scope: the primary contribution is a security-driven, traceable reference architecture supported by a minimal feasibility PoC.


\section{Toolchain and Development Environment}

This thesis relies on a small, consistent toolchain to ensure that modeling, documentation, and validation artifacts remain reproducible and traceable throughout the project lifecycle. The toolchain is selected to support (i) model-driven design, (ii) version-controlled evolution of artifacts, and (iii) implementation of a minimal proof of concept.

\subsection{Modeling Environment (Visual Paradigm)}

Visual Paradigm is used to develop the conceptual and architectural models, including Secure Tropos goal models and UML diagrams (Use Case, Component, Sequence, and Deployment). Exports of the diagrams are treated as versioned artifacts to support review and traceability.

\subsection{Version Control and Traceability (GitLab and GitHub)}

GitLab is used as the central repository (source of truth) for all project artifacts, including the thesis source, model exports, traceability matrices, and proof-of-concept code. Version control is used to preserve design evolution and to maintain an auditable change history for security-relevant decisions.

For dissemination and external sharing, a mirrored copy of the repository may also be maintained on GitHub. In that case, GitLab remains the authoritative repository, and GitHub is treated as a read-only mirror to avoid divergence between artifact versions.

\subsection{Implementation Environment (Visual Studio)}

Visual Studio is used to implement a minimal proof of concept that supports validation of selected security properties (e.g., dual control enforcement and tamper-evident audit logging). The PoC is intentionally limited and is treated as supporting evidence rather than the primary contribution.

\subsection{Documentation Environment (Overleaf)}

The thesis is written in Latex using Overleaf. The source is synchronized with the GitLab repository to ensure reproducibility and consistent versioning of the final document.

\subsection{Integrated Development Flow}

The overall workflow is iterative: models and requirements are refined based on misuse scenarios, architectural controls are updated accordingly, and validation evidence is collected through traceability checks and targeted PoC tests. This integrated flow ensures that changes in threats or requirements propagate consistently to the architecture and its supporting validation artifacts.



% =====================================================
\chapter{Threat Modeling}

\section{Threat Modeling Scope and Objectives}

This chapter presents the structured threat analysis performed for the Secure Custody Framework for Cryptocurrency Assets (SCFCA). The purpose of this chapter is not to provide a generic overview of cybersecurity threats, but to identify concrete risk scenarios that directly affect institutional cryptocurrency custody under criminal investigation contexts.

The threat model focuses on risks that may compromise:

\begin{itemize}
    \item Custody integrity (unauthorized asset manipulation or transfer)
    \item Role separation and governance constraints
    \item Auditability and non-repudiation
    \item Confidentiality of case-related information
    \item System availability during operational use
\end{itemize}

The analysis considers both external adversaries and malicious insiders. Given the institutional setting, insider threats are treated as equally critical as external attacks, particularly in scenarios involving privilege abuse or misuse of authorized access.

The output of this chapter is a structured set of misuse cases, associated attack paths, and mitigation measures that serve as the foundation for the formal security requirements and architectural controls defined in subsequent chapters.

\section{Threat Model Assumptions and Boundaries}

A clear definition of system boundaries and trust assumptions is necessary to ensure that the threat model remains realistic and technically coherent. The Secure Custody Framework for Cryptocurrency Assets (SCFCA) is modeled as an institutional custody management system operating within a controlled governmental environment.

\subsection{System Boundary}

The system boundary includes:

\begin{itemize}
    \item User authentication and role management mechanisms
    \item Case management and ticketing workflows
    \item Custody authorization logic (dual-control enforcement)
    \item Audit logging and traceability components
    \item Interfaces with the custody infrastructure responsible for cryptographic operations
\end{itemize}

The custody infrastructure (e.g., key management and transaction signing components) is treated as a controlled subsystem that executes approved operations but does not expose private keys directly to human actors.

External blockchain networks are considered outside the system boundary. The SCFCA interacts with them only through defined execution interfaces.

\subsection{Trust Assumptions}

The following trust assumptions are defined for this threat model:

\begin{itemize}
    \item Cryptographic primitives (e.g., hashing and digital signatures) are assumed to be secure and correctly implemented.
    \item The operating environment is institutionally controlled, but not immune to insider misuse.
    \item Administrators and case handlers may act maliciously if governance controls fail.
    \item External adversaries may attempt unauthorized access or system disruption.
    \item The underlying blockchain network behaves according to its consensus rules and is not considered compromised.
\end{itemize}

The threat model does not assume that all authenticated users are trustworthy. Instead, the architecture is explicitly designed to remain secure even if one privileged role attempts to abuse its access.

\subsection{Out-of-Scope Considerations}

The following aspects are considered outside the scope of this threat model:

\begin{itemize}
    \item Physical attacks against secure facilities
    \item Compromise of national infrastructure or state-level adversary control
    \item Formal cryptographic proof of algorithm correctness
    \item Economic attacks against blockchain consensus mechanisms
\end{itemize}

By clearly defining system boundaries and trust assumptions, the threat analysis in the following sections focuses on realistic governance failures, misuse scenarios, and technical abuse paths that directly impact institutional cryptocurrency custody.
\section{Threat Taxonomy}

Before defining specific misuse scenarios, it is useful to classify threats according to their origin and intent. In cybersecurity literature, threats are commonly categorized based on whether they originate internally or externally, and whether they result from malicious or non-malicious actions.

Figure~\ref{fig:threat_taxonomy} illustrates a general taxonomy of threats adapted from Jouini et al. (2014). The model distinguishes between external and internal threats and further classifies them into human, environmental, and technological sources. Human threats may be malicious (intentional attacks) or non-malicious (accidental actions), while environmental and technological threats are typically non-malicious and accidental in nature.

Within the context of the SCFCA, the primary focus of the threat model is on intentional human threats, both external adversaries and malicious insiders. However, accidental internal actions and technological failures are also considered where they may impact custody integrity, availability, or audit reliability.

Threat graphs are commonly used in cyber threat intelligence to model adversarial paths and objectives \cite{Lee2023}.

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{figure 11.png}
    \caption{Taxonomy of threats. Adapted from Jouini et al. (2014).}
    \label{fig:threat_taxonomy}  \cite{Lee2023}
\end{figure}


\section{Assets and Security Objectives}

Before identifying misuse scenarios, it is necessary to define the assets that require protection within the Secure Custody Framework for Cryptocurrency Assets (SCFCA). In this context, assets are not limited to cryptocurrency balances. They also include governance mechanisms and evidentiary records that are essential to institutional integrity.

\subsection{Primary Assets}

The primary assets considered in this threat model are:

\begin{itemize}
    \item \textbf{Seized cryptocurrency assets:} digital assets recorded under a CaseID and associated with frozen valuation snapshots.
    \item \textbf{Custody authorization workflows:} dual-control approval mechanisms governing sensitive operations such as transfers or reassignment.
    \item \textbf{Audit records and logs:} tamper-evident records of system actions, approvals, and execution outcomes.
    \item \textbf{Role and access control configurations:} definitions of privileges and enforcement of separation of duties.
    \item \textbf{Case-related information:} metadata, documentation, and sensitive information associated with investigations.
\end{itemize}

\subsection{Security Objectives}

Based on these assets, the following security objectives guide the threat analysis:

\begin{itemize}
    \item \textbf{Integrity:} Seized asset records and custody actions must not be modified without proper authorization and traceability.
    \item \textbf{Accountability:} All actions must be attributable to authenticated users and preserved in tamper-evident logs.
    \item \textbf{Separation of Duties:} No single actor must be able to initiate and execute custody-impacting actions independently.
    \item \textbf{Confidentiality:} Sensitive case information and identity mappings must be protected from unauthorized access.
    \item \textbf{Availability:} The system must remain operational for legitimate institutional use and resist disruption attempts.
\end{itemize}

These objectives define the protection goals that misuse cases attempt to violate. The following sections analyze concrete adversarial scenarios targeting these assets and objectives.

\section{Threat Graph–Based Misuse Analysis}

Threat graphs are used to visually represent the different paths an attacker may follow in order to achieve a specific objective. Instead of listing threats in isolation, a threat graph models how adversarial goals can be reached through multiple tactics and techniques.

In this thesis, threat graphs are constructed for each high-risk misuse case identified in the SCFCA system. Each graph begins with a clearly defined malicious goal and works backwards through possible ATT\&CK tactics and techniques that an adversary could realistically apply within the institutional custody context.

This approach allows the analysis to focus on concrete attack paths rather than abstract threat categories. It also supports systematic mapping between adversarial techniques (MITRE ATT\&CK) and defensive countermeasures (MITRE D3FEND), ensuring that mitigation strategies address realistic attack sequences.

\subsection{MU-7 – Case Data Exfiltration (Threat Graph Analysis)}

\textbf{Attacker Goal.}  
Exfiltrate confidential case-related data or sensitive custody information from the SCFCA system.

Maintaining confidentiality of case narratives, personal data, and asset records is a critical institutional security objective. A successful exfiltration may compromise investigations, violate legal protections, and damage institutional credibility.

Working backwards from this malicious objective, the attacker must successfully apply the ATT\&CK tactic:

\begin{itemize}
    \item \textbf{Exfiltration – TA0010}
\end{itemize}

This may be achieved through one or more techniques, such as:

\begin{itemize}
    \item Exfiltration Over C2 Channel – T1041
    \item Exfiltration Over Alternative Protocol – T1048
    \item Exfiltration Over Web Service – T1567
     \item Exfiltration Over Physical Medium – TA1052
\end{itemize}

To perform exfiltration, the attacker must first obtain sufficient access privileges. This typically requires one or more of the following tactics:

\begin{itemize}
    \item Credential Access – TA0006
    \item Privilege Escalation – TA0004
    \item Lateral Movement – TA0008
    \item Execution – TA0002
\end{itemize}

In the SCFCA context, realistic attack paths include:

\begin{enumerate}
    \item Compromise of a Case Handler account via phishing (T1566) leading to Valid Account usage (T1078).
    \item Exploitation of broken access control allowing Insecure Direct Object Reference (IDOR).
    \item Insider abuse of legitimate access privileges.
\end{enumerate}

The corresponding defensive perspective maps to MITRE D3FEND mechanisms such as:

\begin{itemize}
    \item Multi-factor authentication enforcement
    \item Role-based access control validation
    \item Data access logging and anomaly detection
    \item Network monitoring for abnormal outbound data flows
\end{itemize}

By modeling the attack graph in this manner, the threat analysis highlights that preventing exfiltration requires not only perimeter controls, but also strict privilege enforcement, monitoring, and separation of duties within custody workflows.

\begin{figure}
    \centering
    \includegraphics[width=0.75\linewidth]{figure10.png}
    \caption{Example of a threat graph , MU-7 Case data Exfiltration \cite{Lee2023}. }
    \label{fig:placeholder}
\end{figure}

\subsection{MU-1 – Unauthorized Access (Threat Graph Analysis)}

\textbf{Attacker Goal.}  
The adversary aims to gain unauthorized access to the SCFCA system in order to later manipulate custody workflows, escalate privileges, or exfiltrate sensitive case information. Unauthorized access represents a foundational threat because it enables multiple secondary misuse scenarios.

Working backwards from this objective, the attacker must ultimately succeed in abusing a valid authentication context. Within the MITRE ATT\&CK framework, this corresponds primarily to:

\begin{itemize}
    \item \textbf{Valid Accounts – T1078}
\end{itemize}

Alternative direct approaches may also include:

\begin{itemize}
    \item \textbf{Brute Force – T1110}
\end{itemize}

To obtain valid credentials or authenticated session control, the attacker may follow several realistic attack paths in the institutional custody context.

These alternative paths form the basis of the MU-1 threat graph. Each branch illustrates a distinct route through which the attacker may reach the same malicious objective.

\textbf{Security Impact.}  
If successful, unauthorized access compromises the confidentiality of case data, undermines role-based access control enforcement, and may enable privilege escalation or manipulation of custody operations. In an institutional custody system, even temporary unauthorized access may jeopardize evidentiary integrity and institutional accountability.

\textbf{Defensive Considerations.}  
From a defensive perspective, mitigation requires layered controls including:

\begin{itemize}
    \item Multi-factor authentication enforcement
    \item Rate limiting and account lockout mechanisms
    \item Credential storage protection and endpoint monitoring
    \item Session binding and re-authentication for sensitive actions
    \item Continuous authentication logging and anomaly detection
\end{itemize}

The threat graph analysis demonstrates that preventing unauthorized access is not dependent on a single control, but on a combination of authentication hardening, credential protection, and session monitoring mechanisms.
\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{figure9.png}
    \caption{MU-1 Threat Graph  : Unauthorized Access }
    \label{fig:placeholder}
\end{figure}

\subsection{MU-2 – Privilege Escalation Exploit}

MU-2 addresses the scenario in which an attacker who already possesses some level of access to the SCFCA system attempts to escalate privileges in order to obtain administrative control. Unlike MU-1, which focuses on unauthorized initial access, this misuse case assumes that the adversary has successfully authenticated as a lower-privileged user (e.g., Case Handler) or has compromised a non-administrative account.

The attacker’s objective is to transition from limited access to elevated privileges, ultimately gaining Administrator-level capabilities within the custody system. This would enable manipulation of custody workflows, modification of asset records, or bypassing governance controls such as dual approval mechanisms.

From a MITRE ATT\&CK perspective, privilege escalation may involve the following tactics and techniques:

\begin{itemize}
    \item Exploitation for Privilege Escalation – T1068
    \item Abuse Elevation Control Mechanism – T1548
    \item Valid Accounts – T1078 (leveraging already compromised credentials)
    \item Exploitation of Application Vulnerabilities (e.g., injection, insecure API endpoints)
\end{itemize}

The threat graph for MU-2 models alternative attacker paths that converge on the attacker goal of achieving elevated privileges within SCFCA. Possible escalation routes include:

\begin{itemize}
    \item Exploiting misconfigured RBAC policies or improper role validation,
    \item Manipulating backend APIs to bypass authorization checks,
    \item Exploiting software vulnerabilities to gain code execution in a privileged context,
    \item Abusing token handling or session management flaws to assume a higher-privileged identity.
\end{itemize}

All attack branches ultimately converge on the attacker goal:

\begin{center}
\textit{Administrator-Level Access to SCFCA}
\end{center}

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{figure 12.png}
    \caption{MU-2 – Privilege Escalation Threat Graph}
    \label{fig:placeholder}
\end{figure}

From a defensive standpoint, the architecture mitigates these escalation paths through strict role-based access control (SR-1), controlled role assignment mechanisms (SR-4), privilege escalation prevention controls (SR-3), and enforcement of authorization checks at every security-sensitive endpoint. Additionally, audit logging and traceability mechanisms reduce the likelihood that unauthorized privilege transitions remain undetected.

By modeling privilege escalation explicitly as a graph of converging attacker options, the analysis highlights that elevated access is rarely the result of a single failure. Rather, it typically emerges from combinations of misconfigurations, insufficient authorization enforcement, or exploitable vulnerabilities. The architectural design of SCFCA therefore enforces privilege boundaries structurally, rather than relying solely on procedural controls.

The threat graphs developed in this chapter are grounded in structured threat intelligence sources, most notably the MITRE ATT\&CK and MITRE D3FEND frameworks, which provide detailed mappings of adversarial tactics, techniques, and corresponding defensive countermeasures. These sources, complemented by broader open intelligence and the technical knowledge acquired throughout this Master's program—particularly in secure software design and security engineering best practices—form the analytical foundation of the SCFCA threat model. 

By systematically mapping misuse scenarios to established attack techniques and defensive controls, this analysis moves beyond abstract risk discussion and establishes a concrete, evidence-based understanding of how the system may be targeted and how those threats can be mitigated. 

With this structured threat knowledge in place, the work can now transition from adversarial analysis to architectural design. The next chapter builds directly upon these findings to define the security-driven architecture of the SCFCA framework, ensuring that its components, controls, and governance mechanisms are explicitly aligned with the identified threat landscape.



% =====================================================
\chapter{System Architecture}
\section{System Actors}
The Secure Custody Framework for Cryptocurrency Assets (SCFCA) operates within an institutional environment involving multiple actors with clearly separated responsibilities and access privileges. The explicit definition of system actors is essential to enforce separation of duties, prevent abuse of privileges, and ensure accountability and auditability across all custody operations.

All interactions with the system are performed by authenticated users operating under predefined roles. Each role is associated with a specific set of permissions that strictly limit the actions the actor can perform.

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure 1 . System overview ( simplified first idea ).png}
    \caption{ System overview ( simplified first idea , use cases)}
    \label{fig:placeholder}
\end{figure}

\subsection{Identity Representation}
All users within the system are represented internally by pseudonymous UserIDs. These identifiers do not encode the user’s role, real-world identity, or organizational position. Role information and access privileges are managed separately through the system’s access control mechanisms. This design minimizes information leakage, prevents bias, and ensures that audit records remain operationally meaningful without exposing unnecessary personal data.

The mapping between UserIDs and real-world identities is restricted to authorized administrative processes outside the scope of the audit role.


\subsection{Case Handler}
The Case Handler represents the authorized investigative authority responsible for managing a specific case (e.g., a prosecutor or designated investigative officer). This actor is responsible for initiating all custody-related requests within the system.

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure2.png}
    \caption{Tropo Analysis diagram (case handler’s goals)}
    \label{fig:placeholder2}
\end{figure}

The Case Handler can:

\begin{itemize}
\item Access full details only for cases assigned to them
\item Register requests by creating tickets associated with a case
\item Attach supporting documentation to tickets
\item Generate informational reports for their assigned cases
\end{itemize}

The Case Handler cannot:
\begin{itemize}
\item Modify case or asset data directly
\item Execute asset transfers or conversions
\item Approve or reject tickets
\item Access detailed information of cases not assigned to them 
\end{itemize}


\subsection{Administrator}
The Administrator is responsible for managing and executing approved custody and governance operations within the system. Administrators act as validators and executors of requests initiated by Case Handlers.

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure3.png}
    \caption{Tropo Analysis Diagram ( Administrator’s goals)}
    \label{fig:placeholder}
\end{figure}


The Administrator can:

\begin{itemize}
\item Create and manage user accounts
\item Create cases and assign or reassign case handlers
\item Modify system records without an approved ticket
\item All administrative actions are fully logged and subject to audit.
\end{itemize}

The Administrator cannot:

\begin{itemize}
\item Initiate tickets
\item Approve tickets related to actions they have requested indirectly
\item Review, approve, or reject tickets
\item Execute approved custody actions (e.g., transfers, reassignment)
\item Access full case details, including sensitive information
\item Generate system-wide and case-specific reports
\end{itemize}

\subsection{Auditor}
The Auditor is responsible for independent oversight of the system’s operation. This role is strictly read-only and is designed to detect irregularities, verify compliance, and support accountability.
The Auditor can:
\begin{itemize}
\item View all CaseIDs
\item Monitor all system actions and events
\item Review tickets, approvals, rejections, and execution outcomes
\item Generate and download audit reports for any time period or case
\item Verify integrity of logs and documentation
\end{itemize}


The Auditor cannot:
\begin{itemize}
\item Modify cases, assets, tickets, or assignments
\item Approve or reject tickets
\item Execute custody actions
\item Access real-world identities of users
\item Access personally identifiable information (PII) or confidential case narrativesormation
\end{itemize}
\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure4.png}
    \caption{Tropo Analysis Diagram ( Auditor’s goals) }
    \label{fig:placeholder}
\end{figure}

\subsection{External Adversary}
The External Adversary represents any unauthorized entity attempting to compromise the system. This includes attackers seeking to gain unauthorized access, escalate privileges, manipulate custody operations, or tamper with audit records. While not interacting through legitimate system interfaces, this actor is considered in the system’s threat model to ensure resilience against external attacks. Misuse cases: 

MU-1 Unauthorized Access

MU-2 Privilege Escalation Exploit

MU-9 DoS

MU-7 (if credentials stolen)

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure5.png}
    \caption{Tropo Analysis Diagram ( External Adversary’s goals)}
    \label{fig:placeholder}
\end{figure}



\subsection{Malicious Insider}
The Malicious Insider represents an authenticated internal user who intentionally abuses legitimate access privileges to compromise custody integrity, confidentiality, or auditability.
This actor may correspond to:

- A compromised Case Handler

- A compromised Administrator

- A privileged technical operator

- Any authorized user acting with malicious intent


Unlike the External Adversary, the Malicious Insider already possesses valid authentication credentials and operates within legitimate system boundaries. The risk arises not from bypassing authentication mechanisms, but from abusing authorized privileges, exploiting workflow weaknesses, or attempting to manipulate governance controls.

The Malicious Insider may attempt to:

\begin{itemize}
\item Bypass dual approval mechanisms
\item Manipulate ticket states
\item Modify or tamper with audit logs
\item Alter seized asset records
\item Replace or manipulate supporting documentation
\item Replay or duplicate custody executions
\item Access sensitive case data beyond authorized scope
\end{itemize}

The design of SCFCA explicitly mitigates insider threats through:
\begin{itemize}
\item Strict separation of duties
\item Dual administrative approval enforcement
\item Immutable asset records
\item Tamper-evident audit logging
\item Least-privilege role enforcement
\item Full action traceability and non-repudiation
\end{itemize}

The inclusion of the Malicious Insider actor ensures that the framework addresses not only perimeter security risks but also internal abuse scenarios, which are particularly critical in institutional custody environments.

Misuse cases : 

MU-3 Bypass Dual Approval

MU-4 Log Tampering

MU-5 Asset Manipulation

MU-6 Document Tampering

MU-8 Replay Execution

MU-7 (internal abuse)

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure6.png}
    \caption{Tropo Analysis Diagram ( Malicious Insider’s goals)}
    \label{fig:placeholder}
\end{figure}



\subsection{Misuse Case – Threat and Mitigation Mapping}

In addition to legitimate use cases, the Secure Custody Framework for Cryptocurrency Assets (SCFCA) explicitly models malicious goals through misuse cases. These misuse cases represent intentional attempts by adversarial actors to compromise the confidentiality, integrity, availability, or auditability of institutional cryptocurrency custody operations.

Unlike functional use cases, which describe intended system behavior, misuse cases describe adversarial objectives and potential exploitation paths. Their inclusion serves two primary purposes:

1.To formally identify security-relevant threats against the system.

2.To ensure that every identified threat is mitigated by specific security controls and requirements.


Each misuse case defines:

a. A malicious goal (what the adversary aims to achieve),

b. Potential attack vectors (how the goal may be attempted),

c. Corresponding mitigation measures (which system requirements or controls prevent, detect, or contain the threat).



This structured mapping establishes traceability between:


Misuse Case → Security Control → Functional/Security Requirement


By linking each malicious goal to explicit mitigation mechanisms, the framework ensures that security controls are not arbitrary but directly justified by threat analysis.


Furthermore, this approach supports:
\begin{itemize}
\item Defense-in-depth design,
\item Verification of security coverage,
\item Architectural traceability between Chapter 3 (Requirements) and Chapter 5 (Design and Architecture).
\end{itemize}


The following table summarizes the identified misuse cases, their attack vectors, and the corresponding mitigation measures embedded in the system requirements.



\begin{longtable}{|p{1.2cm}|p{3.2cm}|p{3.2cm}|p{3.8cm}|p{4.5cm}|}
\caption{Misuse Case - Threat \& Mitigation Mapping}
\\\hline
\textbf{ID} & \textbf{Misuse Case} & \textbf{Malicious Goal} & \textbf{Typical Attack Vectors} & \textbf{Mitigation Measures (Mapped to Requirements)} \\
\\\hline
\endfirsthead

\hline
\textbf{ID} & \textbf{Misuse Case} & \textbf{Malicious Goal} & \textbf{Typical Attack Vectors} & \textbf{Mitigation Measures (Mapped to Requirements)} \\
\hline
\endhead

MU-1 & Attempt to Gain Unauthorized Access & Log into the system without valid credentials & Brute force, credential stuffing, phishing, stolen credentials & SR-5 MFA; SR-6 Re-authentication for sensitive actions; SR-7 Session traceability; SR-8 Logging \\
\hline

MU-2 & Exploit Privilege Escalation Vulnerability & Become Administrator from Case Handler or external account & RBAC misconfiguration, API manipulation, injection attacks & SR-1 Least Privilege; SR-3 Privilege Escalation Prevention; SR-4 Controlled Role Assignment \\
\hline

MU-3 & Execute Custody Action Without Dual Approval & Trigger asset transfer without two admin approvals & Ticket state manipulation, direct API call to execution endpoint, race condition exploit & SR-12 Dual Approval Enforcement; FR-17 Ticket Approval Rule; SR-13 Execution Traceability \\
\hline

MU-4 & Modify or Delete Audit Logs & Hide malicious activity & Database manipulation, filesystem access, log deletion & SR-9 Tamper-Evident Logs; SR-10 Log Deletion Prevention; SR-11 Non-Repudiation; Append-only storage \\
\hline

MU-5 & Alter Seized Asset Data & Modify asset quantities or frozen valuation snapshot & DB injection, insider manipulation, unauthorized admin change & SR-15 Asset Data Immutability; FR-12 Asset Facts Immutability \\
\hline

MU-6 & Document Tampering & Replace or alter supporting PDF evidence & File replacement, DB hash modification & SR-16 Document Integrity Verification; FR-23 Document Hashing \\
\hline

MU-7 & Case Data Exfiltration & Access PII or confidential case narratives & IDOR, broken access control, API abuse & FR-3 RBAC; SR-18 Restricted Access; SR-19 Audit Privacy Boundary \\
\hline

MU-8 & Replay Custody Action & Execute same transfer twice & Resubmitting transaction, manipulating execution state & FR-27 Transaction Linking; SR-13 Execution Traceability \\
\hline

MU-9 & Denial of Service & Prevent system usage & API flooding, login flooding, ticket spam & NFR-1 Availability; Rate limiting \\
\hline

\end{longtable}


MU-1 (Unauthorized Access) → threatens → "Access full details for assigned cases"


MU-2 (Privilege Escalation) → threatens → "Create and manage user accounts"


MU-3 (Bypass Dual Approval) → threatens → "Execute approved custody actions"


MU-4 (Modify Logs) → threatens → "Monitor all system actions and events"


MU-5 (Alter Asset Data) → threatens → "Maintain seized asset records"


MU-6 (Document Tampering) → threatens → "Attach supporting documentation"

MU-7 (Data Exfiltration) → threatens → "Access full case details"

MU-8 (Replay Action) → threatens → "Execute approved custody actions"

MU-9 (DoS) → threatens → "System availability / Generate reports / Submit tickets"

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure7.png}
    \caption{Tropo Analysis Diagram (Threat-goals relations)}
    \label{fig:placeholder}
\end{figure}

\subsection{Mitigation Measures (Security Countermeasures)}

In order to address identified misuse cases and threat scenarios, a set of security mitigation measures is defined at the design level. These measures represent security goals and architectural constraints that directly counteract the malicious objectives modeled in the threat analysis.
Each mitigation measure is derived from the formal Security Requirements defined in Section 3.3 and is conceptually mapped to one or more misuse cases. The purpose of this mapping is to demonstrate traceability between identified threats and the corresponding technical or procedural controls implemented within the Secure Custody Framework for Cryptocurrency Assets (SCFCA).

\begin{figure}
    \centering
    \includegraphics[width=1\linewidth]{Figure8.png}
    \caption{Tropo Analysis Diagram (Mitigation Measures )}
    \label{fig:placeholder}
\end{figure}

The mitigation measures focus on:

Preventing unauthorized access and privilege escalation

Enforcing dual control and separation of duties

Protecting custody integrity and asset immutability

Ensuring auditability and non-repudiation

Preserving confidentiality of sensitive case information

Maintaining system availability and resilience

\begin{longtable}{|p{1.2cm}|p{4.2cm}|p{4.8cm}|p{3.5cm}|}

\caption{Mitigation Measures Use Cases -- Threat \& Mitigation Mapping}
\label{tab:mitigation-mapping} \\

\hline
\textbf{ID} & \textbf{Mitigation Measure } & \textbf{Requirements} & \textbf{Misuse Case} \\
\hline
\endfirsthead

\hline
\textbf{ID} & \textbf{Mitigation Measure } & \textbf{Requirements} & \textbf{Misuse Case} \\
\hline
\endhead

MM-1 & Ensure authenticated access (strong authentication) & SR-5 MFA; SR-6 Re-authentication for sensitive actions; SR-7 Session traceability; SR-8 Logging & Attempt to Gain Unauthorized Access \\
\hline

MM-2 & Prevent privilege escalation / enforce controlled role assignment & SR-1 Least Privilege; SR-3 Privilege Escalation Prevention; SR-4 Controlled Role Assignment & Exploit Privilege Escalation Vulnerability \\
\hline

MM-3 & Enforce dual-control for custody actions & SR-12 Dual Approval Enforcement; FR-17 Ticket Approval Rule; SR-13 Execution Traceability & Execute Custody Action Without Dual Approval \\
\hline

MM-4 & Ensure tamper-evident, append-only audit logs & SR-9 Tamper-Evident Logs; SR-10 Log Deletion Prevention; SR-11 Non-Repudiation; Append-only storage & Modify or Delete Audit Logs \\
\hline

MM-5 & Maintain immutability of seized asset records & SR-15 Asset Data Immutability; FR-12 Asset Facts Immutability & Alter Seized Asset Data \\
\hline

MM-6 & Protect integrity of evidence documents (PDF hashing) & SR-16 Document Integrity Verification; FR-23 Document Hashing & Document Tampering \\
\hline

MM-7 & Enforce confidentiality via RBAC + case-based access & FR-3 RBAC; SR-18 Restricted Access; SR-19 Audit Privacy Boundary & Case Data Exfiltration \\
\hline

MM-8 & Ensure custody execution traceability and uniqueness & FR-27 Transaction Linking; SR-13 Execution Traceability & Replay Custody Action \\
\hline

MM-9 & Maintain service availability / resilience & NFR-1 Availability; Rate limiting & Denial of Service \\
\hline

\end{longtable}

This structured threat–mitigation relationship ensures that security controls are not added reactively, but are embedded as explicit design constraints within the system architecture.



\subsection{Custody Infrastructure}

The Custody Infrastructure represents the technical subsystem responsible for performing cryptographic custody operations and interacting with external blockchain networks. It encompasses components for secure key management, transaction construction, transaction signing, and transaction broadcasting.
The Custody Infrastructure operates as a trusted technical boundary within the overall system architecture. It enforces cryptographic controls independently from user-facing application logic and ensures that custody-related operations are executed only upon validated and approved instructions originating from the governance layer of the system.
The Custody Infrastructure:

\begin{itemize}
\item Operates autonomously based on approved and validated instructions
\item Does not represent a human actor
\item Does not expose private keys or sensitive cryptographic material to any user
\item Executes custody actions only after dual administrative approval has been verified
\item Logs all cryptographic and execution-related operations for audit and traceability purposes
\end{itemize}
The Custody Infrastructure is treated as a high-trust component within the architecture. However, its operations remain fully traceable through system-level logging and audit mechanisms to preserve accountability and evidentiary integrity.


\section{Functional Requirements}
\subsection{Identity, Accounts, Roles}

\subsubsection{FR-1 User Account Management}

The system shall allow administrators to create and manage user profiles for the following roles: Case Handler, Administrator, Auditor (and optionally System Manager if needed for maintenance).

\subsubsection{FR-2 Pseudonymous User IDs}


The system shall assign each user a pseudonymous UserID used in the UI and logs, where the UserID does not encode role or real identity.

\subsubsection{FR-3 Role-Based Access Control (RBAC)}


The system shall enforce RBAC so that users can perform only actions authorized by their role and by case assignment rules.

\subsubsection{FR-4 Identity Mapping Restriction}


The system shall restrict real-identity data (names/PII of case subjects and user real identities) so that Audit cannot view it. Administrators and assigned case handlers may access case-subject PII only for their authorized cases.

\subsection{Case Management and Visibility}


\subsubsection{FR-5 Case Creation and Persistence}

The system shall allow administrators to create cases identified by a unique, random, non-semantic CaseID. CaseIDs shall never be deleted.

\subsubsection{FR-6 Case Assignment}

Each case shall be assigned to exactly one case handler at a time. The system shall prevent access to detailed case data by non-assigned case handlers.

\subsubsection{FR-7 Case Index Visibility}

All authenticated users shall be able to view the list of CaseIDs, while access to case details is restricted according to role and assignment.

\subsubsection{FR-8 Case Reassignment via Ticket}

The system shall allow case reassignment only through an approved reassignment ticket.


\subsubsection{FR-9 Assignment History}

The system shall maintain an immutable history of all case assignments and reassignments, including timestamps, involved UserIDs, ticket reference, and admin approvals.

\subsection{Asset Registration and Valuation}


\subsubsection{FR-10 Asset Registration}

The system shall allow the registration of seized assets under a CaseID, including asset type (e.g., BTC, SOL), quantity, and relevant metadata.

\subsubsection{FR-11 Frozen Reference Valuation Snapshot}

The system shall store a frozen valuation snapshot expressed in a fixed reference currency (e.g., USDT) calculated at the moment of seizure/registration (with timestamp and valuation source). This snapshot shall be immutable.

\subsubsection{FR-12 Asset Facts Immutability}

The system shall prevent modification of the original seized asset facts (asset types and quantities) and the frozen reference valuation snapshot once recorded.

\subsubsection{FR-13 Administrative Metadata Updates via Ticket}

The system shall allow administrative updates/corrections only for permitted metadata fields (e.g., notes, documentation links, status fields), and only via approved tickets. No case handler can directly change stored case/asset records.

\subsection{Ticketing Workflow (the core)}

\subsubsection{FR-14 Ticket Creation}

The system shall allow a case handler to create a ticket linked to a CaseID, containing: request type, description, and supporting documentation.

\subsubsection{FR-15 Ticket Types}

The system shall support typed tickets at minimum:
\begin{itemize}
\item Transfer request (custody action)
\item Conversion request (custody action) (may be “out of system” in PoC)
\item Case reassignment request (governance action)
\item Metadata correction/update request (administrative action)
\end{itemize}

\subsubsection{FR-16 Ticket Lifecycle States}

Each ticket shall have a lifecycle state: Open, In Process, Closed.

\subsubsection{FR-17 Ticket Approval Rule (Two Admins)}

A ticket shall be executed only if both administrators approve it (parallel approval; order does not matter).

\subsubsection{FR-18 Ticket Rejection Rule}

If any administrator rejects a ticket, the ticket shall be Closed as Rejected, no system changes shall occur, and both administrators shall add notes explaining the rejection.

\subsubsection{FR-19 Ticket Re-submission}

After rejection, the case handler may open a new ticket addressing the rejection requirements; rejected tickets remain permanently recorded.

\subsubsection{FR-20 Ticket Cancellation by Case Handler}

The case handler shall be able to cancel a ticket only if it has not yet received both approvals and no execution/system changes have begun.

\subsubsection{FR-21 Admins Cannot Initiate Tickets}

Administrators shall not be able to create tickets. If an admin requires an action, the admin must request the case handler to open a ticket.


\subsection{Document Handling (PDF + integrity)}

\subsubsection{FR-22 PDF-Only Documentation}

All supporting documents attached to tickets shall be uploaded and stored as PDF files only.

\subsubsection{FR-23 Document Integrity Hashing}

Upon upload, the system shall compute and store a cryptographic hash (e.g., SHA-256) for each PDF and associate it with the CaseID/TicketID, uploader UserID, and timestamp.


\subsection{Reporting}

\subsubsection{FR-24 Audit Reporting (System-Wide)}

The Auditor shall be able to generate and download full activity reports for any period, any case, and any user, excluding protected PII and confidential case narrative details.

\subsubsection{FR-25 Case Reporting (Per Case)}

Administrators and the assigned case handler shall be able to generate and download per-case reports (PDF) reflecting the current case state for evidentiary or court usage.

\subsubsection{FR-26 Reports are Informational}

Generated reports shall be informational snapshots and shall not modify system state or constitute authorization for actions.



\subsection{Execution Traceability}

\subsubsection{FR-27 Transaction/Action Linking}

For custody actions (e.g., transfer), the system shall link the executed action to the originating ticket and record identifiers and status (e.g., transaction hash, timestamp).

\subsubsection{FR-28 Execution Failure Recording}

If an approved action cannot be executed (technical failure), the system shall record the failure reason, preserve traceability, and close the ticket with a final outcome indicating failure (no silent retries without logging).

\subsection{Audit Log (syslog-level)}

\subsubsection{FR-29 Comprehensive Event Logging}

The system shall record every meaningful action and security-relevant event (authentication events, ticket lifecycle changes, approvals/rejections, policy changes, report downloads, document uploads, assignment changes, execution attempts) in an audit log with actor UserID and timestamp.


\section{Security Requirements}

Although security requirements are often classified as non-functional requirements in traditional software engineering, in this work they are defined as a separate category due to their central role in addressing insider threats, custody integrity, and auditability within institutional cryptocurrency custody systems.

The following security requirements specify the controls necessary to ensure confidentiality, integrity, accountability, and traceability throughout the custody lifecycle. These requirements are derived from the threat landscape identified in Chapter 2 and are designed to mitigate risks related to privilege abuse, unauthorized asset manipulation, and tampering with audit evidence.

\subsection{Access Control and Privilege Management}

\subsubsection{SR-1 Least Privilege Enforcement}

The system shall enforce a least-privilege access control model ensuring that each role can perform only explicitly authorized actions.


\subsubsection{SR-2 Separation of Duties}

The system shall enforce strict separation of duties such that no single actor can both initiate and approve custody-impacting operations.

\subsubsection{SR-3 Privilege Escalation Prevention}

The system shall prevent unauthorized role modifications and privilege escalation attempts.

\subsubsection{SR-4 Controlled Role Assignment}

Role creation and modification shall be restricted to Administrators and shall be fully logged.

\subsection{Authentication and Session Security}

\subsubsection{SR-5 Strong Authentication for Privileged Roles}

Administrators shall use multi-factor authentication (MFA) when performing privileged operations.

\subsubsection{SR-6 Re-authentication for Sensitive Actions}

The system shall require explicit re-authentication before executing custody-impacting actions.

\subsubsection{SR-7 Session Traceability}

Authentication events and session activities shall be recorded and associated with the corresponding UserID.


\subsection{Audit Integrity and Non-Repudiation}

\subsubsection{SR-8 Comprehensive Logging}

The system shall record all security-relevant events, including authentication events, ticket lifecycle transitions, approvals, rejections, assignment changes, document uploads, report generation, and custody execution attempts.

\subsubsection{SR-9 Tamper-Evident Audit Logs}

Audit logs shall be implemented as append-only records and protected using integrity mechanisms (e.g., cryptographic hash chaining) to ensure that unauthorized modifications are detectable.

\subsubsection{SR-10 Log Deletion Prevention}

No actor shall be able to delete or alter existing audit records.

\subsubsection{SR-11 Non-Repudiation of Actions}

All actions shall be attributable to a specific authenticated UserID.

\subsection{Custody Integrity and Dual Control}

\subsubsection{SR-12 Dual Approval Enforcement}

Custody-impacting operations shall require independent approval from two Administrators. A single rejection shall prevent execution.

\subsubsection{SR-13 Execution Traceability}

Every executed custody operation shall be linked to its originating ticket and recorded with execution status and relevant identifiers.

\subsubsection{SR-14 Execution Failure Recording}

If an approved custody operation fails during execution, the system shall record the failure outcome and preserve full traceability.

\subsection{Data Integrity and Evidence Protection}

\subsubsection{SR-15 Asset Data Immutability}

Original seized asset records and frozen valuation snapshots shall be immutable.

\subsubsection{SR-16 Document Integrity Verification}

All uploaded PDF documents shall be integrity-protected using cryptographic hashing. Any integrity mismatch shall be logged as a security incident.

\subsubsection{SR-17 Case Identifier Persistence}

CaseIDs shall be immutable and shall never be deleted.

\subsection{Confidentiality and Privacy Protection}

\subsubsection{SR-18 Restricted Access to Sensitive Data}

Sensitive case data and PII shall only be accessible to authorized Administrators and the assigned Case Handler.

\subsubsection{SR-19 Audit Privacy Boundary}

The Auditor shall be restricted from accessing PII and confidential case content while retaining full visibility into operational and security events.

\subsubsection{SR-20 Pseudonymous Identity Representation}

System interfaces and audit records shall use pseudonymous UserIDs that do not encode role or real-world identity.

\section{Non-Functional Requirements}

The following non-functional requirements define the operational qualities and system-level constraints of the Secure Custody Framework for Cryptocurrency Assets (SCFCA). These requirements ensure that the system remains reliable, maintainable, and usable within an institutional environment while preserving evidentiary integrity.

\subsection{Availability and Reliability}

\subsubsection{NFR-1 System Availability}

The system shall be designed to provide high availability during institutional working hours, minimizing operational downtime.

\subsubsection{NFR-2 Contolled Downtime}

Maintenance operations shall be performed in a controlled manner and shall not compromise data integrity or audit records.

\subsubsection{NFR-3 Reliability of Custody Records}

The system shall ensure that case and asset records remain consistent and recoverable in the event of system interruption.

\subsection{Data Persistence and Retention}

\subsubsection{NFR-4 Long-Term Data Retention}

All case records, tickets, audit logs, and documentation shall be retained for the entire legal lifecycle of the case and shall not be automatically deleted.

\subsubsection{NFR-5 Backup and Recovery}

The system shall support secure backup and recovery mechanisms to prevent permanent loss of institutional data.

\subsection{ Performance and Scalability}

\subsubsection{NFR-6 Reasonable Response Time}

The system shall provide reasonable response times for standard operations such as case viewing, ticket creation, and report generation.

\subsubsection{NFR-7 Scalability Assumption}

The architecture shall be designed to support the management of multiple concurrent cases without degradation of core functionality.

(Note: As a proof-of-concept implementation, extreme-scale performance optimization is outside scope.)

\subsection{Usability and Operational Clarity}

\subsubsection{NFR-8 Role-Based Interface Clarity}

The user interface shall clearly reflect role-based permissions to minimize operational errors.

\subsubsection{NFR-9 Workflow Transparency}

Ticket status transitions and approval states shall be clearly visible to authorized users.


\subsection{Audit and Traceability Quality}

\subsubsection{NFR-10 Report Generation Capability}

The system shall support generation of structured reports suitable for institutional and judicial use.

\subsubsection{NFR-11 Log Retention Integrity}

Audit records shall remain accessible and interpretable over time, ensuring evidentiary usability.

\subsection{Maintainability and Extensibility}

\subsubsection{NFR-12 Modular Architecture}

The system architecture shall be modular to allow future integration with external custody infrastructures or regulatory systems.

\subsubsection{NFR-13 Configurability of Reference Currency}

The system shall allow configuration of the fixed reference currency used for valuation snapshots.

The SCFCA architecture separates governance logic from
custody infrastructure, enforcing dual approval and RBAC.

% =====================================================
\chapter{Implementation and Proof of Concept (PoC)}
A proof-of-concept validates RBAC enforcement,
dual approval workflow, and audit logging integrity.

\section{Development Environment and Tooling}
Describe why you chose Python, specific libraries (like cryptography or hashlib), and your local setup.
\section{Architecture of the Prototype}
\subsection{Initial Repository Structure Proposal}

The initial repository structure proposed for the \textbf{SCFCA} project, following a Python-first approach, is shown below.

\begin{verbatim}
scfca-repo/
|
|-- backend/                # FastAPI backend (Python)
|   |-- auth/
|   |-- users/
|   |-- roles/
|   |-- cases/
|   |-- tickets/
|   |-- assets/
|   |-- custody/
|   |-- audit/
|   |-- documents/
|   |-- common/
|   |-- config/
|   |-- middleware/
|   |-- validators/
|   |-- models/
|   |-- services/
|   |-- repositories/
|   `-- tests/
|
|-- frontend/               # Python-friendly UI (e.g., Streamlit, minimal React if needed)
|   |-- pages/
|   |-- components/
|   |-- layouts/
|   |-- services/
|   |-- hooks/
|   |-- utils/
|   |-- styles/
|   |-- auth/
|   |-- cases/
|   |-- tickets/
|   |-- assets/
|   |-- audit/
|   |-- documents/
|   `-- tests/
|
|-- docs/                   # Documentation (Markdown, PlantUML)
|   |-- architecture/
|   |-- threat-model/
|   |-- api/
|   |-- diagrams/
|   |-- thesis-notes/
|   `-- adrs/
|
|-- infra/                  # Infrastructure, DevSecOps, deployment
|   |-- docker/
|   |-- env-examples/
|   |-- ci-cd/
|   |-- security/
|   `-- deployment/
|
|-- scripts/                # Python automation scripts
|
|-- tests/                  # End-to-end/integration tests
|
|-- diagrams/               # Architecture/process diagrams (PlantUML)
|
|-- .github/                # Copilot and workflow instructions
|
`-- README.md               # Project overview
\end{verbatim}

\subsubsection{Folder Description}

\begin{itemize}
    \item \textbf{backend/}: Python FastAPI backend, organized by domain such as authentication, users, cases, tickets, custody, audit, and documents. It also includes shared layers for models, services, repositories, middleware, validation, and testing.
    \item \textbf{frontend/}: Python-friendly user interface layer, intended primarily for Streamlit-based prototyping, with the possibility of using a minimal React frontend only if strictly necessary.
    \item \textbf{docs/}: Documentation folder containing architecture notes, threat models, API notes, diagrams, thesis-related notes, and architecture decision records.
    \item \textbf{infra/}: Infrastructure and DevSecOps-related material, including Docker, CI/CD, deployment, environment examples, and security-related configuration.
    \item \textbf{scripts/}: Python scripts for automation, setup, maintenance, or auxiliary project tasks.
    \item \textbf{tests/}: End-to-end and integration tests, kept separate from backend and frontend local tests.
    \item \textbf{diagrams/}: PlantUML or Markdown-based diagrams for architecture, process flows, and other technical visualizations.
    \item \textbf{.github/}: GitHub-related configuration, including Copilot instructions and workflow files.
    \item \textbf{README.md}: Main project entry point describing the repository, its purpose, structure, and setup instructions.
\end{itemize}

\subsubsection{Next Implementation Steps}

\begin{itemize}
    \item Scaffold the FastAPI backend application.
    \item Define the main Pydantic models and database entities.
    \item Set up the PostgreSQL connection and ORM layer.
    \item Implement authentication and authorization with RBAC.
    \item Start the frontend with Streamlit for rapid prototyping.
    \item Add Dockerfiles and a local \texttt{docker-compose} setup.
    \item Introduce security mechanisms such as dual approval and tamper-evident audit logging from the beginning.
    \item Establish a testing strategy using \texttt{pytest} for backend and integration testing.
\end{itemize}

\subsubsection{Login and RBAC Flow}

The proof of concept implements a simple session-based authentication and role-based access control mechanism suitable for demonstration purposes.

\begin{itemize}
    \item \textbf{Login}: The backend validates the submitted username and password against the database using hashed password verification. If authentication succeeds, the system stores the authenticated username in a session cookie (for example, \texttt{scfca\_user}).
    
    \item \textbf{Current User Resolution}: The \texttt{get\_current\_user} dependency reads the username from the session cookie, retrieves the corresponding user from the database, and returns the authenticated user object.
    
    \item \textbf{Role-Based Access Control}: The \texttt{require\_role} and \texttt{require\_any\_role} dependencies are applied to protected routes to restrict access according to user role. For example, administrative actions such as ticket approval can be limited to users with the administrator role. If a user lacks the required role, the system returns an HTTP 403 Forbidden response.
\end{itemize}

This approach is intentionally lightweight and is designed for a thesis proof of concept rather than a production deployment. Nevertheless, it is sufficient to demonstrate authentication, user resolution, and least-privilege access control within the SCFCA prototype.

\subsubsection{Case Management Module Structure}

The case management module follows a layered structure composed of repository, service, and route layers.

\begin{itemize}
    \item \textbf{Repository Layer}: Responsible for direct database access and CRUD operations related to cases.
    
    \item \textbf{Service Layer}: Implements the business logic of the module, including case creation, case assignment, and integration with audit logging for relevant actions.
    
    \item \textbf{Routes Layer}: Exposes the API endpoints, applies role-based access control through dependencies, and delegates processing to the service layer.
\end{itemize}

RBAC is enforced at the route level using authorization dependencies, while important operations such as case creation and handler assignment are recorded through the audit module. This structure keeps the implementation modular, maintainable, and appropriate for a proof-of-concept developed in an academic context.

\subsubsection{Asset Registry Module Structure}

The asset registry module follows a layered architecture composed of repository, service, and route layers.

\begin{itemize}
    \item \textbf{Repository Layer}: Responsible for direct database access and CRUD operations related to registered crypto-assets.
    
    \item \textbf{Service Layer}: Implements the business logic of the module, including asset registration, asset-to-case linking, status updates, and integration with audit logging for relevant actions.
    
    \item \textbf{Routes Layer}: Exposes the API endpoints, applies role-based access control through dependencies, and delegates processing to the service layer.
\end{itemize}

Audit logging is performed for important asset-related actions, particularly asset registration and asset status updates. This structure keeps the module modular, maintainable, and appropriate for a proof-of-concept developed in an academic context.

\subsubsection{Ticket and Approval Workflow Structure}

The ticket and approval workflow module is implemented through three main files:

\begin{itemize}
    \item \texttt{backend/tickets/repository.py}
    \item \texttt{backend/tickets/service.py}
    \item \texttt{backend/tickets/routes.py}
\end{itemize}

\paragraph{Approval Logic}
The workflow is designed to enforce separation of duties and controlled authorization for sensitive actions.

\begin{itemize}
    \item \textbf{Dual Approval}: Sensitive ticket types require approval from two distinct administrators. The user who created the ticket cannot serve as the sole approving authority.
    
    \item \textbf{No Repeated Action}: An administrator cannot approve or reject the same ticket more than once.
    
    \item \textbf{Audit Logging}: Ticket creation, approval, and rejection events are recorded in the audit trail to preserve traceability and accountability.
    
    \item \textbf{Status Update}: A ticket remains in the \texttt{pending} state until two distinct administrator approvals are registered. If a rejection occurs, the ticket is immediately marked as \texttt{rejected}. Only after the required approvals are completed is the ticket marked as \texttt{approved}.
\end{itemize}

This structure keeps the implementation modular, understandable, and suitable for demonstrating governance controls in the SCFCA proof of concept.

\subsubsection{Audit Logging Module}

The audit module provides a simple and reusable mechanism for recording security-relevant events across the SCFCA proof of concept.

\paragraph{Core Functionality}
A central \texttt{log\_audit} function is used by other modules to register audit events in a consistent manner. Each event stores:

\begin{itemize}
    \item the acting user or system actor,
    \item the action performed,
    \item the timestamp,
    \item the related entity type,
    \item the related entity identifier,
    \item and additional details describing the event.
\end{itemize}

\paragraph{Tamper-Evident Integrity}
To strengthen the demonstrative value of the proof of concept, each audit entry includes a simple hash-chain mechanism. In this approach, every new event stores a hash derived from its own content together with the hash of the previous event. This creates a sequential integrity relationship between audit records and provides a lightweight tamper-evident property suitable for a thesis prototype.

\paragraph{Audit Retrieval}
The module also provides a \texttt{list\_audit\_events} function, which allows retrieval of recent audit events for dashboard visualization, traceability review, or audit inspection.

\paragraph{Integration Across the Prototype}
Other modules in the system, including authentication, case management, asset registry, ticket workflow, and document integrity, invoke \texttt{log\_audit(...)} after significant actions. Typical examples include user login, case creation, asset registration, ticket approval or rejection, and document registration.

This design ensures that relevant operations are consistently recorded, thereby supporting traceability, accountability, and auditability requirements within the SCFCA proof of concept.

\subsubsection{Document Integrity Module}

The document integrity module is implemented through three main files:

\begin{itemize}
    \item \texttt{backend/documents/repository.py}
    \item \texttt{backend/documents/service.py}
    \item \texttt{backend/documents/routes.py}
\end{itemize}

\paragraph{Integrity Workflow}
The module is designed to demonstrate document registration, integrity preservation, and verification within the SCFCA proof of concept.

\begin{itemize}
    \item \textbf{Registration}: A user uploads a document associated with a case. The backend computes the SHA-256 hash of the uploaded file and stores the filename, computed hash, upload date, and case reference. An audit event is generated for traceability.
    
    \item \textbf{Listing}: Registered documents can be listed globally or filtered according to the associated case.
    
    \item \textbf{Verification}: To verify integrity, a user uploads a file for comparison. The backend computes its SHA-256 hash and compares it against the stored hash value. The result of the verification, whether matching or not, is returned by the system and recorded in the audit trail.
    
    \item \textbf{Audit Logging}: Both registration and verification events are logged to support accountability and traceability.
\end{itemize}

This design is intentionally lightweight, modular, and suitable for demonstrating document integrity and auditability requirements within the thesis proof of concept.

\subsubsection{Dashboard Module}

The dashboard module is implemented through two main files:

\begin{itemize}
    \item \texttt{backend/dashboard/routes.py}
    \item \texttt{backend/dashboard/service.py}
\end{itemize}

\paragraph{Dashboard Endpoints}
The module provides lightweight summary endpoints intended to support the Streamlit dashboard of the SCFCA proof of concept.

\begin{itemize}
    \item \textbf{\texttt{/dashboard/summary}}: Returns a JSON summary containing the main high-level indicators of the system:
    \begin{itemize}
        \item \texttt{total\_cases}: total number of cases registered in the system,
        \item \texttt{total\_assets}: total number of registered crypto-assets,
        \item \texttt{pending\_tickets}: number of tickets currently in the \texttt{pending} state,
        \item \texttt{approved\_tickets}: number of tickets currently in the \texttt{approved} state.
    \end{itemize}
    These queries are intentionally simple, SQLite-compatible, and suitable for fast retrieval in a demonstration environment.
    
    \item \textbf{\texttt{/dashboard/audit-events}}: Returns a list of the most recent audit events, with a default limit of ten records. This endpoint is intended to support dashboard visualization and basic compliance or traceability review.
\end{itemize}

Both endpoints are modular and easy to connect to the frontend layer. They may also be extended later to restrict data visibility according to user role when finer-grained dashboard access control is required.

\subsubsection{Frontend Module}

The frontend layer of the SCFCA proof of concept is implemented through the following files:

\begin{itemize}
    \item \texttt{frontend/app.py}
    \item \texttt{frontend/services.py}
    \item \texttt{frontend/pages/login.py}
    \item \texttt{frontend/pages/dashboard.py}
    \item \texttt{frontend/pages/cases.py}
    \item \texttt{frontend/pages/assets.py}
    \item \texttt{frontend/pages/tickets.py}
    \item \texttt{frontend/pages/audit.py}
    \item \texttt{frontend/pages/documents.py}
\end{itemize}

\paragraph{Execution}
To run the proof of concept locally, the backend and frontend must be started separately.

\begin{itemize}
    \item Start the backend:
    \begin{verbatim}
uvicorn backend.main:app --reload
    \end{verbatim}

    \item Start the frontend:
    \begin{verbatim}
streamlit run frontend/app.py
    \end{verbatim}
\end{itemize}

Once both components are running, the user interface can be accessed through the Streamlit address, typically \texttt{http://localhost:8501}.

\paragraph{Frontend Design}
The Streamlit application provides a lightweight and role-aware user interface for demonstrating the core workflows of the SCFCA proof of concept. Each page interacts with the FastAPI backend through a dedicated service layer, which keeps frontend logic separated from backend communication.

The interface includes pages for authentication, dashboard visualization, case management, asset registry operations, ticket workflow handling, audit review, and document integrity operations. Navigation options and available actions are adapted according to the authenticated user role, ensuring consistency with the RBAC design of the platform.

This frontend structure is intentionally simple, functional, and suitable for demonstrating the main thesis concepts in a clear and academically defensible way.

\subsubsection{Demonstration Preparation}

The SCFCA proof of concept was prepared for demonstration by refining the repository documentation and adding a basic test suite for key workflows.

\paragraph{Updates Introduced}
The following elements were updated:

\begin{itemize}
    \item The main \texttt{README} file was expanded to include clear setup and execution steps.
    \item A concise demonstration walkthrough was added for the three main roles of the platform.
    \item A basic test suite was included in \texttt{test\_workflows.py} to validate selected workflows such as login, RBAC, dashboard access, audit retrieval, and ticket approval.
\end{itemize}

\paragraph{Execution Procedure}
To run the proof of concept locally, the following steps are performed:

\begin{itemize}
    \item Clone the repository and ensure Python 3.10 or later is installed.
    \item Install backend dependencies:
\begin{verbatim}
cd backend && pip install -r requirements.txt
\end{verbatim}

    \item Seed the demonstration data:
\begin{verbatim}
cd ../scripts && python seed_demo_data.py
\end{verbatim}

    \item Start the backend:
\begin{verbatim}
cd ../backend && uvicorn main:app --reload
\end{verbatim}

    \item Optionally run the tests:
\begin{verbatim}
cd ../tests && pytest
\end{verbatim}

    \item If the frontend is included, start the Streamlit interface:
\begin{verbatim}
cd ../frontend && streamlit run app.py
\end{verbatim}
\end{itemize}

\paragraph{Demonstration Users}
The following demonstration users are included in the seeded dataset:

\begin{itemize}
    \item \textbf{Case Handler}: \texttt{alice / alice123}
    \item \textbf{Administrator}: \texttt{bob / bob123} or \texttt{eve / eve123}
    \item \textbf{Auditor}: \texttt{carol / carol123}
\end{itemize}

All credentials are intended exclusively for demonstration purposes.

\paragraph{Demonstration Readiness}
At this stage, the proof of concept includes the minimum documentation, test coverage, and execution guidance required for a thesis demonstration. The material remains intentionally concise, clear, and aligned with the academic scope of the SCFCA project.


\section{Implementation of Core Security Logic}

Focus on how you coded the Dual Approval workflow and the RBAC (Role-Based Access Control).
\section{Cryptographic Key Management Simulation}

Since you aren't using a physical HSM yet, describe how your code "simulates" secure key storage.
\section{Audit Log Generation}
Explain the implementation of the immutable log that records every action for the judicial "chain of custody.


% =====================================================
\chapter{Evaluation and Testing}

\section{Testing Environment and Methodology}
This work applies a security-by-design testing strategy in which each environment (Dev, Test/CI, Staging, and Production) has a distinct purpose, dataset policy, and set of controls. The objective is to validate both the functional correctness and the security posture of the SCFCA service while minimizing the exposure of sensitive information and preventing configuration drift.

\subsection{Tooling}
The testing and validation activities combine automated and manual techniques:

\begin{itemize}
    \item \textbf{Unit and integration testing:} PyTest for backend unit tests and integration tests.
    \item \textbf{API testing and smoke checks:} automated HTTP checks (e.g., health endpoints) executed in CI/CD after deployment.
    \item \textbf{Container and dependency scanning:} image and dependency vulnerability scanners (e.g., Trivy, Clair, Snyk) integrated into CI/CD gates.
    \item \textbf{Infrastructure-as-Code (IaC) validation:} static analysis of IaC definitions (e.g., Checkov, tfsec, KICS) and policy-as-code validation (e.g., OPA, Sentinel) to enforce configuration baselines.
    \item \textbf{Security testing in staging:} API fuzzing and penetration testing activities executed against a production-equivalent staging deployment.
    \item \textbf{Logging and monitoring:} centralized log collection and correlation (SIEM-style analysis) to detect abnormal patterns and support incident response.
\end{itemize}

\subsection{Data Minimization and Dataset Policy}
A strict data minimization policy is enforced across environments:

\begin{itemize}
    \item \textbf{No production data outside production.} Real case data and any sensitive custody-related information are restricted to the Production environment.
    \item \textbf{Synthetic and seeded datasets.} Development and Test/CI environments rely on automatically generated synthetic data (seed data) to validate functionality without exposing sensitive information.
    \item \textbf{Access control to non-production data.} Staging datasets are non-production and access is restricted to internal teams for validation and acceptance testing.
\end{itemize}

\subsection{Environment Security Configuration}
\subsubsection{Development (Dev)}
\textbf{Objective:} fast iteration with containment.
\begin{itemize}
    \item \textbf{Isolation:} local containerized execution (e.g., Docker) to avoid contaminating the host OS.
    \item \textbf{Secrets management:} credentials are never hardcoded; local \texttt{.env} files are used and excluded from version control.
\end{itemize}

\subsubsection{Testing / CI}
\textbf{Objective:} repeatability and prevention of configuration drift.
\begin{itemize}
    \item \textbf{Ephemeral infrastructure:} short-lived environments created per pull request and destroyed after execution.
    \item \textbf{Synthetic data and fuzzing:} seeded datasets and input fuzzing to exercise error handling and resilience.
\end{itemize}

\subsubsection{Staging}
\textbf{Objective:} production-equivalent validation.
\begin{itemize}
    \item \textbf{Equivalence:} same OS versions, libraries, runtime, and external services as Production to detect dependency and configuration issues.
    \item \textbf{Restricted access:} limited to internal users, preferably gated by VPN or a bastion host.
\end{itemize}

\subsubsection{Production (Prod)}
\textbf{Objective:} secure operation under real threat conditions.
\begin{itemize}
    \item \textbf{Zero-trust segmentation:} strict network controls; outbound connectivity is denied unless explicitly required.
    \item \textbf{Immutability:} production instances are replaced via new signed images rather than patched in-place whenever feasible (immutable infrastructure model).
\end{itemize}

\subsection{Controls Across the Deployment Lifecycle}
To structure the validation strategy, controls are grouped into preventive, detective, and corrective categories.

\subsubsection{Preventive Controls}
\begin{itemize}
    \item \textbf{Image hardening:} use of hardened and patched base images aligned with recognized benchmarks (e.g., CIS Benchmarks).
    \item \textbf{RBAC:} least-privilege access for service accounts and human operators.
    \item \textbf{Artifact signing:} cryptographic signing of build artifacts and container images to ensure origin and integrity (e.g., cosign, Notary).
    \item \textbf{WAF:} perimeter filtering for common injection attacks before they reach the application layer.
\end{itemize}

\subsubsection{Detective Controls}
\begin{itemize}
    \item \textbf{Container vulnerability analysis:} scanning images for known vulnerabilities (e.g., Trivy, Clair, Snyk).
    \item \textbf{File Integrity Monitoring (FIM):} detection of unauthorized modifications to binaries and critical files (e.g., osquery, Samhain).
    \item \textbf{Centralized logging and correlation:} SIEM-style analysis to identify suspicious behavior such as credential stuffing or anomalous access patterns.
\end{itemize}

\subsubsection{Corrective Controls}
\begin{itemize}
    \item \textbf{Incident Response Plan:} documented procedures for compromised deployments or security incidents.
    \item \textbf{Automatic rollback:} capability to revert rapidly to a previously verified secure release.
    \item \textbf{Live patching (when applicable):} mitigation of critical OS/kernel vulnerabilities with minimal operational disruption.
\end{itemize}

\subsection{Test Types and Where They Run}
\subsubsection{Smoke Tests}
\textbf{Purpose:} detect catastrophic failures immediately after deployment. Failures trigger rollback mechanisms and incident procedures as needed. These tests provide an availability baseline and early detection of operational regressions.

\subsubsection{User Acceptance Testing (UAT)}
\textbf{Purpose:} validate that the system meets business requirements and the intended custody workflow in Staging. UAT also provides a practical integrity check of business logic, which can reveal authorization or workflow defects.

\subsubsection{Performance Tests and Benchmarks}
\textbf{Purpose:} validate capacity, stability, and latency under expected and adverse loads (load, stress, spike, and soak tests). Performance testing supports availability assurance and informs alert thresholds, scaling policies, and denial-of-service resilience.

\subsubsection{Infrastructure-as-Code (IaC) Tests}
\textbf{Purpose:} ensure that the target infrastructure is secure before deployment. Static IaC analysis detects insecure configurations (e.g., public storage, missing encryption), while policy-as-code enforces organizational requirements such as encryption-at-rest and restricted network exposure.

\subsubsection{Integration and Contract Tests}
\textbf{Purpose:} ensure that service interactions follow an agreed contract and remain compatible across versions. Contract tests prevent breaking changes in API schemas, and API fuzzing exercises resilience against malformed inputs and unexpected payloads.

\subsubsection{Advanced Security Testing in Staging}
\textbf{Purpose:} execute intrusive security validation without impacting real users. Penetration testing and security scanning are performed in a production-equivalent Staging environment to ensure results remain representative of Production.

\subsubsection{Controlled Production Testing}
\begin{itemize}
    \item \textbf{Canary deployments:} gradual rollout to a small fraction of users with intensive monitoring before full promotion.
    \item \textbf{Runtime protection (RASP):} behavioral detection and blocking of attacks during execution when supported by the runtime.
    \item \textbf{Chaos engineering:} controlled fault injection to verify resilience, alerting, and recovery mechanisms under partial failures.
\end{itemize}

\section{Monitoring for Security in Evolving Systems (DevSecOps)}
Security in SCFCA is not a one-time design decision; it is an operational property that must be continuously measured as the system evolves through code changes, dependency updates, and configuration drift. In a DevSecOps model, monitoring is the feedback loop that confirms whether preventive controls remain effective and whether emerging threats are detected early enough to respond.

This section defines the security monitoring strategy for SCFCA, focusing on (i) what must be observed, (ii) how signals are collected and correlated, and (iii) how detections trigger response actions and drive improvements in the pipeline.

\subsection{Monitoring Objectives}
The monitoring program is designed to achieve the following objectives:

\begin{itemize}
    \item \textbf{O1 -- Detect compromise attempts early:} identify suspicious authentication patterns, privilege abuse, and anomalous API usage before asset-impact occurs.
    \item \textbf{O2 -- Preserve integrity of custody operations:} detect unauthorized changes to critical components (configurations, binaries, containers) and ensure audit logs remain complete and tamper-evident.
    \item \textbf{O3 -- Support incident response and forensics:} provide sufficient, time-synchronized evidence to reconstruct events, attribute actions to identities, and validate chain-of-custody procedures.
    \item \textbf{O4 -- Maintain availability under attack or failure:} detect degradation, DoS conditions, and capacity saturation to trigger automated mitigation (rate limiting, scaling, rollback).
\end{itemize}

\subsection{Security Telemetry: What SCFCA Must Observe}
SCFCA monitoring is organized into telemetry domains:

\subsubsection{Application and API Telemetry}
\begin{itemize}
    \item Authentication events (success/failure, MFA outcomes, token refresh, session anomalies).
    \item Authorization decisions (role checks, denied actions, escalation attempts).
    \item High-risk custody actions (wallet creation, key access, transaction proposal/approval/execution).
    \item Input validation failures and unexpected payload patterns (signals for fuzzing-like behavior).
\end{itemize}

\subsubsection{Infrastructure and Container Telemetry}
\begin{itemize}
    \item Container lifecycle events (image used, start/stop/restart, crash loops).
    \item Runtime security signals (unexpected outbound connections, privilege changes, suspicious process execution).
    \item Network policy violations (blocked egress/ingress attempts; segmentation violations).
\end{itemize}

\subsubsection{Integrity and Configuration Telemetry}
\begin{itemize}
    \item File Integrity Monitoring (FIM) for critical binaries and configuration files.
    \item Drift detection for security-sensitive configuration (RBAC policies, firewall rules, secrets configuration).
    \item Artifact provenance verification (signed images, verified build source).
\end{itemize}

\subsubsection{Audit and Chain-of-Custody Telemetry}
Because SCFCA manages confiscated assets, auditability is a first-class security property:
\begin{itemize}
    \item Immutable audit logs for all custody actions with actor identity, timestamp, action type, and outcome.
    \item Correlation identifiers across services to reconstruct workflows end-to-end.
    \item Alerts for missing logs, log pipeline failures, or suspicious gaps.
\end{itemize}

\subsection{Collection, Centralization, and Correlation}
Telemetry is only useful if it is consolidated and searchable. SCFCA adopts centralized logging and metric collection to enable correlation across layers:

\begin{itemize}
    \item \textbf{Centralized logs:} application logs, API gateway/WAF logs, and infrastructure logs are shipped to a common platform (SIEM-like) for correlation.
    \item \textbf{Metrics and health signals:} latency, error rates, saturation, and resource usage are collected to detect degradation and potential DoS conditions.
    \item \textbf{Alerting rules:} detections are expressed as rules over aggregated signals (e.g., repeated failed logins from diverse IPs, privilege denials followed by admin token usage, abnormal transaction approval frequency).
\end{itemize}

\subsection{Detection Use Cases}
Representative detection use cases for SCFCA include:

\begin{itemize}
    \item \textbf{Credential abuse:} brute-force patterns, password spraying, impossible travel, anomalous device/session behavior.
    \item \textbf{Privilege escalation attempts:} repeated authorization denials on privileged endpoints followed by successful access.
    \item \textbf{Suspicious custody activity:} unusual transaction proposal volume, approvals outside normal business hours, abnormal approval chains.
    \item \textbf{Integrity violations:} changes to approved images, unexpected container runtime behavior, modification of critical files.
    \item \textbf{Data exposure indicators:} spikes in export endpoints, excessive read operations, unexpected large responses, or error messages leaking internals.
\end{itemize}

\subsection{Response and Continuous Improvement Loop}
Monitoring must drive action. SCFCA aligns detections with response playbooks and pipeline feedback:

\begin{itemize}
    \item \textbf{Immediate actions:} revoke tokens, disable accounts, block IPs via WAF rules, isolate workloads, or trigger automated rollback.
    \item \textbf{Incident response workflow:} triage, containment, eradication, recovery, and post-incident review with evidence preservation.
    \item \textbf{DevSecOps feedback:} validated incidents and near-misses become new pipeline checks (tests, policies, hardening) to prevent recurrence.
\end{itemize}

\subsection{Privacy and Data Minimization in Monitoring}
Monitoring is constrained by data minimization principles:
\begin{itemize}
    \item Logs must avoid storing sensitive custody data (private keys, seed phrases, raw secrets).
    \item Security events should record \textit{what happened} and \textit{who did it} without exposing protected content.
    \item Access to monitoring platforms must be restricted and auditable (least privilege, strong authentication, segregation of duties).
\end{itemize}

\subsection{Motivation: From Static Verification to Runtime Assurance}
In security engineering, static verification (design reviews, threat modeling, code analysis) is necessary but insufficient. Real systems evolve: dependencies change, configurations drift, and operational contexts introduce new assumptions. As a result, security claims require \emph{runtime evidence}. Monitoring provides that evidence and closes the DevSecOps feedback loop by turning production behavior into actionable security improvements.

Monitoring is therefore treated as a mechanism of trust and continuous improvement: it complements preventive controls by detecting deviations, supporting compliance, and enabling timely response when assumptions no longer hold.

\subsection{The Role of Monitoring}
Monitoring complements security mechanisms across the stack (hardware, operating system, platform/middleware, and application). Its purpose is to validate that the system behaves according to an expected execution model and to detect when reality diverges from that model.

Two design tensions must be addressed:
\begin{itemize}
    \item \textbf{Assumption management:} monitoring validates assumptions such as isolation between workloads, correct enforcement of access control, and integrity of execution environments.
    \item \textbf{Balance of power vs. cost:} stronger monitoring can increase detection capability but may introduce overhead and privacy risks. The selected monitoring strategy must be effective without becoming harmful or impractical.
\end{itemize}

Beyond intrusion detection, monitoring supports compliance checking (e.g., generation of required records for each custody phase), performance and availability validation, and guidance for secure evolution based on observed data.

\subsection{Basic Concepts}
Monitoring is expressed in terms of observable facts, persistent conditions, and expected behavior:

\begin{itemize}
    \item \textbf{Event:} an observable fact relevant to security (e.g., failed login, approval action, container restart).
    \item \textbf{Fluent:} a persistent condition evaluated over time (e.g., ``account is locked'', ``service is in degraded mode'').
    \item \textbf{Rule/Policy:} a specification of expected behavior linking events and fluents over time.
    \item \textbf{Violation:} a detected deviation from the expected model.
\end{itemize}

Traditional monitoring compares actual behavior against an expected model defined through rules or policies. In distributed systems, this approach also helps reveal unexpected interactions and defects in the model itself.

\subsection{Rule-Based Monitoring}
Rules typically describe normal operation; when observations do not satisfy a rule, a violation is raised. Rules can be expressed using temporal and event-based formalisms (e.g., temporal logic or event calculus). Probabilistic methods (e.g., Bayesian inference) may complement rule-based detection when evidence is uncertain.

A generic rule structure can be expressed as:
\[
B_{t_1} \Rightarrow H_{t_2}
\]
where $B_{t_1}$ (body) is a conjunction of conditions (events, system state, time constraints) and $H_{t_2}$ (head) is the expected consequence.

Typical predicates include:
\begin{itemize}
    \item $Observed(e,t)$: event $e$ is observed at time $t$
    \item $HoldsAt(f,t)$: fluent $f$ holds at time $t$
    \item relational and temporal constraints (e.g., $t_2 > t_1$, equality/inequality relations)
\end{itemize}

\textbf{Example.} If an access control component sends a credential request to an authorization component, it must receive a response within 3 seconds:
\[
Observed(ReqCred,t_1) \Rightarrow Observed(RespCred,t_2) \wedge (t_2>t_1) \wedge (t_2 < t_1+3)
\]

\subsection{Monitoring Options and Trust Domains}
Monitoring can differ based on where events are produced and where monitoring is executed:
\begin{itemize}
    \item \textbf{Internal vs. external event generation:} events may be generated by the application itself (instrumentation) or derived externally (network/host telemetry).
    \item \textbf{Internal vs. external monitoring:} internal monitors operate within the same trust domain as the application, while external monitors run in a separate trust domain (useful when the application is not fully trusted).
    \item \textbf{Observe vs. act:} monitoring may be purely observational or may trigger reactions (containment, restart, throttling, permission changes). Detection can be reactive or include predictive elements based on trends.
\end{itemize}

\subsection{Instrumented vs. Non-Instrumented vs. Self-Monitoring Applications}
Three broad monitoring approaches exist:

\subsubsection{Self-Monitoring Applications (RASP-like)}
Applications implement their own checks during execution.
\textbf{Advantages:} transparent to the platform and less likely to require platform modification.
\textbf{Disadvantages:} increased development effort, limited adaptability at runtime, and inability to observe certain cross-service interactions; response capabilities may also be constrained.

\subsubsection{Non-Instrumented Applications}
Monitoring relies on generic signals (network, host, platform telemetry) without application-specific event generation.
\textbf{Advantages:} applicable to legacy systems and more adaptable to environmental change.
\textbf{Disadvantages:} lower precision, higher false positives/negatives, and potential accountability issues.

\subsubsection{Instrumented Applications}
Applications include monitoring-specific event generation and rules tailored to the application.
\textbf{Advantages:} better precision and fault/attack tolerance; rules can be aligned to business-critical workflows.
\textbf{Disadvantages:} higher cost and limited adaptability; ensuring event genuineness becomes critical.

In distributed environments, instrumentation may be necessary to observe internal state transitions and to disambiguate behavior across multiple instances.

\subsection{From Proof-Carrying Code to Monitoring-Capable Code}
Static verification techniques such as Proof-Carrying Code (PCC) validate a limited set of properties before execution (e.g., bytecode safety). Monitoring-Capable Code (MCC) complements this by enabling dynamic verification during execution through behavior models and runtime rules, providing control to the platform and stronger assurance under evolution.

\subsection{Multi-Level Monitoring Architecture}
For scalable monitoring in distributed systems, responsibilities can be separated across monitoring layers:

\begin{itemize}
    \item \textbf{Local Application Surveillance (LAS):} detects implementation anomalies using an application behavior security model.
    \item \textbf{Intra-Platform Surveillance (IPS) (horizontal monitoring):} detects unexpected interactions between applications and enforces monitoring forwarding controls.
    \item \textbf{Global/Vertical Surveillance (GAS):} detects design-level inconsistencies through generalized behavior models.
\end{itemize}

This separation improves scalability and clarifies accountability: implementation anomalies, interaction anomalies, and model/design anomalies are handled at the appropriate layer.

\subsection{Monitoring in the DevSecOps Cycle}
DevSecOps requires continuous feedback from production to guide secure evolution. Monitoring provides:
\begin{itemize}
    \item early detection of deviations and operational regressions,
    \item evidence-driven updates to the threat model,
    \item support for compliance and auditing through verifiable runtime records,
    \item the basis for automated reactions (containment, rollback, throttling) when required.
\end{itemize}

\subsection{Conclusion}
Monitoring provides continuous assurance in distributed and evolving systems. It connects design-time security controls with runtime evidence, enabling true DevSecOps operation. For systems such as SCFCA, where integrity, auditability, and controlled access are fundamental, designing for monitorability is a required security property rather than an optional feature.

\section{Functional Validation}
(Does the Registry work? Does Dual Approval actually require two people?).
\section{Security Evaluation (Misuse Case Analysis)}
This is crucial! You prove that the "Thief Admin" or "Unauthorized Access" scenarios you identified in Chapter 3 are blocked by your framework).
\section{Analysis of Results}
(A summary of what went well and any edge cases you found).

Test scenarios confirm that:
\begin{enumerate}
    \item Custody execution fails without two approvals.
    \item Unauthorized asset modifications are denied.
    \item All actions are traceable to pseudonymous UserIDs.
\end{enumerate}

% =====================================================
\chapter{Conclusions and Future Work}
\section{Achievement of Objectives}
Go back to your "Specific Objectives" from Chapter 1 and explain how you met each one.
\section{Limitations of the Prototype}
Be honest—mention that the current PoC is a simulation and doesn't handle live blockchain transactions yet.
\section{Future Lines of Research}
* Integration with physical HSMs.

Expansion to MPC (Multi-Party Computation) for decentralized signing.

Adaptation to specific legal requirements in different jurisdictions (beyond Albania).



The SCFCA demonstrates that governance-driven security architecture
can mitigate insider threats and preserve custody integrity.

Future work includes full HSM integration and blockchain
network interaction testing.



% =====================================================
\printbibliography

\end{document}
