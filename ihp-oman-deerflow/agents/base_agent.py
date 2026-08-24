"""
IHP Oman DeerFlow - Base Agent
Common functionality for all specialized agents
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

from pydantic import BaseModel, Field
from anthropic import Anthropic


# Configure logging
logger = logging.getLogger(__name__)


class AgentInput(BaseModel):
    """Base input structure for all agents."""
    object_id: str = Field(..., description="Object identifier (RFQ#, PO#, etc.)")
    object_type: str = Field(..., description="Object type (rfq, quotation, po, etc.)")
    action: str = Field(..., description="Action to perform")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class AgentOutput(BaseModel):
    """Base output structure for all agents."""
    success: bool
    agent_name: str
    action: str
    object_id: str
    object_type: str
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    escalation_needed: bool = False
    escalation_to: Optional[str] = None  # deepak or hamed
    escalation_reason: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class BaseAgent(ABC):
    """
    Abstract base class for all DeerFlow agents.
    Provides common functionality: logging, LLM interaction, escalation.
    """

    def __init__(
        self,
        agent_name: str,
        agent_type: str,
        model: str = "claude-opus-5",
        system_prompt: str = "",
        max_tokens: int = 4096,
        db_connection=None,
    ):
        """
        Initialize base agent.

        Args:
            agent_name: Display name of agent
            agent_type: Type of agent (orchestrator, rfq_handler, etc.)
            model: Claude model to use (opus-5, sonnet-5)
            system_prompt: System prompt for agent
            max_tokens: Maximum tokens for response
            db_connection: SQLite database connection
        """
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.model = model
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.max_tokens = max_tokens
        self.db = db_connection
        self.client = Anthropic()

        logger.info(f"Initialized {agent_name} ({agent_type}) with model {model}")

    @abstractmethod
    def _default_system_prompt(self) -> str:
        """Return default system prompt for this agent."""
        pass

    @abstractmethod
    async def process(self, agent_input: AgentInput) -> AgentOutput:
        """
        Process input and return output.
        Must be implemented by subclass.
        """
        pass

    def _log_action(
        self,
        action_type: str,
        object_id: str,
        object_type: str,
        status: str,
        message: str = "",
        error: str = None,
        escalated: bool = False,
        assigned_to: str = None,
    ):
        """Log agent action to database."""
        if not self.db:
            logger.info(f"Action: {action_type} | {object_id} | {status}")
            return

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """
                INSERT INTO agent_logs
                (agent_name, agent_type, action_type, object_type, object_id,
                 status, message, escalated, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    self.agent_name,
                    self.agent_type,
                    action_type,
                    object_type,
                    object_id,
                    status,
                    message,
                    escalated,
                    assigned_to,
                ),
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to log action: {e}")

    def _create_alert(
        self,
        alert_type: str,
        severity: str,
        object_id: str,
        object_type: str,
        message: str,
        assigned_to: str,
    ):
        """Create an alert in database."""
        if not self.db:
            logger.warning(f"Alert: {alert_type} [{severity}] - {message}")
            return

        try:
            cursor = self.db.cursor()
            cursor.execute(
                """
                INSERT INTO alerts
                (alert_type, severity, object_id, object_type, message, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (alert_type, severity, object_id, object_type, message, assigned_to),
            )
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to create alert: {e}")

    def _call_llm(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Call Claude LLM with given messages and optional tools.

        Args:
            messages: List of messages in conversation
            tools: Optional list of tool definitions

        Returns:
            Response from Claude
        """
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": self.system_prompt,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools

            response = self.client.messages.create(**kwargs)
            return response
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise

    def _extract_text_from_response(self, response) -> str:
        """Extract text content from Claude response."""
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    def _should_escalate(
        self,
        condition: bool,
        escalation_to: str,
        reason: str,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Check if escalation is needed.

        Returns:
            (should_escalate, escalation_to, reason)
        """
        if condition:
            logger.warning(f"Escalation triggered: {escalation_to} - {reason}")
            return True, escalation_to, reason
        return False, None, None

    def create_output(
        self,
        success: bool,
        action: str,
        object_id: str,
        object_type: str,
        result: Dict[str, Any] = None,
        error: str = None,
        escalation_needed: bool = False,
        escalation_to: str = None,
        escalation_reason: str = None,
    ) -> AgentOutput:
        """Create standardized agent output."""
        return AgentOutput(
            success=success,
            agent_name=self.agent_name,
            action=action,
            object_id=object_id,
            object_type=object_type,
            result=result or {},
            error=error,
            escalation_needed=escalation_needed,
            escalation_to=escalation_to,
            escalation_reason=escalation_reason,
        )

    def save_output(self, output: AgentOutput, output_dir: str = ".deer-flow/agent_outputs"):
        """Save agent output to file for audit trail."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = (
            f"{self.agent_name}_{output.object_type}_{output.object_id}_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        filepath = output_dir / filename

        try:
            with open(filepath, "w") as f:
                f.write(output.model_dump_json(indent=2))
            logger.debug(f"Output saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
