import re

with open("src/confidence/application/engine.py", "r") as f:
    engine = f.read()

if "from confidence.infrastructure.audit import BackgroundAuditLogger" not in engine:
    engine = engine.replace(
        "from confidence.infrastructure.persistence import DatabasePersistenceProvider",
        "from confidence.infrastructure.persistence import DatabasePersistenceProvider\nfrom confidence.infrastructure.audit import BackgroundAuditLogger"
    )
    
    engine = engine.replace(
        "        self.persistence = persistence_provider",
        "        self.persistence = persistence_provider\n        self.audit_logger = audit_logger"
    )

    engine = engine.replace(
        "        persistence_provider: DatabasePersistenceProvider,",
        "        persistence_provider: DatabasePersistenceProvider,\n        audit_logger: 'BackgroundAuditLogger | None' = None,"
    )

    # In engine.decide
    # Create the AuditRecord
    audit_insertion = """        decision_id = result.decision.decision_id
        
        if self.audit_logger:
            from confidence.domain.models import AuditRecord
            from uuid import uuid4
            audit_record = AuditRecord(
                audit_id=uuid4(),
                decision_id=decision_id,
                timestamp=result.decision.timestamp,
                context_snapshot=context,
                safety_result=safety_result,
                state_estimate=state_estimate,
                candidate_actions=result.decision.candidate_actions,
                selected_action=result.decision.selected_action,
                no_intervention_reason=result.decision.no_intervention_reason,
                policy_version=result.decision.policy_version,
                model_version=result.decision.model_version,
                action_registry_version=result.decision.action_registry_version,
                facts_version=result.decision.facts_version,
                reason=result.decision.reason,
                response_text=result.response_text,
            )
            self.audit_logger.log_decision(audit_record)
"""
    engine = engine.replace(
        "        # Fire-and-forget persistence",
        audit_insertion + "\n        # Fire-and-forget persistence"
    )

    with open("src/confidence/application/engine.py", "w") as f:
        f.write(engine)

print("Updated engine.py")
