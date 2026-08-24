"""
IHP Oman DeerFlow - Orchestrator Agent
Lead coordinator for all specialist agents
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Lead Orchestrator Agent - Coordinates all specialist agents and makes escalation decisions.
    """

    def __init__(self, db_connection=None):
        system_prompt = """
You are the Lead Orchestrator for IHP Oman's RFQ-to-cash workflow automation system.

ROLE & RESPONSIBILITIES:
- Coordinate RFQ Handler, Principal Coordinator, Compliance Manager, VDP Tracker, Collections Handler
- Route work items to appropriate specialist agents
- Monitor for escalation flags from all agents
- Make escalation decisions to Deepak (operations) or Hamed (strategic)
- Generate daily leadership briefs
- Alert on critical business issues

CRITICAL BUSINESS CONTEXT:
- VDP (Vendor Delivery Performance) is EXISTENTIAL for PDO: 68.96% → 90% target within 6 months
- PDO stated: "Will reconsider doing business if VDP < 90%"
- All RFQs require bid or regret by BCD (same-day response standard)
- Same-day SOA (Statement of Account) responses required
- Reference numbers (RFX#, IHP RFQ#, PO#) are sacred

ESCALATION RULES:
TO DEEPAK (Manager – Sales & Services):
- Any delivery slip on PDO PO
- RFQ approaching BCD with no response
- Principal TQ response >48 hours delayed
- NCR open >7 days
- Customer invoice >60 days overdue
- Principal SOA unanswered 24+ hours

TO HAMED (Managing Director):
- VDP trending <75% (critical business risk)
- New principal registration/opportunity
- Pricing authority exceeded (discount >20%)
- Customer relationship at risk
- Legal/regulatory compliance issue
- Revenue impact >$500K at risk

DECISION LOGIC:
1. Receive incoming item (RFQ, quotation, PO, compliance, collection)
2. Determine primary handler agent
3. Send to agent with context
4. Monitor response for escalation flags
5. If escalation triggered, determine recipient (Deepak or Hamed)
6. Create alert and notify

OUTPUT MUST INCLUDE:
- Coordinated actions (which agents to involve)
- Alerts (what leadership needs to know)
- Escalations (if any)
- Daily summary for reporting
"""
        super().__init__(
            agent_name="Orchestrator",
            agent_type="orchestrator",
            model="claude-opus-5",
            system_prompt=system_prompt,
            max_tokens=4096,
            db_connection=db_connection,
        )

    def _default_system_prompt(self) -> str:
        return self.system_prompt

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """
        Process incoming item and coordinate appropriate agents.
        """
        try:
            # Log incoming action
            self._log_action(
                action_type="coordination_receive",
                object_id=agent_input.object_id,
                object_type=agent_input.object_type,
                status="processing",
            )

            # Route based on object type
            if agent_input.object_type == "rfq":
                result = await self._handle_rfq(agent_input)
            elif agent_input.object_type == "quotation":
                result = await self._handle_quotation(agent_input)
            elif agent_input.object_type == "po":
                result = await self._handle_po(agent_input)
            elif agent_input.object_type == "compliance":
                result = await self._handle_compliance(agent_input)
            elif agent_input.object_type == "collection":
                result = await self._handle_collection(agent_input)
            elif agent_input.object_type == "payable":
                result = await self._handle_payable(agent_input)
            else:
                return self.create_output(
                    success=False,
                    action=agent_input.action,
                    object_id=agent_input.object_id,
                    object_type=agent_input.object_type,
                    error=f"Unknown object type: {agent_input.object_type}",
                )

            return result

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return self.create_output(
                success=False,
                action=agent_input.action,
                object_id=agent_input.object_id,
                object_type=agent_input.object_type,
                error=str(e),
            )

    async def _handle_rfq(self, agent_input: AgentInput) -> AgentOutput:
        """Route RFQ to RFQ Handler agent."""
        coordinated = {
            "primary_agent": "RFQ Handler",
            "actions": [
                "log_rfq",
                "forward_to_principal",
                "track_bcd",
            ],
        }

        return self.create_output(
            success=True,
            action=agent_input.action,
            object_id=agent_input.object_id,
            object_type="rfq",
            result={
                "coordination": coordinated,
                "routing": "rfq-handler",
                "priority": "high" if "pdo" in agent_input.context.get("operator", "").lower() else "medium",
            },
        )

    async def _handle_quotation(self, agent_input: AgentInput) -> AgentOutput:
        """Route quotation to Principal Coordinator agent."""
        coordinated = {
            "primary_agent": "Principal Coordinator",
            "actions": [
                "handle_technical_queries",
                "compile_quotation",
                "submit_to_operator",
            ],
        }

        return self.create_output(
            success=True,
            action=agent_input.action,
            object_id=agent_input.object_id,
            object_type="quotation",
            result={
                "coordination": coordinated,
                "routing": "principal-coordinator",
            },
        )

    async def _handle_po(self, agent_input: AgentInput) -> AgentOutput:
        """Route PO to multiple agents: Compliance Manager and VDP Tracker."""
        coordinated = {
            "primary_agents": ["Compliance Manager", "VDP Tracker"],
            "actions": {
                "compliance": ["track_vdrl", "manage_rfi", "monitor_ncr"],
                "vdp": ["monitor_delivery_date", "calculate_vdp", "alert_on_slip"],
            },
        }

        return self.create_output(
            success=True,
            action=agent_input.action,
            object_id=agent_input.object_id,
            object_type="po",
            result={
                "coordination": coordinated,
                "routing": ["compliance-manager", "vdp-tracker"],
                "priority": "critical" if "pdo" in agent_input.context.get("operator", "").lower() else "high",
            },
        )

    async def _handle_compliance(self, agent_input: AgentInput) -> AgentOutput:
        """Route compliance item to Compliance Manager."""
        coordinated = {
            "primary_agent": "Compliance Manager",
            "actions": ["track_document", "alert_on_overdue"],
        }

        return self.create_output(
            success=True,
            action=agent_input.action,
            object_id=agent_input.object_id,
            object_type="compliance",
            result={"coordination": coordinated, "routing": "compliance-manager"},
        )

    async def _handle_collection(self, agent_input: AgentInput) -> AgentOutput:
        """Route collection/invoice to Collections Handler."""
        coordinated = {
            "primary_agent": "Collections Handler",
            "actions": ["track_receivable", "send_reminder", "escalate_if_overdue"],
        }

        return self.create_output(
            success=True,
            action=agent_input.action,
            object_id=agent_input.object_id,
            object_type="collection",
            result={"coordination": coordinated, "routing": "collections-handler"},
        )

    async def _handle_payable(self, agent_input: AgentInput) -> AgentOutput:
        """Route SOA/payable to Collections Handler."""
        coordinated = {
            "primary_agent": "Collections Handler",
            "actions": ["receive_soa", "acknowledge_same_day", "commit_payment"],
        }

        return self.create_output(
            success=True,
            action=agent_input.action,
            object_id=agent_input.object_id,
            object_type="payable",
            result={
                "coordination": coordinated,
                "routing": "collections-handler",
                "priority": "critical",  # SOA response is same-day critical
            },
        )

    async def generate_daily_brief(self) -> Dict[str, Any]:
        """Generate daily brief for leadership (Deepak, Hamed)."""
        try:
            brief = {
                "date": datetime.now().date().isoformat(),
                "generated_at": datetime.now().isoformat(),
                "sections": {
                    "critical_alerts": await self._get_critical_alerts(),
                    "at_risk_items": await self._get_at_risk_items(),
                    "vdp_status": await self._get_vdp_status(),
                    "today_rfq_bcds": await self._get_today_bcds(),
                    "escalations": await self._get_escalations(),
                },
            }
            return brief
        except Exception as e:
            logger.error(f"Error generating daily brief: {e}")
            return {}

    async def _get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get critical alerts for the day."""
        if not self.db:
            return []

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT alert_type, severity, message, assigned_to
                   FROM alerts
                   WHERE resolved = 0 AND severity IN ('red', 'critical')
                   ORDER BY created_at DESC
                   LIMIT 10"""
            )
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    "type": row[0],
                    "severity": row[1],
                    "message": row[2],
                    "for": row[3],
                })
            return alerts
        except Exception as e:
            logger.error(f"Error fetching critical alerts: {e}")
            return []

    async def _get_at_risk_items(self) -> List[Dict[str, Any]]:
        """Get items at risk (delivery slips, overdue documents)."""
        # Placeholder for fetching at-risk items
        return []

    async def _get_vdp_status(self) -> Dict[str, Any]:
        """Get current VDP status for all operators."""
        if not self.db:
            return {}

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT operator_name, vdp_percentage, vdp_status
                   FROM vdp_tracking
                   WHERE vdp_status IN ('alert', 'critical')
                   ORDER BY vdp_percentage ASC"""
            )
            vdp_status = []
            for row in cursor.fetchall():
                vdp_status.append({
                    "operator": row[0],
                    "vdp": row[1],
                    "status": row[2],
                })
            return {"at_risk_operators": vdp_status}
        except Exception as e:
            logger.error(f"Error fetching VDP status: {e}")
            return {}

    async def _get_today_bcds(self) -> List[Dict[str, Any]]:
        """Get RFQs with BCD today."""
        # Placeholder for fetching today's BCDs
        return []

    async def _get_escalations(self) -> List[Dict[str, Any]]:
        """Get all escalations from last 24 hours."""
        if not self.db:
            return []

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT alert_type, assigned_to, message
                   FROM alerts
                   WHERE created_at > datetime('now', '-1 day')
                   AND assigned_to IN ('deepak', 'hamed')
                   ORDER BY created_at DESC"""
            )
            escalations = []
            for row in cursor.fetchall():
                escalations.append({
                    "type": row[0],
                    "escalated_to": row[1],
                    "reason": row[2],
                })
            return escalations
        except Exception as e:
            logger.error(f"Error fetching escalations: {e}")
            return []
