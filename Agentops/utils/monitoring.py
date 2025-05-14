"""
Monitoring utilities using AgentOps.
"""
import agentops
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentOpsMonitoring:
    """
    Class to handle AgentOps monitoring for the multi-agent system.
    """

    def __init__(self, api_key: str, project_name: str = "content_creation_agents"):
        """
        Initialize AgentOps monitoring.

        Args:
            api_key: AgentOps API key
            project_name: Name of the project in AgentOps
        """
        self.api_key = api_key
        self.project_name = project_name
        self.session = None
        self.initialized = False

        try:
            # Check if API key is a placeholder
            if api_key == "your_agentops_api_key_here" or not api_key:
                logger.warning("Using placeholder AgentOps API key. Monitoring will be disabled.")
                return

            # Initialize AgentOps with correct parameters
            # Note: AgentOps API might have changed, check the current version's parameters
            agentops.init(api_key=api_key)
            self.initialized = True
            logger.info("AgentOps monitoring initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AgentOps monitoring: {e}")

    def start_session(self, session_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Start a new monitoring session.

        Args:
            session_name: Name of the session
            metadata: Additional metadata for the session
        """
        if not self.initialized:
            logger.warning("AgentOps not initialized, skipping session start")
            return

        try:
            self.session = agentops.start_session(
                session_name=session_name,
                metadata=metadata or {}
            )
            logger.info(f"Started AgentOps session: {session_name}")
        except Exception as e:
            logger.error(f"Failed to start AgentOps session: {e}")

    def log_agent_action(self,
                         agent_name: str,
                         action_type: str,
                         inputs: Dict[str, Any],
                         outputs: Dict[str, Any],
                         metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an agent action to AgentOps.

        Args:
            agent_name: Name of the agent
            action_type: Type of action performed
            inputs: Input data for the action
            outputs: Output data from the action
            metadata: Additional metadata for the action
        """
        if not self.initialized:
            logger.warning("AgentOps not initialized, skipping action logging")
            return

        try:
            agentops.log_agent_action(
                agent_name=agent_name,
                action_type=action_type,
                inputs=inputs,
                outputs=outputs,
                metadata=metadata or {}
            )
            logger.debug(f"Logged action for agent {agent_name}: {action_type}")
        except Exception as e:
            logger.error(f"Failed to log agent action: {e}")

    def end_session(self, status: str = "completed", metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        End the current monitoring session.

        Args:
            status: Status of the session (completed, failed, etc.)
            metadata: Additional metadata for the session end
        """
        if not self.initialized or not self.session:
            logger.warning("No active AgentOps session to end")
            return

        try:
            agentops.end_session(
                status=status,
                metadata=metadata or {}
            )
            logger.info(f"Ended AgentOps session with status: {status}")
            self.session = None
        except Exception as e:
            logger.error(f"Failed to end AgentOps session: {e}")
