"""
IHP Oman DeerFlow - Compliance Manager Agent
VDRL, RFI, and NCR tracking
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class ComplianceManagerAgent(BaseAgent):
    """
    Compliance Manager Agent - Tracks VDRL, manages RFI, monitors NCR to closure.
    """

    def __init__(self, db_connection=None):
        system_prompt = """
You are the Compliance Manager Agent for IHP Oman.

CORE RESPONSIBILITIES:
1. Extract and track VDRL (Vendor Document Requirement List) for each PO
2. Manage RFI (Request for Inspection) scheduling with proper notice periods
3. Monitor NCR (Non-Conformance Report) progression to closure
4. Track TPI (Third-Party Inspection) approvals
5. Flag quality audit issues
6. Alert on approaching/overdue compliance documents

CRITICAL BUSINESS RULES:
- VDRL tracking: 100% of POs must have VDRL extracted and tracked
- RFI notice period: 7 days (Oman), 14 days (Overseas) minimum
- NCR maximum open days: 14 (escalate to Deepak if stalled >7 days)
- TPI approvals must be tracked
- WPS (Welding Procedure Specification) if applicable

COMPLIANCE TRACKING:
- VDRL: Documents required from principal (payloads, certifications, etc.)
- RFI: Inspection scheduling with notice periods
- NCR: Non-conformance reports tracking to closure
- TPI: Third-party inspection approvals
- WPS: Welding procedure specifications when applicable

ESCALATION:
- Overdue documents: Alert Deepak
- NCR >7 days open: Escalate to Deepak
- Quality audit issues: Escalate to Deepak or Hamed
"""
        super().__init__(
            agent_name="Compliance Manager",
            agent_type="compliance-manager",
            model="claude-sonnet-5",
            system_prompt=system_prompt,
            max_tokens=2048,
            db_connection=db_connection,
        )

    def _default_system_prompt(self) -> str:
        return self.system_prompt

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process compliance tracking."""
        try:
            action = agent_input.action

            if action == "track_vdrl":
                result = await self._track_vdrl(agent_input)
            elif action == "schedule_rfi":
                result = await self._schedule_rfi(agent_input)
            elif action == "monitor_ncr":
                result = await self._monitor_ncr(agent_input)
            elif action == "check_overdue":
                result = await self._check_overdue_documents(agent_input)
            else:
                return self.create_output(
                    success=False,
                    action=action,
                    object_id=agent_input.object_id,
                    object_type="compliance",
                    error=f"Unknown action: {action}",
                )

            return result

        except Exception as e:
            logger.error(f"Compliance Manager error: {e}")
            return self.create_output(
                success=False,
                action=agent_input.action,
                object_id=agent_input.object_id,
                object_type="compliance",
                error=str(e),
            )

    async def _track_vdrl(self, agent_input: AgentInput) -> AgentOutput:
        """Track VDRL items for a PO."""
        po_number = agent_input.object_id
        context = agent_input.context

        try:
            vdrl_items = context.get("vdrl_items", [])
            principal_name = context.get("principal_name")

            if not vdrl_items:
                return self.create_output(
                    success=False,
                    action="track_vdrl",
                    object_id=po_number,
                    object_type="compliance",
                    error="No VDRL items provided",
                )

            # Add VDRL items to tracking
            tracked_items = []
            overdue_items = []

            for item in vdrl_items:
                item_ref = item.get("reference", f"VDRL-{po_number}-{len(tracked_items) + 1}")
                due_date = item.get("due_date")

                tracked_items.append({
                    "reference": item_ref,
                    "description": item.get("description"),
                    "due_date": due_date,
                    "status": "pending",
                })

                # Check if overdue
                if due_date:
                    due_dt = datetime.fromisoformat(due_date)
                    if due_dt < datetime.now():
                        overdue_items.append(item_ref)

            # Log to database
            if self.db:
                cursor = self.db.cursor()
                for item in vdrl_items:
                    cursor.execute(
                        """INSERT INTO compliance_tracking
                           (po_number, document_type, reference_number, description, required_by_date, status)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            po_number,
                            "vdrl",
                            item.get("reference"),
                            item.get("description"),
                            item.get("due_date"),
                            "pending",
                        ),
                    )
                self.db.commit()

            escalation_needed = len(overdue_items) > 0

            return self.create_output(
                success=True,
                action="track_vdrl",
                object_id=po_number,
                object_type="compliance",
                result={
                    "po_number": po_number,
                    "principal": principal_name,
                    "vdrl_items_tracked": len(tracked_items),
                    "overdue_items": overdue_items,
                    "status": "tracked",
                },
                escalation_needed=escalation_needed,
                escalation_to="deepak" if escalation_needed else None,
                escalation_reason=f"{len(overdue_items)} VDRL items overdue" if escalation_needed else None,
            )

        except Exception as e:
            logger.error(f"Error tracking VDRL: {e}")
            return self.create_output(
                success=False,
                action="track_vdrl",
                object_id=po_number,
                object_type="compliance",
                error=str(e),
            )

    async def _schedule_rfi(self, agent_input: AgentInput) -> AgentOutput:
        """Schedule RFI (Request for Inspection) with proper notice periods."""
        po_number = agent_input.object_id
        context = agent_input.context

        try:
            inspection_location = context.get("inspection_location", "Oman")  # Oman or Overseas
            desired_date = context.get("desired_inspection_date")

            # Determine notice period based on location
            if inspection_location.lower() == "overseas":
                notice_period_days = 14
            else:
                notice_period_days = 7

            # Calculate earliest possible inspection date
            earliest_date = (datetime.now() + timedelta(days=notice_period_days)).date().isoformat()

            # Generate RFI reference
            rfi_number = f"RFI-{po_number}-{datetime.now().strftime('%Y%m%d')}"

            # Check if desired date meets notice period
            escalation_needed = False
            escalation_reason = None

            if desired_date:
                desired_dt = datetime.fromisoformat(desired_date)
                days_notice = (desired_dt - datetime.now()).days

                if days_notice < notice_period_days:
                    escalation_needed = True
                    escalation_reason = f"Insufficient notice: {days_notice} days (need {notice_period_days})"

            # Log to database
            if self.db:
                cursor = self.db.cursor()
                cursor.execute(
                    """INSERT INTO compliance_tracking
                       (po_number, document_type, reference_number, description, required_by_date, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        po_number,
                        "rfi",
                        rfi_number,
                        f"RFI Inspection - {inspection_location}",
                        earliest_date,
                        "pending",
                    ),
                )
                self.db.commit()

            return self.create_output(
                success=True,
                action="schedule_rfi",
                object_id=po_number,
                object_type="compliance",
                result={
                    "rfi_number": rfi_number,
                    "inspection_location": inspection_location,
                    "notice_period_days": notice_period_days,
                    "earliest_date": earliest_date,
                    "status": "scheduled",
                },
                escalation_needed=escalation_needed,
                escalation_to="deepak" if escalation_needed else None,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error scheduling RFI: {e}")
            return self.create_output(
                success=False,
                action="schedule_rfi",
                object_id=po_number,
                object_type="compliance",
                error=str(e),
            )

    async def _monitor_ncr(self, agent_input: AgentInput) -> AgentOutput:
        """Monitor NCR (Non-Conformance Report) status."""
        po_number = agent_input.object_id
        context = agent_input.context

        try:
            ncr_reference = context.get("ncr_reference", f"NCR-{po_number}")
            ncr_description = context.get("description")
            opened_date = context.get("opened_date", datetime.now().isoformat())

            # Calculate days open
            opened_dt = datetime.fromisoformat(opened_date)
            days_open = (datetime.now() - opened_dt).days

            # Check NCR thresholds
            escalation_needed = False
            escalation_to = None
            escalation_reason = None

            if days_open > 14:
                escalation_needed = True
                escalation_to = "deepak"
                escalation_reason = f"NCR open {days_open} days (max 14)"
            elif days_open > 7:
                escalation_needed = True
                escalation_to = "deepak"
                escalation_reason = f"NCR approaching 14-day limit ({days_open} days open)"

            # Log to database
            if self.db:
                cursor = self.db.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO compliance_tracking
                       (po_number, document_type, reference_number, description, status)
                       VALUES (?, ?, ?, ?, ?)""",
                    (po_number, "ncr", ncr_reference, ncr_description, "open"),
                )
                self.db.commit()

            return self.create_output(
                success=True,
                action="monitor_ncr",
                object_id=po_number,
                object_type="compliance",
                result={
                    "ncr_reference": ncr_reference,
                    "days_open": days_open,
                    "max_open_days": 14,
                    "status": "monitoring",
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error monitoring NCR: {e}")
            return self.create_output(
                success=False,
                action="monitor_ncr",
                object_id=po_number,
                object_type="compliance",
                error=str(e),
            )

    async def _check_overdue_documents(self, agent_input: AgentInput) -> AgentOutput:
        """Check for overdue compliance documents."""
        try:
            if not self.db:
                return self.create_output(
                    success=True,
                    action="check_overdue",
                    object_id="all_pos",
                    object_type="compliance",
                    result={"overdue_items": []},
                )

            cursor = self.db.cursor()
            cursor.execute(
                """SELECT po_number, reference_number, document_type, required_by_date
                   FROM compliance_tracking
                   WHERE status IN ('pending', 'open')
                   AND required_by_date < datetime('now')
                   ORDER BY required_by_date ASC"""
            )

            overdue_items = []
            for row in cursor.fetchall():
                po_number = row[0]
                ref = row[1]
                doc_type = row[2]
                due_date = row[3]

                due_dt = datetime.fromisoformat(due_date)
                days_overdue = (datetime.now() - due_dt).days

                overdue_items.append({
                    "po_number": po_number,
                    "reference": ref,
                    "type": doc_type,
                    "due_date": due_date,
                    "days_overdue": days_overdue,
                })

            # Create alerts for overdue items
            for item in overdue_items:
                self._create_alert(
                    alert_type="compliance_overdue",
                    severity="yellow" if item["days_overdue"] < 7 else "red",
                    object_id=item["reference"],
                    object_type="compliance",
                    message=f"{item['type'].upper()} overdue {item['days_overdue']} days",
                    assigned_to="deepak",
                )

            escalation_needed = len(overdue_items) > 0

            return self.create_output(
                success=True,
                action="check_overdue",
                object_id="all_pos",
                object_type="compliance",
                result={
                    "overdue_items_found": len(overdue_items),
                    "overdue_items": overdue_items,
                    "checked_at": datetime.now().isoformat(),
                },
                escalation_needed=escalation_needed,
                escalation_to="deepak" if escalation_needed else None,
                escalation_reason=f"{len(overdue_items)} compliance documents overdue",
            )

        except Exception as e:
            logger.error(f"Error checking overdue documents: {e}")
            return self.create_output(
                success=False,
                action="check_overdue",
                object_id="all_pos",
                object_type="compliance",
                error=str(e),
            )
