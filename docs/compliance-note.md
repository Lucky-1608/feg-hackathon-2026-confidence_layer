# D4 Compliance Analysis

## Regulatory Frameworks Addressed
Confidence Layer is built with compliance as a structural property, ensuring alignment with the following standards:
1.  **EU Regulations & GDPR:** All session telemetry and decisioning is strictly bound to the authenticated user ID. Shadow modes and testing loops explicitly prohibit the use of identifiable PII without consent. 
2.  **AI Act:** We strictly prohibit generative AI (LLMs) on the financial/decisioning critical path. All odds, stakes, and returns are generated via deterministic, pre-approved templates. 
3.  **WCAG 2.1 AA:** The user interface interventions are text-based and high-contrast, designed to be read by screen readers without time-based urgency mechanics.

## Responsible Gambling (RG) Constraints
1.  **Safety Gates Before Policy:** If a user is self-excluded or triggers a harm indicator threshold, the safety check returns `NO_INTERVENTION`. The policy authority is structurally prevented from seeing unsafe candidate actions.
2.  **Harm-Neutrality:** Our evaluation framework runs statistical chi-squared tests to ensure that the contextual bandit policy never increases harm indicators over the control group.
3.  **No Dark Patterns:** The Action Registry explicitly contains no urgency mechanics (e.g., countdown timers) or scarcity mechanics (e.g., "only 2 left").
