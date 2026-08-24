"""
IHP Oman DeerFlow - Collections Handler Agent
Receivables and payables management
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class CollectionsHandlerAgent(BaseAgent):
    """
    Collections Handler Agent - Manages invoicing, receivables, and payables.
    """

    def __init__(self, db_connection=None):
        system_prompt = """
You are the Collections Handler Agent for IHP Oman.

CORE RESPONSIBILITIES:
1. Send invoices at each project milestone
2. Track receivables (what customers owe IHP) - follow up at 30, 60, 90 days
3. Monitor SOA (Statement of Account) from principals (what IHP owes them)
4. Respond to SOA same-day with payment commitment
5. Send payment reminders (REMINDER-01, REMINDER-02, etc.)
6. Escalate overdue payments

CRITICAL BUSINESS RULES:
- Invoice follow-up: 30 days (first reminder), 60 days (escalate to Deepak), 90 days (escalate to Hamed)
- SOA response time: Same day required (24 hours max)
- Same-day response rate target: 95%
- Reminder severity: High priority

PAYMENT TERMS:
- Autocontrol: 30 days
- KAM: 45 days
- Terranova: 30 days

WORKFLOW:
1. Invoice sent → Track receivable
2. 30 days: Send reminder (REMINDER-01)
3. 60 days: Escalate to Deepak + send reminder (REMINDER-02)
4. 90 days: Escalate to Hamed + send final reminder
5. SOA received → Acknowledge same-day + commit payment
"""
        super().__init__(
            agent_name="Collections Handler",
            agent_type="collections-handler",
            model="claude-sonnet-5",
            system_prompt=system_prompt,
            max_tokens=2048,
            db_connection=db_connection,
        )

    def _default_system_prompt(self) -> str:
        return self.system_prompt

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """Process collections workflow."""
        try:
            action = agent_input.action

            if action == "track_invoice":
                result = await self._track_invoice(agent_input)
            elif action == "send_reminder":
                result = await self._send_reminder(agent_input)
            elif action == "receive_soa":
                result = await self._receive_soa(agent_input)
            elif action == "respond_to_soa":
                result = await self._respond_to_soa(agent_input)
            elif action == "check_overdue":
                result = await self._check_overdue_receivables(agent_input)
            else:
                return self.create_output(
                    success=False,
                    action=action,
                    object_id=agent_input.object_id,
                    object_type="collection",
                    error=f"Unknown action: {action}",
                )

            return result

        except Exception as e:
            logger.error(f"Collections Handler error: {e}")
            return self.create_output(
                success=False,
                action=agent_input.action,
                object_id=agent_input.object_id,
                object_type="collection",
                error=str(e),
            )

    async def _track_invoice(self, agent_input: AgentInput) -> AgentOutput:
        """Track invoice for collections."""
        invoice_number = agent_input.object_id
        context = agent_input.context

        try:
            customer_name = context.get("customer_name")
            invoice_amount = context.get("invoice_amount")
            invoice_date = context.get("invoice_date", datetime.now().isoformat())
            po_number = context.get("po_number")

            if not customer_name or not invoice_amount:
                return self.create_output(
                    success=False,
                    action="track_invoice",
                    object_id=invoice_number,
                    object_type="collection",
                    error="Missing customer_name or invoice_amount",
                )

            # Calculate due date (standard 30 days)
            invoice_dt = datetime.fromisoformat(invoice_date)
            due_date = (invoice_dt + timedelta(days=30)).date().isoformat()

            # Log to database
            if self.db:
                cursor = self.db.cursor()
                cursor.execute(
                    """INSERT INTO collections_tracking
                       (invoice_number, po_number, customer_name, invoice_amount, invoice_date, due_date, payment_status)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        invoice_number,
                        po_number,
                        customer_name,
                        invoice_amount,
                        invoice_date,
                        due_date,
                        "outstanding",
                    ),
                )
                self.db.commit()

            self._log_action(
                action_type="invoice_tracked",
                object_id=invoice_number,
                object_type="collection",
                status="tracked",
                message=f"Invoice {invoice_amount} from {customer_name}, due {due_date}",
            )

            return self.create_output(
                success=True,
                action="track_invoice",
                object_id=invoice_number,
                object_type="collection",
                result={
                    "invoice_number": invoice_number,
                    "customer": customer_name,
                    "amount": invoice_amount,
                    "invoice_date": invoice_date,
                    "due_date": due_date,
                    "status": "outstanding",
                },
            )

        except Exception as e:
            logger.error(f"Error tracking invoice: {e}")
            return self.create_output(
                success=False,
                action="track_invoice",
                object_id=invoice_number,
                object_type="collection",
                error=str(e),
            )

    async def _send_reminder(self, agent_input: AgentInput) -> AgentOutput:
        """Send payment reminder for overdue invoice."""
        invoice_number = agent_input.object_id
        context = agent_input.context

        try:
            customer_email = context.get("customer_email")
            reminder_level = context.get("reminder_level", 1)  # 1=first, 2=second, 3=final

            if not customer_email:
                return self.create_output(
                    success=False,
                    action="send_reminder",
                    object_id=invoice_number,
                    object_type="collection",
                    error="Missing customer_email",
                )

            reminder_number = f"REMINDER-{reminder_level:02d}"

            # Determine escalation level based on reminder
            escalation_needed = False
            escalation_to = None
            escalation_reason = None

            if reminder_level >= 2:
                escalation_needed = True
                escalation_to = "deepak"
                escalation_reason = f"Invoice overdue, reminder {reminder_level} sent"
            if reminder_level >= 3:
                escalation_to = "hamed"
                escalation_reason = f"Invoice overdue 90+ days, final reminder sent"

            # Log reminder
            self._log_action(
                action_type="reminder_sent",
                object_id=invoice_number,
                object_type="collection",
                status="sent",
                message=f"{reminder_number} sent to {customer_email}",
                escalated=escalation_needed,
                assigned_to=escalation_to,
            )

            return self.create_output(
                success=True,
                action="send_reminder",
                object_id=invoice_number,
                object_type="collection",
                result={
                    "invoice_number": invoice_number,
                    "reminder": reminder_number,
                    "sent_to": customer_email,
                    "sent_at": datetime.now().isoformat(),
                    "status": "sent",
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
            return self.create_output(
                success=False,
                action="send_reminder",
                object_id=invoice_number,
                object_type="collection",
                error=str(e),
            )

    async def _receive_soa(self, agent_input: AgentInput) -> AgentOutput:
        """Receive SOA (Statement of Account) from principal."""
        soa_reference = agent_input.object_id
        context = agent_input.context

        try:
            principal_name = context.get("principal_name")
            soa_amount = context.get("soa_amount")
            soa_date = context.get("soa_date", datetime.now().isoformat())

            if not principal_name or not soa_amount:
                return self.create_output(
                    success=False,
                    action="receive_soa",
                    object_id=soa_reference,
                    object_type="payable",
                    error="Missing principal_name or soa_amount",
                )

            # Calculate due date based on principal payment terms
            principal_terms = {
                "autocontrol": 30,
                "kam": 45,
                "terranova": 30,
            }
            payment_days = principal_terms.get(principal_name.lower(), 30)

            soa_dt = datetime.fromisoformat(soa_date)
            due_date = (soa_dt + timedelta(days=payment_days)).date().isoformat()

            # Log to database
            if self.db:
                cursor = self.db.cursor()
                cursor.execute(
                    """INSERT INTO payables_tracking
                       (soa_reference, principal_name, soa_amount, soa_date, due_date, response_status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        soa_reference,
                        principal_name,
                        soa_amount,
                        soa_date,
                        due_date,
                        "pending",
                    ),
                )
                self.db.commit()

            # Create alert for immediate response needed
            self._create_alert(
                alert_type="soa_received",
                severity="critical",
                object_id=soa_reference,
                object_type="payable",
                message=f"SOA from {principal_name} - requires same-day response",
                assigned_to="deepak",
            )

            return self.create_output(
                success=True,
                action="receive_soa",
                object_id=soa_reference,
                object_type="payable",
                result={
                    "soa_reference": soa_reference,
                    "principal": principal_name,
                    "amount": soa_amount,
                    "soa_date": soa_date,
                    "due_date": due_date,
                    "status": "received",
                },
                escalation_needed=True,
                escalation_to="deepak",
                escalation_reason="SOA received - requires same-day response",
            )

        except Exception as e:
            logger.error(f"Error receiving SOA: {e}")
            return self.create_output(
                success=False,
                action="receive_soa",
                object_id=soa_reference,
                object_type="payable",
                error=str(e),
            )

    async def _respond_to_soa(self, agent_input: AgentInput) -> AgentOutput:
        """Respond to SOA with payment commitment."""
        soa_reference = agent_input.object_id
        context = agent_input.context

        try:
            payment_commitment = context.get("payment_commitment", "Acknowledged and payment committed within 30 days")

            # Update database
            if self.db:
                cursor = self.db.cursor()
                cursor.execute(
                    """UPDATE payables_tracking
                       SET ihp_response_date = ?, payment_commitment = ?, response_status = 'acknowledged'
                       WHERE soa_reference = ?""",
                    (datetime.now().isoformat(), payment_commitment, soa_reference),
                )
                self.db.commit()

            self._log_action(
                action_type="soa_acknowledged",
                object_id=soa_reference,
                object_type="payable",
                status="acknowledged",
                message="SOA acknowledged with payment commitment",
            )

            return self.create_output(
                success=True,
                action="respond_to_soa",
                object_id=soa_reference,
                object_type="payable",
                result={
                    "soa_reference": soa_reference,
                    "response_date": datetime.now().isoformat(),
                    "commitment": payment_commitment,
                    "status": "acknowledged",
                },
            )

        except Exception as e:
            logger.error(f"Error responding to SOA: {e}")
            return self.create_output(
                success=False,
                action="respond_to_soa",
                object_id=soa_reference,
                object_type="payable",
                error=str(e),
            )

    async def _check_overdue_receivables(self, agent_input: AgentInput) -> AgentOutput:
        """Check for overdue receivables and create reminders."""
        try:
            if not self.db:
                return self.create_output(
                    success=True,
                    action="check_overdue",
                    object_id="all_invoices",
                    object_type="collection",
                    result={"overdue_invoices": []},
                )

            cursor = self.db.cursor()
            cursor.execute(
                """SELECT invoice_number, customer_name, invoice_amount, due_date, reminder_count
                   FROM collections_tracking
                   WHERE payment_status IN ('outstanding', 'partial')
                   AND due_date < datetime('now')
                   ORDER BY due_date ASC"""
            )

            overdue_invoices = []
            escalations = []

            for row in cursor.fetchall():
                invoice_number = row[0]
                customer_name = row[1]
                invoice_amount = row[2]
                due_date = row[3]
                reminder_count = row[4]

                due_dt = datetime.fromisoformat(due_date)
                days_overdue = (datetime.now() - due_dt).days

                overdue_invoices.append({
                    "invoice_number": invoice_number,
                    "customer": customer_name,
                    "amount": invoice_amount,
                    "days_overdue": days_overdue,
                    "due_date": due_date,
                })

                # Determine escalation
                if days_overdue >= 90:
                    escalations.append({
                        "to": "hamed",
                        "reason": f"Invoice {invoice_number} overdue 90+ days",
                    })
                elif days_overdue >= 60:
                    escalations.append({
                        "to": "deepak",
                        "reason": f"Invoice {invoice_number} overdue 60+ days",
                    })

                # Create alert
                self._create_alert(
                    alert_type="invoice_overdue",
                    severity="yellow" if days_overdue < 60 else "red" if days_overdue < 90 else "critical",
                    object_id=invoice_number,
                    object_type="collection",
                    message=f"Invoice overdue {days_overdue} days",
                    assigned_to="deepak" if days_overdue >= 60 else "general",
                )

            escalation_needed = len(escalations) > 0
            escalation_to = "hamed" if any(e["to"] == "hamed" for e in escalations) else "deepak" if escalation_needed else None

            return self.create_output(
                success=True,
                action="check_overdue",
                object_id="all_invoices",
                object_type="collection",
                result={
                    "overdue_invoices_found": len(overdue_invoices),
                    "overdue_invoices": overdue_invoices,
                    "escalations_needed": len(escalations),
                    "checked_at": datetime.now().isoformat(),
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=f"{len(overdue_invoices)} invoices overdue, {len(escalations)} require escalation",
            )

        except Exception as e:
            logger.error(f"Error checking overdue receivables: {e}")
            return self.create_output(
                success=False,
                action="check_overdue",
                object_id="all_invoices",
                object_type="collection",
                error=str(e),
            )
