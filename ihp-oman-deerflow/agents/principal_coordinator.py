"""
IHP Oman DeerFlow - Principal Coordinator Agent
Technical queries and quotation compilation
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class PrincipalCoordinatorAgent(BaseAgent):
    """
    Principal Coordinator Agent - Manages technical queries, compiles quotations, submits bids.
    """

    def __init__(self, db_connection=None):
        system_prompt = """
You are the Principal Coordinator Agent for IHP Oman.

CORE RESPONSIBILITIES:
1. Monitor for Technical Queries (TQ-01, TQ-02, ...) from operators on open RFQs
2. Forward TQs to principal, track responses (48-hour timeout)
3. Compile principal's offer with IHP commercial terms
4. Create quotation and submit to operator before BCD
5. Handle pricing authority (>20% discount needs Hamed approval)
6. Track multi-round negotiations (TR1=initial, TR2=revision, etc.)

CRITICAL BUSINESS RULES:
- TQ response timeout: 48 hours (escalate to Deepak if delayed)
- Quotation submission: Submit 24 hours before BCD minimum
- Standard margin: 15% (min 12%, max 25%)
- Pricing >20% discount: Escalate to Hamed for approval
- Revision rounds tracked (TR1, TR2, etc.)

PRINCIPALS:
- Autocontrol: Flow/Level/Pressure instruments (30 day terms)
- KAM: Water-cut meters/Flow measurement (45 day terms)
- Terranova: General instruments (30 day terms, compliance heavy)

WORKFLOW:
1. Receive TQ notification from RFQ
2. Forward TQ to principal, set 48-hour response timer
3. Receive principal's offer
4. Apply IHP margin (15% standard)
5. Check if discount needed (if >20%, escalate to Hamed)
6. Create quotation with all details
7. Submit to operator before BCD
"""
        super().__init__(
            agent_name="Principal Coordinator",
            agent_type="principal-coordinator",
            model="claude-sonnet-5",
            system_prompt=system_prompt,
            max_tokens=2048,
            db_connection=db_connection,
        )

    def _default_system_prompt(self) -> str:
        return self.system_prompt

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process quotation workflow."""
        try:
            action = agent_input.action

            if action == "forward_technical_query":
                result = await self._forward_technical_query(agent_input)
            elif action == "compile_quotation":
                result = await self._compile_quotation(agent_input)
            elif action == "submit_quotation":
                result = await self._submit_quotation(agent_input)
            else:
                return self.create_output(
                    success=False,
                    action=action,
                    object_id=agent_input.object_id,
                    object_type="quotation",
                    error=f"Unknown action: {action}",
                )

            return result

        except Exception as e:
            logger.error(f"Principal Coordinator error: {e}")
            return self.create_output(
                success=False,
                action=agent_input.action,
                object_id=agent_input.object_id,
                object_type="quotation",
                error=str(e),
            )

    async def _forward_technical_query(self, agent_input: AgentInput) -> AgentOutput:
        """Forward technical query to principal."""
        rfq_id = agent_input.object_id
        context = agent_input.context

        try:
            principal_name = context.get("principal_name")
            tq_details = context.get("tq_details")

            if not principal_name or not tq_details:
                return self.create_output(
                    success=False,
                    action="forward_technical_query",
                    object_id=rfq_id,
                    object_type="quotation",
                    error="Missing principal_name or tq_details",
                )

            # Generate TQ reference
            tq_number = await self._generate_tq_number()

            # Log the technical query
            if self.db:
                cursor = self.db.cursor()
                cursor.execute(
                    """INSERT INTO agent_logs
                       (agent_name, agent_type, action_type, object_type, object_id, status, message)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        self.agent_name,
                        self.agent_type,
                        "tq_forward",
                        "quotation",
                        rfq_id,
                        "forwarded",
                        f"TQ {tq_number} forwarded to {principal_name}",
                    ),
                )
                self.db.commit()

            # Set response timeout (48 hours)
            response_deadline = (datetime.now() + timedelta(hours=48)).isoformat()

            # Check for timeout risk
            escalation_needed = False
            escalation_to = "deepak"
            escalation_reason = None

            return self.create_output(
                success=True,
                action="forward_technical_query",
                object_id=rfq_id,
                object_type="quotation",
                result={
                    "tq_number": tq_number,
                    "principal": principal_name,
                    "tq_details": tq_details,
                    "forwarded_at": datetime.now().isoformat(),
                    "response_deadline": response_deadline,
                    "status": "awaiting_response",
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error forwarding TQ: {e}")
            return self.create_output(
                success=False,
                action="forward_technical_query",
                object_id=rfq_id,
                object_type="quotation",
                error=str(e),
            )

    async def _compile_quotation(self, agent_input: AgentInput) -> AgentOutput:
        """Compile quotation from principal offer with IHP terms."""
        rfq_id = agent_input.object_id
        context = agent_input.context

        try:
            principal_offer_price = context.get("principal_offer_price")
            ihp_margin_percent = context.get("ihp_margin_percent", 15.0)  # Default 15%
            bcd_date = context.get("bcd_date")

            if not principal_offer_price or not bcd_date:
                return self.create_output(
                    success=False,
                    action="compile_quotation",
                    object_id=rfq_id,
                    object_type="quotation",
                    error="Missing principal_offer_price or bcd_date",
                )

            # Calculate IHP selling price
            ihp_selling_price = principal_offer_price * (1 + ihp_margin_percent / 100)

            # Check if discount is needed (if margin < 12% or > 25%)
            escalation_needed = False
            escalation_to = None
            escalation_reason = None

            if ihp_margin_percent > 20:
                escalation_needed = True
                escalation_to = "hamed"
                escalation_reason = f"High discount: {ihp_margin_percent}% exceeds 20% authority"
            elif ihp_margin_percent < 12:
                escalation_needed = True
                escalation_to = "deepak"
                escalation_reason = f"Low margin: {ihp_margin_percent}% below 12% minimum"

            # Generate quotation number
            quotation_number = await self._generate_quotation_number(rfq_id)

            # Calculate hours until BCD
            bcd_dt = datetime.fromisoformat(bcd_date)
            hours_until_bcd = (bcd_dt - datetime.now()).total_seconds() / 3600

            # Check if enough time to submit (24 hour buffer)
            if hours_until_bcd < 24:
                escalation_needed = True
                escalation_to = "deepak"
                escalation_reason = f"Tight deadline: Only {hours_until_bcd:.1f} hours until BCD"

            return self.create_output(
                success=True,
                action="compile_quotation",
                object_id=quotation_number,
                object_type="quotation",
                result={
                    "quotation_number": quotation_number,
                    "rfq_id": rfq_id,
                    "principal_offer_price": principal_offer_price,
                    "ihp_margin_percent": ihp_margin_percent,
                    "ihp_selling_price": round(ihp_selling_price, 2),
                    "bcd_date": bcd_date,
                    "hours_until_bcd": round(hours_until_bcd, 1),
                    "status": "ready_to_submit",
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error compiling quotation: {e}")
            return self.create_output(
                success=False,
                action="compile_quotation",
                object_id=rfq_id,
                object_type="quotation",
                error=str(e),
            )

    async def _submit_quotation(self, agent_input: AgentInput) -> AgentOutput:
        """Submit compiled quotation to operator."""
        quotation_id = agent_input.object_id
        context = agent_input.context

        try:
            operator_email = context.get("operator_email")
            quotation_details = context.get("quotation_details")

            if not operator_email:
                return self.create_output(
                    success=False,
                    action="submit_quotation",
                    object_id=quotation_id,
                    object_type="quotation",
                    error="Missing operator_email",
                )

            # Log submission
            self._log_action(
                action_type="quotation_submit",
                object_id=quotation_id,
                object_type="quotation",
                status="submitted",
                message=f"Submitted to {operator_email}",
            )

            return self.create_output(
                success=True,
                action="submit_quotation",
                object_id=quotation_id,
                object_type="quotation",
                result={
                    "quotation_number": quotation_id,
                    "submitted_to": operator_email,
                    "submitted_at": datetime.now().isoformat(),
                    "status": "submitted",
                },
            )

        except Exception as e:
            logger.error(f"Error submitting quotation: {e}")
            return self.create_output(
                success=False,
                action="submit_quotation",
                object_id=quotation_id,
                object_type="quotation",
                error=str(e),
            )

    async def _generate_tq_number(self) -> str:
        """Generate unique TQ reference number."""
        if not self.db:
            return f"TQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM agent_logs WHERE action_type = 'tq_forward'")
            count = cursor.fetchone()[0]
            return f"TQ-{count + 1:05d}"
        except Exception as e:
            logger.error(f"Error generating TQ number: {e}")
            return f"TQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    async def _generate_quotation_number(self, rfq_id: str) -> str:
        """Generate unique quotation number."""
        if not self.db:
            return f"QUOTE-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM quotation_tracking")
            count = cursor.fetchone()[0]
            return f"QUOTE-{count + 1:06d}"
        except Exception as e:
            logger.error(f"Error generating quotation number: {e}")
            return f"QUOTE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
