"""
IHP Oman DeerFlow - RFQ Handler Agent
Portal monitoring and tender logging
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


@dataclass
class RFQData:
    """RFQ data structure."""
    rfx_number: str  # Operator's tender reference
    operator_name: str
    bcd_date: str  # Bid Closing Date
    description: str
    received_date: str


class RFQHandlerAgent(BaseAgent):
    """
    RFQ Handler Agent - Monitors RFQ portals, logs tenders, forwards to principals.
    """

    # Principals and their specialties
    PRINCIPALS = {
        "autocontrol": {
            "name": "Autocontrol Process Instrumentation",
            "location": "India/UAE",
            "specialties": ["flow_instruments", "level_instruments", "pressure_instruments"],
            "payment_terms": 30,
        },
        "kam": {
            "name": "KAM",
            "location": "USA",
            "specialties": ["water_cut_meters", "flow_measurement"],
            "payment_terms": 45,
        },
        "terranova": {
            "name": "Terranova Instruments",
            "location": "Global",
            "specialties": ["general_instrumentation"],
            "payment_terms": 30,
            "compliance_heavy": True,
        },
    }

    def __init__(self, db_connection=None):
        system_prompt = """
You are the RFQ Handler Agent for IHP Oman.

CORE RESPONSIBILITIES:
1. Monitor RFQ sources (PDO Rabithah, Tatweer, email)
2. Log ALL tenders immediately with: RFX#, IHP RFQ#, BCD, description
3. Forward to appropriate principal SAME DAY
4. Track BCD countdown and alert if no response approaching deadline
5. Send regret notices if IHP decides not to bid

CRITICAL BUSINESS RULES:
- RFQs must be LOGGED same-day (0 day max)
- RFQs must be FORWARDED same-day (0 day max)
- BCD is HARD DEADLINE - no exceptions
- If no principal available: escalate to Deepak
- Regret notices must be professional with business reason

OPERATOR PRIORITY:
1. PDO (Petroleum Development Oman) - CRITICAL (VDP 68.96% at risk)
2. OQ8/OQ - High priority
3. bp Oman - High priority
4. Shell Oman - High priority
5. Marsa LNG - Medium priority
6. MEDCO LLC - Medium priority
7. Tatweer/Business Gateways - Medium priority

PRINCIPAL ROUTING:
- Flow/Level/Pressure instruments → Autocontrol
- Water-cut meters (OWD) → KAM
- General instruments → Terranova (check compliance requirements)

ACTIONS:
- Accept: Log and forward to principal
- Miss BCD: Alert to Deepak (operational escalation)
- No principal match: Escalate to Deepak
- Multiple principals possible: Forward to best fit (check capacity)
"""
        super().__init__(
            agent_name="RFQ Handler",
            agent_type="rfq-handler",
            model="claude-sonnet-5",
            system_prompt=system_prompt,
            max_tokens=2048,
            db_connection=db_connection,
        )

    def _default_system_prompt(self) -> str:
        return self.system_prompt

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process RFQ: log and forward to principal."""
        try:
            # Log incoming RFQ
            self._log_action(
                action_type="rfq_receive",
                object_id=agent_input.object_id,
                object_type="rfq",
                status="received",
            )

            # Extract RFQ data from context
            rfq_data = self._extract_rfq_data(agent_input)

            if not rfq_data:
                return self.create_output(
                    success=False,
                    action="log_rfq",
                    object_id=agent_input.object_id,
                    object_type="rfq",
                    error="Missing required RFQ data",
                )

            # Check if already logged (duplicate check)
            if await self._is_rfq_logged(rfq_data.rfx_number):
                return self.create_output(
                    success=False,
                    action="log_rfq",
                    object_id=agent_input.object_id,
                    object_type="rfq",
                    error=f"RFQ {rfq_data.rfx_number} already logged",
                )

            # Generate IHP RFQ number
            ihp_rfq_number = await self._generate_ihp_rfq_number()

            # Log RFQ to database
            await self._log_rfq_to_db(rfq_data, ihp_rfq_number)

            # Check BCD deadline (must forward same day)
            bcd_datetime = datetime.fromisoformat(rfq_data.bcd_date)
            hours_until_bcd = (bcd_datetime - datetime.now()).total_seconds() / 3600

            if hours_until_bcd < 1:
                # BCD is within 1 hour - urgent!
                escalation_needed = True
                escalation_to = "deepak"
                escalation_reason = f"RFQ {rfq_data.rfx_number} BCD in {hours_until_bcd:.1f} hours"
            else:
                escalation_needed = False
                escalation_to = None
                escalation_reason = None

            # Route to appropriate principal
            principal = self._route_to_principal(rfq_data)

            if not principal:
                return self.create_output(
                    success=True,
                    action="log_rfq",
                    object_id=ihp_rfq_number,
                    object_type="rfq",
                    result={
                        "rfx_number": rfq_data.rfx_number,
                        "ihp_rfq_number": ihp_rfq_number,
                        "logged": True,
                        "forwarded": False,
                        "status": "pending_principal_match",
                    },
                    escalation_needed=True,
                    escalation_to="deepak",
                    escalation_reason="No principal available for RFQ type",
                )

            # Forward to principal
            await self._forward_to_principal(ihp_rfq_number, principal, rfq_data)

            # Log action
            self._log_action(
                action_type="rfq_forward",
                object_id=ihp_rfq_number,
                object_type="rfq",
                status="forwarded",
                message=f"Forwarded to {principal['name']}",
            )

            return self.create_output(
                success=True,
                action="log_and_forward_rfq",
                object_id=ihp_rfq_number,
                object_type="rfq",
                result={
                    "rfx_number": rfq_data.rfx_number,
                    "ihp_rfq_number": ihp_rfq_number,
                    "operator": rfq_data.operator_name,
                    "bcd_date": rfq_data.bcd_date,
                    "hours_until_bcd": round(hours_until_bcd, 1),
                    "logged": True,
                    "forwarded_to": principal["name"],
                    "forwarded_date": datetime.now().isoformat(),
                    "status": "forwarded",
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"RFQ Handler error: {e}")
            return self.create_output(
                success=False,
                action="log_rfq",
                object_id=agent_input.object_id,
                object_type="rfq",
                error=str(e),
            )

    def _extract_rfq_data(self, agent_input: AgentInput) -> Optional[RFQData]:
        """Extract RFQ data from agent input."""
        context = agent_input.context

        try:
            return RFQData(
                rfx_number=context.get("rfx_number"),
                operator_name=context.get("operator_name"),
                bcd_date=context.get("bcd_date"),
                description=context.get("description"),
                received_date=context.get("received_date", datetime.now().isoformat()),
            )
        except (KeyError, TypeError):
            return None

    async def _is_rfq_logged(self, rfx_number: str) -> bool:
        """Check if RFQ is already logged."""
        if not self.db:
            return False

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT id FROM rfq_tracking WHERE rfx_number = ?", (rfx_number,))
            return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Error checking RFQ: {e}")
            return False

    async def _generate_ihp_rfq_number(self) -> str:
        """Generate unique IHP RFQ number."""
        if not self.db:
            return f"IHP-RFQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM rfq_tracking")
            count = cursor.fetchone()[0]
            return f"IHP-RFQ-{count + 1:06d}"
        except Exception as e:
            logger.error(f"Error generating RFQ number: {e}")
            return f"IHP-RFQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    async def _log_rfq_to_db(self, rfq_data: RFQData, ihp_rfq_number: str):
        """Log RFQ to database."""
        if not self.db:
            logger.info(f"Would log RFQ: {rfq_data.rfx_number} → {ihp_rfq_number}")
            return

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """
                INSERT INTO rfq_tracking
                (rfx_number, ihp_rfq_number, operator_name, description,
                 bcd_date, received_date, logged_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rfq_data.rfx_number,
                    ihp_rfq_number,
                    rfq_data.operator_name,
                    rfq_data.description,
                    rfq_data.bcd_date,
                    rfq_data.received_date,
                    datetime.now().isoformat(),
                    "logged",
                ),
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging RFQ: {e}")

    def _route_to_principal(self, rfq_data: RFQData) -> Optional[Dict[str, Any]]:
        """Route RFQ to appropriate principal based on description."""
        description_lower = rfq_data.description.lower()

        # Check each principal's specialties
        for principal_key, principal_info in self.PRINCIPALS.items():
            for specialty in principal_info["specialties"]:
                if specialty.replace("_", " ") in description_lower or specialty.replace("_", "-") in description_lower:
                    return principal_info

        # Default to Terranova for general instrumentation
        return self.PRINCIPALS.get("terranova")

    async def _forward_to_principal(self, ihp_rfq_number: str, principal: Dict[str, Any], rfq_data: RFQData):
        """Send RFQ to principal via email."""
        if not self.db:
            logger.info(f"Would forward {ihp_rfq_number} to {principal['name']}")
            return

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """
                UPDATE rfq_tracking
                SET forwarded_to_principal = ?, forwarded_date = ?, status = 'forwarded'
                WHERE ihp_rfq_number = ?
                """,
                (principal["name"], datetime.now().isoformat(), ihp_rfq_number),
            )
            self.db.commit()
            # TODO: Send email to principal with RFQ details
        except Exception as e:
            logger.error(f"Error forwarding RFQ: {e}")
