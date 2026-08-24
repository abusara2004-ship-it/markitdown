"""
IHP Oman DeerFlow - VDP Tracker Agent
CRITICAL: Vendor Delivery Performance monitoring and recovery
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent, AgentInput, AgentOutput

logger = logging.getLogger(__name__)


class VDPTrackerAgent(BaseAgent):
    """
    VDP Tracker Agent - CRITICAL: Monitors delivery performance for PDO and all operators.

    BUSINESS CONTEXT: PDO has stated "Will reconsider doing business if VDP < 90%"
    Current VDP: 68.96% (21.04% below target)
    This agent's success = company survival
    """

    def __init__(self, db_connection=None):
        system_prompt = """
You are the VDP Tracker Agent - CRITICAL PRIORITY.

EXISTENTIAL BUSINESS CONTEXT:
- PDO states: "Will reconsider doing business if VDP < 90%"
- Current VDP: 68.96% (CRISIS - 21.04% below threshold)
- Target: 90%+ within 6 months
- Failure of this agent = loss of IHP Oman's largest account

CORE RESPONSIBILITIES:
1. Monitor EVERY open PO line's delivery date (daily)
2. Flag delivery slips PROACTIVELY (alert at T-5 days, T-10 days)
3. Calculate rolling 12-month VDP percentage
4. Generate PDO BOT (Back Office Tool) Expediting Reports automatically
5. Alert Deepak on yellow/red delivery slips
6. Escalate to Hamed if VDP trending <75% (existential risk)

VDP CALCULATION:
VDP = (on-time deliveries in past 12 months) / (total deliveries in past 12 months) × 100

ALERT THRESHOLDS:
- Yellow Alert: Delivery slip 5+ days before due date
- Red Alert: Delivery slip 10+ days before due date
- VDP Alert Threshold: <75% (alert Deepak)
- VDP Critical Threshold: <65% (escalate to Hamed - business at risk)

OPERATORS BY PRIORITY:
1. PDO (Petroleum Development Oman) - CRITICAL - 68.96% VDP
2. OQ8/OQ - High priority
3. bp Oman - High priority
4. Shell Oman - High priority
5. Others - Medium/Low priority

BOT REPORT:
- Generate automatically at end of each month
- Calculate 12-month VDP for each operator
- Highlight at-risk operators (VDP <90%)
- Submit to PDO within 5 days of month-end
- Format: Professional summary with trends and recovery actions
"""
        super().__init__(
            agent_name="VDP Tracker",
            agent_type="vdp-tracker",
            model="claude-opus-5",  # Premium model for critical business logic
            system_prompt=system_prompt,
            max_tokens=4096,
            db_connection=db_connection,
        )

    def _default_system_prompt(self) -> str:
        return self.system_prompt

    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """
        Process VDP tracking for a PO or generate daily/monthly reports.
        """
        try:
            action = agent_input.action

            if action == "track_po_delivery":
                result = await self._track_po_delivery(agent_input)
            elif action == "calculate_daily_vdp":
                result = await self._calculate_daily_vdp(agent_input)
            elif action == "generate_bot_report":
                result = await self._generate_bot_report(agent_input)
            elif action == "check_delivery_alerts":
                result = await self._check_delivery_alerts(agent_input)
            else:
                return self.create_output(
                    success=False,
                    action=action,
                    object_id=agent_input.object_id,
                    object_type="po",
                    error=f"Unknown action: {action}",
                )

            return result

        except Exception as e:
            logger.error(f"VDP Tracker error: {e}")
            return self.create_output(
                success=False,
                action=agent_input.action,
                object_id=agent_input.object_id,
                object_type="po",
                error=str(e),
            )

    async def _track_po_delivery(self, agent_input: AgentInput) -> AgentOutput:
        """Track a single PO's delivery status."""
        po_number = agent_input.object_id
        context = agent_input.context

        try:
            promised_delivery = context.get("promised_delivery_date")
            operator_name = context.get("operator_name")

            if not promised_delivery or not operator_name:
                return self.create_output(
                    success=False,
                    action="track_po_delivery",
                    object_id=po_number,
                    object_type="po",
                    error="Missing promised_delivery_date or operator_name",
                )

            # Update PO tracking in database
            await self._update_po_tracking(po_number, promised_delivery, operator_name)

            # Check for delivery alerts
            alerts = await self._check_po_for_alerts(po_number, promised_delivery)

            escalation_needed = False
            escalation_to = None
            escalation_reason = None

            if alerts:
                for alert in alerts:
                    severity = alert["severity"]
                    message = alert["message"]

                    # Create alert in database
                    self._create_alert(
                        alert_type="delivery_slip",
                        severity=severity,
                        object_id=po_number,
                        object_type="po",
                        message=message,
                        assigned_to="deepak" if severity in ["yellow", "red"] else "general",
                    )

                    # Escalate if critical
                    if severity == "red" and operator_name.lower() == "petroleum development oman":
                        escalation_needed = True
                        escalation_to = "deepak"
                        escalation_reason = f"PDO delivery slip: {message}"

            # Log action
            self._log_action(
                action_type="po_delivery_tracked",
                object_id=po_number,
                object_type="po",
                status="tracked",
                message=f"Promised delivery: {promised_delivery}, Alerts: {len(alerts)}",
            )

            return self.create_output(
                success=True,
                action="track_po_delivery",
                object_id=po_number,
                object_type="po",
                result={
                    "po_number": po_number,
                    "operator": operator_name,
                    "promised_delivery": promised_delivery,
                    "alerts": alerts,
                    "status": "on_time" if not alerts else "at_risk",
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error tracking PO delivery: {e}")
            return self.create_output(
                success=False,
                action="track_po_delivery",
                object_id=po_number,
                object_type="po",
                error=str(e),
            )

    async def _calculate_daily_vdp(self, agent_input: AgentInput) -> AgentOutput:
        """Calculate VDP for specified operator or all operators."""
        operator_name = agent_input.context.get("operator_name")

        try:
            if operator_name:
                vdp_data = await self._calculate_operator_vdp(operator_name)
                operators = [vdp_data]
            else:
                operators = await self._calculate_all_operators_vdp()

            escalations = []
            for vdp_data in operators:
                # Check VDP thresholds
                vdp = vdp_data.get("vdp_percentage", 0)
                op_name = vdp_data.get("operator_name")

                if vdp < 75:
                    escalations.append({
                        "operator": op_name,
                        "vdp": vdp,
                        "to": "hamed" if vdp < 65 else "deepak",
                        "reason": f"VDP {vdp}% below critical threshold" if vdp < 65 else f"VDP {vdp}% trending down",
                    })

                # Update database
                await self._update_operator_vdp(vdp_data)

            # Create escalation if needed
            escalation_needed = len(escalations) > 0
            escalation_to = None
            escalation_reason = None

            if escalation_needed:
                critical_ops = [e for e in escalations if e["to"] == "hamed"]
                if critical_ops:
                    escalation_to = "hamed"
                    escalation_reason = f"VDP CRITICAL: {len(critical_ops)} operators below 65%"
                else:
                    escalation_to = "deepak"
                    escalation_reason = f"VDP alert: {len(escalations)} operators below 75%"

            return self.create_output(
                success=True,
                action="calculate_daily_vdp",
                object_id=operator_name or "all_operators",
                object_type="po",
                result={
                    "vdp_data": operators,
                    "escalations": escalations,
                    "calculated_at": datetime.now().isoformat(),
                },
                escalation_needed=escalation_needed,
                escalation_to=escalation_to,
                escalation_reason=escalation_reason,
            )

        except Exception as e:
            logger.error(f"Error calculating VDP: {e}")
            return self.create_output(
                success=False,
                action="calculate_daily_vdp",
                object_id=agent_input.object_id,
                object_type="po",
                error=str(e),
            )

    async def _generate_bot_report(self, agent_input: AgentInput) -> AgentOutput:
        """Generate PDO BOT (Back Office Tool) Expediting Report."""
        try:
            # Collect VDP data for all operators
            vdp_data = await self._calculate_all_operators_vdp()

            # Generate report
            report = {
                "report_date": datetime.now().date().isoformat(),
                "generated_at": datetime.now().isoformat(),
                "report_type": "PDO_BOT_Expediting_Report",
                "operators": vdp_data,
                "summary": await self._generate_report_summary(vdp_data),
            }

            # Save report
            await self._save_bot_report(report)

            # Update database
            if self.db:
                try:
                    cursor = self.db.cursor()
                    cursor.execute(
                        """UPDATE vdp_tracking
                           SET bot_report_submitted_date = ?
                           WHERE operator_name = ?""",
                        (datetime.now().isoformat(), "Petroleum Development Oman"),
                    )
                    self.db.commit()
                except Exception as e:
                    logger.error(f"Error updating report date: {e}")

            return self.create_output(
                success=True,
                action="generate_bot_report",
                object_id="PDO_BOT_Report",
                object_type="report",
                result={
                    "report_type": "PDO BOT Expediting Report",
                    "operators_included": len(vdp_data),
                    "generated_at": datetime.now().isoformat(),
                    "summary": report.get("summary", {}),
                },
            )

        except Exception as e:
            logger.error(f"Error generating BOT report: {e}")
            return self.create_output(
                success=False,
                action="generate_bot_report",
                object_id="PDO_BOT_Report",
                object_type="report",
                error=str(e),
            )

    async def _check_delivery_alerts(self, agent_input: AgentInput) -> AgentOutput:
        """Check for delivery alerts across all open POs."""
        try:
            if not self.db:
                return self.create_output(
                    success=True,
                    action="check_delivery_alerts",
                    object_id="all_pos",
                    object_type="po",
                    result={"alerts": []},
                )

            # Get all open POs approaching delivery date
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT po_number, operator_name, promised_delivery_date
                   FROM po_tracking
                   WHERE delivery_status IN ('open', 'at_risk')
                   AND promised_delivery_date <= datetime('now', '+10 days')
                   ORDER BY promised_delivery_date ASC"""
            )

            alerts = []
            for row in cursor.fetchall():
                po_number = row[0]
                operator = row[1]
                promised_date = row[2]

                alert_data = await self._check_po_for_alerts(po_number, promised_date)
                if alert_data:
                    alerts.extend(alert_data)

            return self.create_output(
                success=True,
                action="check_delivery_alerts",
                object_id="all_pos",
                object_type="po",
                result={
                    "alerts_found": len(alerts),
                    "alerts": alerts,
                    "checked_at": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"Error checking delivery alerts: {e}")
            return self.create_output(
                success=False,
                action="check_delivery_alerts",
                object_id="all_pos",
                object_type="po",
                error=str(e),
            )

    # Helper methods

    async def _update_po_tracking(self, po_number: str, promised_delivery: str, operator_name: str):
        """Update PO tracking in database."""
        if not self.db:
            return

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """UPDATE po_tracking
                   SET promised_delivery_date = ?, updated_at = ?
                   WHERE po_number = ?""",
                (promised_delivery, datetime.now().isoformat(), po_number),
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"Error updating PO tracking: {e}")

    async def _check_po_for_alerts(self, po_number: str, promised_delivery: str) -> List[Dict[str, Any]]:
        """Check if a PO should trigger delivery alerts."""
        try:
            promised_dt = datetime.fromisoformat(promised_delivery)
            now = datetime.now()
            days_until_delivery = (promised_dt - now).days

            alerts = []

            if days_until_delivery < 0:
                # Already late
                days_overdue = abs(days_until_delivery)
                alerts.append({
                    "po_number": po_number,
                    "type": "overdue",
                    "severity": "red",
                    "days_overdue": days_overdue,
                    "message": f"PO OVERDUE by {days_overdue} days",
                })
            elif days_until_delivery <= 5:
                # Within 5 days - yellow alert
                alerts.append({
                    "po_number": po_number,
                    "type": "delivery_slip_yellow",
                    "severity": "yellow",
                    "days_until_delivery": days_until_delivery,
                    "message": f"Delivery due in {days_until_delivery} days",
                })
            elif days_until_delivery <= 10:
                # Within 10 days - red alert
                alerts.append({
                    "po_number": po_number,
                    "type": "delivery_slip_red",
                    "severity": "red",
                    "days_until_delivery": days_until_delivery,
                    "message": f"Delivery due in {days_until_delivery} days - URGENT",
                })

            return alerts

        except Exception as e:
            logger.error(f"Error checking PO alerts: {e}")
            return []

    async def _calculate_operator_vdp(self, operator_name: str) -> Dict[str, Any]:
        """Calculate VDP for a single operator."""
        if not self.db:
            return {"operator_name": operator_name, "vdp_percentage": 0, "total": 0, "on_time": 0}

        try:
            cursor = self.db.cursor()
            # Get POs from past 12 months
            one_year_ago = (datetime.now() - timedelta(days=365)).isoformat()

            cursor.execute(
                """SELECT COUNT(*) as total,
                          SUM(CASE WHEN delivery_status = 'on_time' THEN 1 ELSE 0 END) as on_time
                   FROM po_tracking
                   WHERE operator_name = ?
                   AND actual_delivery_date > ?
                   AND delivery_status IN ('on_time', 'late')""",
                (operator_name, one_year_ago),
            )

            row = cursor.fetchone()
            total = row[0] if row[0] else 0
            on_time = row[1] if row[1] else 0

            vdp = (on_time / total * 100) if total > 0 else 0

            return {
                "operator_name": operator_name,
                "vdp_percentage": round(vdp, 2),
                "total_deliveries_12m": total,
                "on_time_deliveries_12m": on_time,
                "late_deliveries_12m": total - on_time,
                "calculated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating operator VDP: {e}")
            return {"operator_name": operator_name, "vdp_percentage": 0, "error": str(e)}

    async def _calculate_all_operators_vdp(self) -> List[Dict[str, Any]]:
        """Calculate VDP for all operators."""
        if not self.db:
            return []

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT DISTINCT operator_name FROM vdp_tracking")
            operators = [row[0] for row in cursor.fetchall()]

            vdp_data = []
            for operator in operators:
                vdp = await self._calculate_operator_vdp(operator)
                vdp_data.append(vdp)

            return vdp_data

        except Exception as e:
            logger.error(f"Error calculating all operators VDP: {e}")
            return []

    async def _update_operator_vdp(self, vdp_data: Dict[str, Any]):
        """Update operator VDP in database."""
        if not self.db:
            return

        try:
            operator_name = vdp_data.get("operator_name")
            vdp_percentage = vdp_data.get("vdp_percentage", 0)
            total = vdp_data.get("total_deliveries_12m", 0)
            on_time = vdp_data.get("on_time_deliveries_12m", 0)

            # Determine status
            if vdp_percentage < 65:
                status = "critical"
            elif vdp_percentage < 75:
                status = "alert"
            else:
                status = "normal"

            cursor = self.db.cursor()
            cursor.execute(
                """UPDATE vdp_tracking
                   SET vdp_percentage = ?, vdp_status = ?,
                       total_deliveries_12m = ?, on_time_deliveries_12m = ?,
                       last_calculated = ?
                   WHERE operator_name = ?""",
                (vdp_percentage, status, total, on_time, datetime.now().isoformat(), operator_name),
            )
            self.db.commit()

        except Exception as e:
            logger.error(f"Error updating operator VDP: {e}")

    async def _generate_report_summary(self, vdp_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary for BOT report."""
        return {
            "total_operators": len(vdp_data),
            "operators_at_target": sum(1 for v in vdp_data if v.get("vdp_percentage", 0) >= 90),
            "operators_at_risk": sum(1 for v in vdp_data if v.get("vdp_percentage", 0) < 75),
            "average_vdp": round(sum(v.get("vdp_percentage", 0) for v in vdp_data) / len(vdp_data), 2) if vdp_data else 0,
        }

    async def _save_bot_report(self, report: Dict[str, Any]):
        """Save BOT report to file."""
        import json
        from pathlib import Path

        try:
            output_dir = Path(".deer-flow/agent_outputs")
            output_dir.mkdir(parents=True, exist_ok=True)

            filename = f"PDO_BOT_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = output_dir / filename

            with open(filepath, "w") as f:
                json.dump(report, f, indent=2)

            logger.info(f"BOT report saved: {filepath}")

        except Exception as e:
            logger.error(f"Error saving BOT report: {e}")
