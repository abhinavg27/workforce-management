import threading
from contextlib import contextmanager

import google.generativeai as genai
import json
import logging
from datetime import datetime
import os
import sqlite3
import pickle
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict
import traceback
from datetime import datetime, timedelta  # Add timedelta import
from threading import RLock
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from utils.confluence_client import ConfluenceClient
from utils.universal_llm_generator import UniversalLLMGenerator

logger = logging.getLogger(__name__)


@dataclass
class Interaction:
    """Represents a user interaction"""
    timestamp: datetime
    operation_type: str
    template_used: str
    user_input: Dict
    generated_content: str
    user_feedback: Optional[Dict] = None
    success: bool = True


@dataclass
class UserPreference:
    """User preferences and patterns"""
    user_id: str
    preferred_templates: Dict[str, int]  # template -> usage_count
    common_operations: List[str]
    feedback_patterns: Dict[str, float]  # aspect -> average_rating
    last_updated: datetime
    default_space: Optional[str] = None  # Add default_space field


class ConfluenceAIAgent:
    """Complete AI Agent for Confluence Page Generation"""

    #def __init__(self):
        #self.llm_generator = UniversalLLMGenerator(api_key=os.getenv('GOOGLE_API_KEY'))
        #self.confluence_client = ConfluenceClient(
            #url=os.getenv('CONFLUENCE_URL', 'https://confluence.rakuten-it.com/confluence'),
            #username=os.getenv('CONFLUENCE_USERNAME'),
            #password=os.getenv('CONFLUENCE_PASSWORD')
        #)
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name

        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            self.enabled = True
        else:
            self.model = None
            self.enabled = False

        # Initialize agent components
        self.memory = AgentMemory()
        self.learner = AgentLearner()
        self.planner = AgentPlanner(self.model)
        self.adapter = AgentAdapter()

        self.llm_generator = UniversalLLMGenerator(api_key=api_key, model_name=model_name)
        self.confluence_client = ConfluenceClient(
            url=os.getenv('CONFLUENCE_URL', 'https://confluence.rakuten-it.com/confluence'),
            username=os.getenv('CONFLUENCE_USERNAME'),
            password=os.getenv('CONFLUENCE_PASSWORD')
        )

        # Conversation context
        self.conversation_history = []
        self.current_session = {
            'start_time': datetime.now(),
            'interactions': [],
            'context': {}
        }

        logger.info("🤖 Complete AI Agent initialized with learning, memory, and planning capabilities")

    def __del__(self):
        """Cleanup resources when agent is destroyed"""
        self.memory.close_all_connections()
        logger.info("🧠 Closed all database connections")

    def process_request(self, user_input: Dict, user_id: str = "default") -> Dict:
        start_time = datetime.now()
        logger.debug(f"🤖 Entering process_request for user {user_id}, input keys: {list(user_input.keys())}")

        # Validate user_input
        if not user_input or not isinstance(user_input, dict):
            logger.error("🤖 Invalid user_input: expected non-empty dictionary")
            return self._handle_failure(user_input or {}, "Invalid user input")

        try:
            # 1. 🧠 Analyze user intent and context
            logger.debug("🤖 Starting intent analysis")
            intent_analysis = self._analyze_user_intent(user_input, user_id)
            if not intent_analysis:
                logger.error("🤖 Intent analysis returned None")
                return self._handle_failure(user_input, "Intent analysis failed")
            logger.debug(f"🤖 Intent analysis completed in {(datetime.now() - start_time).total_seconds():.2f}s")

            # 2. 📋 Create execution plan
            logger.debug("🤖 Starting plan creation")
            execution_plan = self.planner.create_plan(intent_analysis, user_input)
            if not execution_plan:
                logger.error("🤖 Execution plan returned None")
                return self._handle_failure(user_input, "Planning failed")
            logger.debug(f"🤖 Plan creation completed in {(datetime.now() - start_time).total_seconds():.2f}s")

            # 3. 🎯 Execute plan with learning
            logger.debug("🤖 Starting plan execution")
            result = self._execute_plan(execution_plan, user_input, user_id)
            if not result:
                logger.error("🤖 Plan execution returned None")
                return self._handle_failure(user_input, "Execution failed")
            logger.debug(f"🤖 Plan execution completed in {(datetime.now() - start_time).total_seconds():.2f}s")

            # 4. 💾 Store interaction for learning
            logger.debug("🤖 Storing interaction")
            interaction = Interaction(
                timestamp=datetime.now(),
                operation_type=user_input.get('operation_type', 'unknown'),
                template_used=execution_plan.get('template_selected', 'unknown'),
                user_input=user_input,
                generated_content=result.get('content', ''),
                success=result.get('success', False)
            )
            logger.debug(f"🤖 Interaction created: {interaction}")
            if not self.memory.store_interaction(interaction, user_id):
                logger.warning("🤖 Failed to store interaction, continuing with response")
                result['warnings'] = result.get('warnings', []) + ["Failed to store interaction in database"]
            self.conversation_history.append(interaction)
            logger.debug(f"🤖 Interaction processed in {(datetime.now() - start_time).total_seconds():.2f}s")

            # 5. 🔄 Learn and adapt
            logger.debug("🤖 Starting learning phase")
            self._learn_from_interaction(interaction, user_id)
            logger.debug(f"🤖 Learning phase completed in {(datetime.now() - start_time).total_seconds():.2f}s")

            result['status'] = 'completed'
            logger.info(f"🤖 Request processing completed in {(datetime.now() - start_time).total_seconds():.2f}s")
            return result

        except Exception as e:
            logger.error(f"🤖 AI Agent processing failed: {e}\n{traceback.format_exc()}")
            return self._handle_failure(user_input, str(e))
        finally:
            self.memory.close_all_connections()
            logger.info("🧠 Cleaned up resources after request processing")

    def _analyze_user_intent(self, user_input: Dict, user_id: str) -> Dict:
        """🧠 Analyze user intent with context and history"""
        start_time = datetime.now()
        logger.info(f"🧠 Analyzing intent for user {user_id}, input: {user_input}")

        if not user_input:
            logger.warning("🧠 Empty user_input, returning default intent analysis")
            return {
                "primary_intent": "unknown",
                "confidence": 0.5,
                "user_expertise": "intermediate",
                "complexity": "moderate",
                "context_factors": [],
                "recommendations": []
            }

        if not self.model or not self.enabled:
            logger.warning("🧠 Model not available, using fallback intent analysis")
            return {
                "primary_intent": user_input.get('operation_type', 'unknown'),
                "confidence": 0.5,
                "user_expertise": "intermediate",
                "complexity": "moderate",
                "context_factors": [],
                "recommendations": ["Ensure model is configured"]
            }

        try:
            logger.info("🧠 Fetching user preferences")
            user_prefs = self.memory.get_user_preferences(user_id) or UserPreference(
                user_id=user_id, preferred_templates={}, common_operations=[], feedback_patterns={}, last_updated=datetime.now()
            )
            logger.info("🧠 Fetching recent interactions{user_prefs}")
            recent_interactions = self.memory.get_recent_interactions(user_id, limit=5) or []

            common_operations = user_prefs.common_operations
            feedback_patterns = user_prefs.feedback_patterns

            context_prompt = f"""Analyze user intent with full context awareness.
    USER INPUT: {json.dumps(user_input, indent=2)}
    USER HISTORY:
    - Preferred operations: {common_operations}
    - Recent interactions: {len(recent_interactions)} in last sessions
    - Feedback patterns: {feedback_patterns}
    CONVERSATION CONTEXT:
    {json.dumps([{'type': i.operation_type, 'success': i.success} for i in self.conversation_history[-3:]], indent=2)}
    ANALYZE:
    1. Primary intent (operation type, urgency, complexity)
    2. Context clues (similar to previous requests?)
    3. User expertise level (based on history)
    4. Potential challenges (based on past failures)
    5. Recommended approach
    Return JSON:
    {{
      "primary_intent": "operation_type",
      "confidence": 0.95,
      "user_expertise": "beginner|intermediate|expert",
      "complexity": "simple|moderate|complex",
      "context_factors": ["factor1", "factor2"],
      "recommendations": ["rec1", "rec2"]
    }}"""

            logger.info("🧠 Sending prompt to LLM")
            response = self.model.generate_content(context_prompt)
            if not response or not hasattr(response, 'text') or not response.text:
                logger.error("🧠 Model response is None or empty, retrying with simplified prompt")
                simplified_prompt = f"Analyze intent: {json.dumps(user_input)}"
                response = self.model.generate_content(simplified_prompt)
                if not response or not hasattr(response, 'text') or not response.text:
                    raise ValueError("Empty model response after retry")

            intent_analysis = json.loads(self._clean_json_response(response.text))
            logger.info(f"🧠 Intent analysis completed: {intent_analysis.get('primary_intent')} (confidence: {intent_analysis.get('confidence')}) in {(datetime.now() - start_time).total_seconds():.2f}s")
            return intent_analysis

        except json.JSONDecodeError as e:
            logger.error(f"🧠 JSON parsing failed: {e}\n{traceback.format_exc()}")
            return {
                "primary_intent": user_input.get('operation_type', 'unknown'),
                "confidence": 0.5,
                "user_expertise": "intermediate",
                "complexity": "moderate",
                "context_factors": [],
                "recommendations": ["Check input format"]
            }
        except Exception as e:
            logger.error(f"🧠 Intent analysis failed: {e}\n{traceback.format_exc()}")
            return {
                "primary_intent": user_input.get('operation_type', 'unknown'),
                "confidence": 0.5,
                "user_expertise": "intermediate",
                "complexity": "moderate",
                "context_factors": [],
                "recommendations": ["Retry with valid input"]
            }

    def _execute_plan_old(self, execution_plan: Dict, user_input: Dict, user_id: str) -> Dict:
        start_time = datetime.now()
        logger.debug(f"🎯 Entering _execute_plan for user {user_id}, steps: {execution_plan.get('execution_steps', [])}")

        if not execution_plan:
            logger.error("🎯 Execution plan is None")
            return self._handle_failure(user_input, "Execution plan is None")

        try:
            from .universal_llm_generator import UniversalLLMGenerator
            from .confluence_client import ConfluenceClient  # Your mock client

            generator = UniversalLLMGenerator(self.api_key, self.model_name)
            logger.debug(f"🎯 Initialized UniversalLLMGenerator with {len(execution_plan.get('execution_steps', []))} steps")

            enhanced_input = {
                **user_input,
                'agent_context': {
                    'execution_plan': execution_plan,
                    'user_expertise': execution_plan.get('user_expertise', 'intermediate'),
                    'recommendations': execution_plan.get('recommendations', [])
                }
            }

            template_data = enhanced_input.get('template_data', {})
            operation_date = enhanced_input.get('operation_date')
            display_date = enhanced_input.get('display_date')
            operation_type = enhanced_input.get('operation_type')

            if template_data and isinstance(template_data, dict) and 'title' in template_data:
                title_template = template_data['title']
                if operation_date:
                    title_template = title_template.replace('{operation_date}', operation_date)
                timestamp = datetime.now().strftime("%H%M%S")[:12]
                enhanced_title = f"{title_template}_{timestamp}"
                logger.debug(f"🏷️ Enhanced title: {enhanced_title}")

                enhanced_template_data = template_data.copy()
                enhanced_template_data['title'] = enhanced_title
                enhanced_input['template_data'] = enhanced_template_data

            logger.debug("🎯 Starting UniversalLLMGenerator.generate_confluence_page")
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        generator.generate_confluence_page,
                        enhanced_input.get('template_data'),
                        operation_date,
                        display_date,
                        operation_type,
                        execution_plan.get('execution_steps', [])
                    )
                    result = future.result(timeout=60)
            except TimeoutError:
                logger.error("🎯 API call timed out after 60 seconds")
                return self._handle_failure(user_input, "API call timeout")
            except Exception as e:
                logger.error(f"🎯 UniversalLLMGenerator failed: {e}\n{traceback.format_exc()}")
                raise ValueError(f"UniversalLLMGenerator error: {str(e)}")

            if not result:
                raise ValueError("Generator returned None")

            if isinstance(result, tuple) and len(result) >= 4:
                title, content, space_key, parent_page_id = result[:4]
            else:
                raise ValueError(f"Unexpected result format: {type(result)}")

            logger.info(f"🎯 Generated page title: {title}, space: {space_key}, parent ID: {parent_page_id} in {(datetime.now() - start_time).total_seconds():.2f}s")

            # Initialize mock ConfluenceClient
            confluence_client = ConfluenceClient(
                url="https://confluence.rakuten-it.com/confluence",
                username=None,  # Mock mode, no auth needed
                password=None
            )
            page_result = confluence_client.create_page(
                space_key=space_key,
                title=title,
                content=content,
                parent_id=parent_page_id
            )

            # Store page creation event
            page_data = {
                'user_id': user_id,
                'operation_type': operation_type,
                'template_file': execution_plan.get('template_selected', 'unknown'),
                'page_title': title,
                'page_id': page_result.get('page_id', ''),
                'page_url': page_result.get('page_url', ''),
                'space_key': space_key,
                'parent_page_id': parent_page_id,
                'success': page_result.get('success', False),
                'error_message': page_result.get('error', ''),
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'source': 'ai_agent',
                'ai_agent_used': True,
                'mock_mode': page_result.get('mock_mode', False)
            }
            if not self.memory.store_page_creation(user_id, page_data):
                logger.warning("🖌️ Failed to store page creation, continuing with response")
                page_result['warnings'] = page_result.get('warnings', []) + ["Failed to store page creation event"]

            if not page_result.get('success'):
                logger.error(f"🎯 Failed to create Confluence page: {page_result.get('error')}")
                return self._handle_failure(user_input, f"Page creation failed: {page_result.get('error')}")

            return {
                'success': True,
                'status': 'completed',
                'title': title,
                'content': content,
                'space_key': space_key,
                'parent_page_id': parent_page_id,
                'page_id': page_result.get('page_id'),
                'page_url': page_result.get('page_url'),
                'operation_type': operation_type,
                'execution_plan': execution_plan,
                'agent_insights': self._generate_insights(execution_plan, user_input),
                'warnings': page_result.get('warnings', []),
                'mock_mode': page_result.get('mock_mode', False)
            }

        except ImportError as e:
            logger.error(f"🎯 Import error: {e}\n{traceback.format_exc()}")
            return self._handle_failure(user_input, f"Import error: {str(e)}")
        except Exception as e:
            logger.error(f"🎯 Plan execution failed: {e}\n{traceback.format_exc()}")
            return self._handle_failure(user_input, str(e))
        finally:
            logger.debug(f"🎯 Exiting _execute_plan in {(datetime.now() - start_time).total_seconds():.2f}s")

    # In ai_agent.py, within ConfluenceAIAgent
    def _execute_plan(self, execution_plan: Dict, user_input: Dict, user_id: str) -> Dict:
        start_time = datetime.now()
        logger.debug(f"🎯 Entering _execute_plan for user {user_id}, steps: {execution_plan.get('execution_steps', [])}")

        if not execution_plan:
            logger.error("🎯 Execution plan is None")
            return self._handle_failure(user_input, "Execution plan is None")

        try:
            from .universal_llm_generator import UniversalLLMGenerator
            from .confluence_client import ConfluenceClient
            import os

            generator = UniversalLLMGenerator(self.api_key, self.model_name)
            logger.debug(f"🎯 Initialized UniversalLLMGenerator with {len(execution_plan.get('execution_steps', []))} steps")

            enhanced_input = {
                **user_input,
                'agent_context': {
                    'execution_plan': execution_plan,
                    'user_expertise': execution_plan.get('user_expertise', 'intermediate'),
                    'recommendations': execution_plan.get('recommendations', [])
                }
            }

            template_data = enhanced_input.get('template_data', {})
            operation_date = enhanced_input.get('operation_date')
            display_date = enhanced_input.get('display_date')
            operation_type = enhanced_input.get('operation_type')

            if template_data and isinstance(template_data, dict) and 'title' in template_data:
                title_template = template_data['title']
                if operation_date:
                    title_template = title_template.replace('{operation_date}', operation_date)
                timestamp = datetime.now().strftime("%H%M%S_%f")[:12]
                enhanced_title = f"{title_template}_{timestamp}"
                logger.debug(f"🏷️ Enhanced title: {enhanced_title}")

                enhanced_template_data = template_data.copy()
                enhanced_template_data['title'] = enhanced_title
                enhanced_input['template_data'] = enhanced_template_data

            logger.debug("🎯 Starting UniversalLLMGenerator.generate_confluence_page")
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        generator.generate_confluence_page,
                        enhanced_input.get('template_data'),
                        operation_date,
                        display_date,
                        operation_type
                    )
                    result = future.result(timeout=60)
            except TimeoutError:
                logger.error("🎯 API call timed out after 60 seconds")
                return self._handle_failure(user_input, "API call timeout")
            except Exception as e:
                logger.error(f"🎯 UniversalLLMGenerator failed: {e}\n{traceback.format_exc()}")
                raise ValueError(f"UniversalLLMGenerator error: {str(e)}")

            if not result:
                raise ValueError("Generator returned None")

            if isinstance(result, tuple) and len(result) >= 4:
                title, content, space_key, parent_page_id = result[:4]
            else:
                raise ValueError(f"Unexpected result format: {type(result)}")

            logger.info(f"🎯 Generated page title: {title}, space: {space_key}, parent ID: {parent_page_id} in {(datetime.now() - start_time).total_seconds():.2f}s")

            # Initialize real ConfluenceClient with credentials
            confluence_client = ConfluenceClient(
                url="https://confluence.rakuten-it.com/confluence",
                username=os.getenv("CONFLUENCE_USERNAME"),
                password=os.getenv("CONFLUENCE_PASSWORD")
            )
            page_result = confluence_client.create_page(
                space_key=space_key,
                title=title,
                content=content,
                parent_id=parent_page_id
            )

            # Store page creation event
            page_data = {
                'user_id': user_id,
                'operation_type': operation_type,
                'template_file': execution_plan.get('template_selected', 'unknown'),
                'page_title': title,
                'page_id': page_result.get('page_id', ''),
                'page_url': page_result.get('page_url', ''),
                'space_key': space_key,
                'parent_page_id': parent_page_id,
                'success': page_result.get('success', False),
                'error_message': page_result.get('error', ''),
                'generation_time_seconds': (datetime.now() - start_time).total_seconds(),
                'source': 'ai_agent',
                'ai_agent_used': True,
                'mock_mode': page_result.get('mock_mode', False)
            }
            if not self.memory.store_page_creation(user_id, page_data):
                logger.warning("🖌️ Failed to store page creation, continuing with response")
                page_result['warnings'] = page_result.get('warnings', []) + ["Failed to store page creation event"]

            if not page_result.get('success'):
                logger.error(f"🎯 Failed to create Confluence page: {page_result.get('error')}")
                return self._handle_failure(user_input, f"Page creation failed: {page_result.get('error')}")

            return {
                'success': True,
                'status': 'completed',
                'title': title,
                'content': content,
                'space_key': space_key,
                'parent_page_id': parent_page_id,
                'page_id': page_result.get('page_id'),
                'page_url': page_result.get('page_url'),
                'execution_plan': execution_plan,
                'agent_insights': self._generate_insights(execution_plan, user_input),
                'warnings': page_result.get('warnings', []),
                'mock_mode': page_result.get('mock_mode', False)
            }

        except ImportError as e:
            logger.error(f"🎯 Import error: {e}\n{traceback.format_exc()}")
            return self._handle_failure(user_input, f"Import error: {str(e)}")
        except Exception as e:
            logger.error(f"🎯 Plan execution failed: {e}\n{traceback.format_exc()}")
            return self._handle_failure(user_input, str(e))
        finally:
            logger.debug(f"🎯 Exiting _execute_plan in {(datetime.now() - start_time).total_seconds():.2f}s")

    def _learn_from_interaction(self, interaction: Interaction, user_id: str):
        """🔄 Learn and adapt from interaction"""

        if not interaction:
            logger.warning("🔄 Interaction is None, skipping learning")
            return

        try:
            # Update user preferences
            self.learner.update_preferences(interaction, user_id)

            # Learn from patterns
            if interaction.success:
                self.learner.reinforce_successful_pattern(interaction)
            else:
                self.learner.learn_from_failure(interaction)

            # Adapt templates if needed
            self.adapter.consider_template_adaptation(interaction)
        except Exception as e:
            logger.error(f"🔄 Learning from interaction failed: {e}")

    def _generate_insights(self, execution_plan: Dict, user_input: Dict) -> Dict:
        """🔍 Generate insights about the operation"""

        if not execution_plan:
            execution_plan = {}
        if not user_input:
            user_input = {}

        return {
            'complexity_assessment': execution_plan.get('complexity', 'moderate'),
            'success_probability': self._calculate_success_probability(execution_plan),
            'optimization_suggestions': self._get_optimization_suggestions(execution_plan),
            'learning_opportunities': self._identify_learning_opportunities(user_input)
        }

    def _calculate_success_probability(self, execution_plan: Dict) -> float:
        """Calculate success probability based on execution plan and historical data"""
        if not execution_plan:
            logger.warning("🔍 Empty execution plan, using default probability")
            return 0.7

        try:
            # Base probability from plan
            base_prob = execution_plan.get('success_probability', 0.7)

            # Adjust based on historical success rate for operation type
            operation_type = execution_plan.get('operation_type', 'unknown')
            patterns = self.memory.get_usage_patterns(execution_plan.get('user_id', 'default'))
            op_stats = patterns.get(operation_type, {'success_rate': 0.7})

            # Combine base probability with historical success rate
            historical_weight = 0.4
            adjusted_prob = (1 - historical_weight) * base_prob + historical_weight * op_stats['success_rate']

            # Apply bonuses for optimizations
            optimizations = execution_plan.get('optimization_strategies', [])
            if "automated_template" in optimizations:
                adjusted_prob += 0.1
            if "workflow_integration" in optimizations:
                adjusted_prob += 0.05

            # Apply penalties for risks
            risks = execution_plan.get('risk_factors', [])
            if "template_complexity" in risks:
                adjusted_prob -= 0.05

            return min(max(adjusted_prob, 0.1), 0.99)  # Bound between 0.1 and 0.99
        except Exception as e:
            logger.error(f"🔍 Failed to calculate success probability: {e}")
            return 0.7

    def _get_optimization_suggestions(self, execution_plan: Dict) -> List[str]:
        """Get optimization suggestions"""
        if not execution_plan:
            return ["Use detailed input data", "Verify template format"]
        return execution_plan.get('optimization_strategies', [])

    def _identify_learning_opportunities(self, user_input: Dict) -> List[str]:
        """Identify learning opportunities"""
        if not user_input:
            return []
        return ["Template customization", "Operation efficiency"]

    def _get_operation_suggestions(self, user_prefs: Optional[UserPreference], recent_patterns: Any) -> List[str]:
        """Get operation suggestions"""
        if user_prefs and user_prefs.common_operations:
            return user_prefs.common_operations[:3]
        return ["create_page", "update_content", "generate_report"]

    def _get_workflow_suggestions(self, recent_patterns: Any) -> List[str]:
        """Get workflow suggestions"""
        return ["Batch similar operations", "Use templates for consistency", "Review generated content"]

    def _clean_json_response(self, response_text: str) -> str:
        """Clean LLM JSON response"""
        if not response_text:
            return "{}"

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith('```'):
                lines = lines[:-1]
            response_text = '\n'.join(lines)

        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx >= 0 and end_idx >= 0:
            response_text = response_text[start_idx:end_idx + 1]
        else:
            return "{}"

        return response_text.strip()

    def _handle_failure(self, user_input: Dict, error: str) -> Dict:
        """Handle agent failures gracefully"""
        logger.error(f"🤖 Agent failure: {error}")
        return {
            'success': False,
            'error': error,
            'fallback_used': True,
            'recommendations': ['Try again with simpler input', 'Check template format', 'Contact support'],
            'debug_info': {
                'user_input_keys': list(user_input.keys()) if user_input else [],
                'error_type': type(error).__name__,
                'timestamp': datetime.now().isoformat(),
                'stack_trace': traceback.format_exc()
            }
        }

    def provide_feedback(self, interaction_id: str, feedback: Dict, user_id: str = "default"):
        """📝 Process user feedback for learning"""

        if not feedback or not isinstance(feedback, dict):
            logger.error("📝 Invalid feedback provided")
            return

        try:
            # Store feedback
            self.memory.store_feedback(interaction_id, feedback, user_id)

            # Learn from feedback
            self.learner.learn_from_feedback(feedback, user_id)

            # Adapt based on feedback
            self.adapter.adapt_from_feedback(feedback)

            logger.info(f"📝 Processed feedback for interaction {interaction_id}")

        except Exception as e:
            logger.error(f"📝 Feedback processing failed: {e}")

    def get_recommendations(self, user_id: str = "default") -> Dict:
        """💡 Provide intelligent recommendations"""

        try:
            user_prefs = self.memory.get_user_preferences(user_id)
            recent_patterns = self.memory.get_usage_patterns(user_id)

            recommendations = {
                'suggested_operations': self._get_operation_suggestions(user_prefs, recent_patterns),
                'template_improvements': self.adapter.get_template_suggestions(user_id),
                'workflow_optimizations': self._get_workflow_suggestions(recent_patterns),
                'learning_insights': self.learner.get_insights(user_id)
            }

            return recommendations
        except Exception as e:
            logger.error(f"💡 Failed to get recommendations: {e}")
            return {
                'suggested_operations': [],
                'template_improvements': [],
                'workflow_optimizations': [],
                'learning_insights': {}
            }


class AgentMemory:
    """🧠 Agent memory system with enhanced feedback storage"""

    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self._lock = RLock()
        self._conn_pool = {}
        self._init_database()
        self._migrate_database()  # Added migration step

    @contextmanager
    def _get_connection(self):
        thread_id = threading.get_ident()
        with self._lock:
            if thread_id not in self._conn_pool:
                conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
                conn.execute('PRAGMA journal_mode=WAL')
                self._conn_pool[thread_id] = conn
            conn = self._conn_pool[thread_id]
            try:
                yield conn
            except Exception as e:
                logger.error(f"🧠 Database connection error: {e}\n{traceback.format_exc()}")
                raise
            finally:
                if 'conn' in locals():
                    conn.commit()

    def close_all_connections(self):
        with self._lock:
            for conn in self._conn_pool.values():
                conn.commit()
                conn.close()
            self._conn_pool.clear()
            logger.debug("🧠 All database connections closed")
    def _init_database(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute('PRAGMA journal_mode=WAL')
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    timestamp TEXT,
                    operation_type TEXT,
                    template_used TEXT,
                    user_input TEXT,
                    generated_content TEXT,
                    success BOOLEAN,
                    feedback TEXT,
                    execution_time REAL,
                    source TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    preferences TEXT,
                    last_updated TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    interaction_id TEXT,
                    user_id TEXT,
                    user_name TEXT,
                    user_email TEXT,
                    rating INTEGER,
                    content_quality INTEGER,
                    formatting INTEGER,
                    accuracy INTEGER,
                    completeness INTEGER,
                    comments TEXT,
                    feature_requests TEXT,
                    contact_me BOOLEAN,
                    timestamp TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    page_title TEXT,
                    operation_type TEXT
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    session_id TEXT,
                    user_name TEXT,
                    user_email TEXT,
                    start_time TEXT,
                    last_activity TEXT,
                    pages_generated INTEGER DEFAULT 0,
                    feedback_given INTEGER DEFAULT 0
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS page_creations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    operation_type TEXT,
                    template_file TEXT,
                    page_title TEXT,
                    page_id TEXT,
                    page_url TEXT,
                    space_key TEXT,
                    parent_page_id TEXT,
                    success BOOLEAN,
                    error_message TEXT,
                    generation_time_seconds REAL,
                    timestamp TEXT,
                    source TEXT,
                    ai_agent_used BOOLEAN DEFAULT 1
                )
            ''')

            conn.commit()
            logger.info("🧠 Database initialized with updated schema")
        except sqlite3.Error as e:
            logger.error(f"🧠 Database initialization failed: {e}\n{traceback.format_exc()}")
            raise RuntimeError("Failed to initialize database")
        finally:
            if 'conn' in locals():
                conn.close()

    def _migrate_database(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(interactions)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'execution_time' not in columns:
                logger.info("🧠 Migrating interactions table to add execution_time column")
                cursor.execute('''
                    ALTER TABLE interactions
                    ADD COLUMN execution_time REAL DEFAULT 0.0
                ''')

            if 'source' not in columns:
                logger.info("🧠 Migrating interactions table to add source column")
                cursor.execute('''
                    ALTER TABLE interactions
                    ADD COLUMN source TEXT DEFAULT 'ai_agent'
                ''')

            conn.commit()
            logger.info("🧠 Database migration completed successfully")
        except sqlite3.Error as e:
            logger.error(f"🧠 Database migration failed: {e}\n{traceback.format_exc()}")
        finally:
            if 'conn' in locals():
                conn.close()

    def store_feedback(self, interaction_id: str, feedback: Dict, user_id: str):
        if not feedback or not isinstance(feedback, dict):
            logger.warning("🧠 Invalid feedback, skipping storage")
            return

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                user_name = feedback.get('user_name', f'User_{user_id}')
                user_email = feedback.get('user_email', '')
                aspects = feedback.get('aspects', {})

                cursor.execute('''
                    INSERT INTO feedback 
                    (interaction_id, user_id, user_name, user_email, rating, 
                     content_quality, formatting, accuracy, completeness, 
                     comments, feature_requests, contact_me, timestamp, 
                     user_agent, ip_address, page_title, operation_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction_id,
                    user_id,
                    user_name,
                    user_email,
                    feedback.get('rating', 3),
                    aspects.get('content_quality', 3),
                    aspects.get('formatting', 3),
                    aspects.get('accuracy', 3),
                    aspects.get('completeness', 3),
                    feedback.get('comments', ''),
                    feedback.get('feature_requests', ''),
                    feedback.get('contact_me', False),
                    datetime.now().isoformat(),
                    feedback.get('user_agent', ''),
                    feedback.get('ip_address', ''),
                    feedback.get('page_title', ''),
                    feedback.get('operation_type', '')
                ))

                cursor.execute('''
                    UPDATE interactions 
                    SET feedback = ? 
                    WHERE id = ? AND user_id = ?
                ''', (json.dumps(feedback), interaction_id, user_id))

                conn.commit()
                logger.debug(f"🧠 Feedback stored for user {user_name} (ID: {user_id})")
        except sqlite3.Error as e:
            logger.error(f"🧠 Failed to store feedback: {e}\n{traceback.format_exc()}")

    def get_recent_feedback(self, limit: int = 10) -> List[Dict]:
        """Get recent feedback with user information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, interaction_id, user_id, user_name, user_email, 
                       rating, content_quality, formatting, accuracy, completeness,
                       comments, feature_requests, contact_me, timestamp,
                       user_agent, ip_address, page_title, operation_type
                FROM feedback 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))

            results = cursor.fetchall()
            conn.close()

            feedback_list = []
            for row in results:
                feedback_list.append({
                    'id': row[0],
                    'interaction_id': row[1],
                    'user_id': row[2],
                    'user_name': row[3],
                    'user_email': row[4],
                    'rating': row[5],
                    'aspects': {
                        'content_quality': row[6],
                        'formatting': row[7],
                        'accuracy': row[8],
                        'completeness': row[9]
                    },
                    'comments': row[10],
                    'feature_requests': row[11],
                    'contact_me': row[12],
                    'timestamp': row[13],
                    'user_agent': row[14],
                    'ip_address': row[15],
                    'page_title': row[16],
                    'operation_type': row[17],
                    'time_ago': self._calculate_time_ago(row[13])
                })

            return feedback_list
        except Exception as e:
            logger.error(f"🧠 Failed to get recent feedback: {e}")
            return []

    def get_feedback_statistics(self) -> Dict:
        """Get feedback statistics and analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Overall statistics
            cursor.execute('SELECT COUNT(*), AVG(rating), AVG(content_quality), AVG(formatting), AVG(accuracy), AVG(completeness) FROM feedback')
            stats = cursor.fetchone()

            # Rating distribution
            cursor.execute('SELECT rating, COUNT(*) FROM feedback GROUP BY rating ORDER BY rating')
            rating_distribution = dict(cursor.fetchall())

            # Recent feedback count (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('SELECT COUNT(*) FROM feedback WHERE timestamp > ?', (week_ago,))
            recent_count = cursor.fetchone()[0]

            # Top feedback providers
            cursor.execute('''
                SELECT user_name, user_id, COUNT(*) as feedback_count, AVG(rating) as avg_rating
                FROM feedback 
                GROUP BY user_id, user_name 
                ORDER BY feedback_count DESC 
                LIMIT 5
            ''')
            top_providers = cursor.fetchall()

            conn.close()

            return {
                'total_feedback': stats[0] or 0,
                'average_rating': round(stats[1] or 0, 2),
                'average_content_quality': round(stats[2] or 0, 2),
                'average_formatting': round(stats[3] or 0, 2),
                'average_accuracy': round(stats[4] or 0, 2),
                'average_completeness': round(stats[5] or 0, 2),
                'rating_distribution': rating_distribution,
                'recent_feedback_count': recent_count,
                'top_feedback_providers': [
                    {
                        'user_name': row[0],
                        'user_id': row[1],
                        'feedback_count': row[2],
                        'average_rating': round(row[3], 2)
                    } for row in top_providers
                ],
                'satisfaction_rate': round((sum(k * v for k, v in rating_distribution.items() if k >= 4) / max(sum(rating_distribution.values()), 1)) * 100, 1)
            }
        except Exception as e:
            logger.error(f"🧠 Failed to get feedback statistics: {e}")
            return {}

    def _calculate_time_ago(self, timestamp_str: str) -> str:
        """Calculate human-readable time ago"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - timestamp

            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            else:
                return "Just now"
        except:
            return "Unknown"

    def store_interaction(self, interaction_or_user_id, user_id_or_data=None):
        with self._lock:
            try:
                with self._get_connection() as conn:
                    cursor = conn.cursor()
                    logger.debug(f"🧠 Storing interaction: interaction_or_user_id={type(interaction_or_user_id)}, user_id_or_data={type(user_id_or_data)}")

                    if isinstance(interaction_or_user_id, str) and isinstance(user_id_or_data, dict):
                        user_id = interaction_or_user_id
                        interaction_data = user_id_or_data or {}
                        start_time = datetime.now()

                        if not interaction_data.get('operation_type'):
                            logger.warning(f"🧠 Missing operation_type for user {user_id}, using default")
                            interaction_data['operation_type'] = 'unknown'
                        if not interaction_data.get('template_file'):
                            logger.warning(f"🧠 Missing template_file for user {user_id}, using default")
                            interaction_data['template_file'] = 'unknown'

                        cursor.execute('''
                            INSERT INTO interactions 
                            (user_id, timestamp, operation_type, template_used, user_input, 
                             generated_content, success, feedback, execution_time, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            user_id,
                            datetime.now().isoformat(),
                            interaction_data.get('operation_type', 'unknown'),
                            interaction_data.get('template_file', 'unknown'),
                            json.dumps(interaction_data.get('user_input', {})),
                            interaction_data.get('generated_content', ''),
                            interaction_data.get('success', False),
                            json.dumps(interaction_data.get('feedback', {})),
                            (datetime.now() - start_time).total_seconds(),
                            interaction_data.get('source', 'ai_agent')
                        ))

                    elif isinstance(interaction_or_user_id, Interaction):
                        interaction = interaction_or_user_id
                        user_id = user_id_or_data or 'default'
                        start_time = datetime.now()

                        cursor.execute('''
                            INSERT INTO interactions 
                            (user_id, timestamp, operation_type, template_used, user_input, 
                             generated_content, success, feedback, execution_time, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            user_id,
                            interaction.timestamp.isoformat(),
                            interaction.operation_type or 'unknown',
                            interaction.template_used or 'unknown',
                            json.dumps(interaction.user_input or {}),
                            interaction.generated_content or '',
                            interaction.success,
                            json.dumps(interaction.user_feedback or {}),
                            (datetime.now() - start_time).total_seconds(),
                            'ai_agent'
                        ))

                    else:
                        logger.error(f"🧠 Invalid interaction data type: {type(interaction_or_user_id)}, value={interaction_or_user_id}")
                        raise ValueError(f"Invalid interaction data type: {type(interaction_or_user_id)}")

                    conn.commit()
                    logger.debug(f"🧠 Interaction stored successfully for user {user_id}")
                    return True

            except sqlite3.Error as e:
                logger.error(f"🧠 Failed to store interaction due to database error: {e}\n{traceback.format_exc()}")
                return False
            except json.JSONDecodeError as e:
                logger.error(f"🧠 Failed to store interaction due to JSON error: {e}\n{traceback.format_exc()}")
                return False
            except Exception as e:
                logger.error(f"🧠 Failed to store interaction: {e}\n{traceback.format_exc()}")
                return False

    def get_user_preferences(self, user_id: str) -> Optional[UserPreference]:
        """Get user preferences from memory"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT preferences FROM user_preferences WHERE user_id = ?', (user_id,))
                result = cursor.fetchone()

                if result and result[0]:
                    prefs_data = json.loads(result[0])
                    # Filter only valid UserPreference fields
                    valid_fields = {f.name for f in UserPreference.__dataclass_fields__.values()}
                    filtered_prefs = {k: v for k, v in prefs_data.items() if k in valid_fields}

                    # Ensure required fields are present with defaults
                    filtered_prefs.setdefault('user_id', user_id)
                    filtered_prefs.setdefault('preferred_templates', {})
                    filtered_prefs.setdefault('common_operations', [])
                    filtered_prefs.setdefault('feedback_patterns', {})
                    filtered_prefs.setdefault('last_updated', datetime.now().isoformat())
                    filtered_prefs.setdefault('default_space', None)

                    return UserPreference(**filtered_prefs)
                return None
        except Exception as e:
            logger.error(f"🧠 Failed to get user preferences: {e}\n{traceback.format_exc()}")
            return None

    def get_recent_interactions(self, user_id: str, limit: int = 10) -> List[Interaction]:
        """Get recent interactions for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM interactions 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))

            results = cursor.fetchall()
            conn.close()

            interactions = []
            for row in results:
                if len(row) >= 8:  # Ensure row has enough columns
                    interactions.append(Interaction(
                        timestamp=datetime.fromisoformat(row[2]),
                        operation_type=row[3] or "unknown",
                        template_used=row[4] or "unknown",
                        user_input=json.loads(row[5]) if row[5] else {},
                        generated_content=row[6] or "",
                        success=bool(row[7])
                    ))

            return interactions
        except Exception as e:
            logger.error(f"🧠 Failed to get recent interactions: {e}")
            return []

    def store_feedback(self, interaction_id: str, feedback: Dict, user_id: str):
        """Store comprehensive feedback with user information"""
        if not feedback or not isinstance(feedback, dict):
            logger.warning("🧠 Invalid feedback, skipping storage")
            return

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                user_name = feedback.get('user_name', f'User_{user_id}')
                user_email = feedback.get('user_email', '')
                aspects = feedback.get('aspects', {})

                cursor.execute('''
                    INSERT INTO feedback 
                    (interaction_id, user_id, user_name, user_email, rating, 
                     content_quality, formatting, accuracy, completeness, 
                     comments, feature_requests, contact_me, timestamp, 
                     user_agent, ip_address, page_title, operation_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction_id,
                    user_id,
                    user_name,
                    user_email,
                    feedback.get('rating', 3),
                    aspects.get('content_quality', 3),
                    aspects.get('formatting', 3),
                    aspects.get('accuracy', 3),
                    aspects.get('completeness', 3),
                    feedback.get('comments', ''),
                    feedback.get('feature_requests', ''),
                    feedback.get('contact_me', False),
                    datetime.now().isoformat(),
                    feedback.get('user_agent', ''),
                    feedback.get('ip_address', ''),
                    feedback.get('page_title', ''),
                    feedback.get('operation_type', '')
                ))

                cursor.execute('''
                    UPDATE interactions 
                    SET feedback = ? 
                    WHERE id = ? AND user_id = ?
                ''', (json.dumps(feedback), interaction_id, user_id))

                conn.commit()
                logger.debug(f"🧠 Feedback stored for user {user_name} (ID: {user_id})")
        except sqlite3.Error as e:
            logger.error(f"🧠 Failed to store feedback: {e}\n{traceback.format_exc()}")

    def get_usage_patterns(self, user_id: str) -> Dict:
        """Get usage patterns for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT operation_type, COUNT(*) as count, AVG(CASE WHEN success THEN 1 ELSE 0 END) as success_rate
                FROM interactions 
                WHERE user_id = ? 
                GROUP BY operation_type
                ORDER BY count DESC
            ''', (user_id,))

            results = cursor.fetchall()
            conn.close()

            patterns = {}
            for row in results:
                patterns[row[0]] = {
                    'count': row[1],
                    'success_rate': row[2]
                }

            return patterns
        except Exception as e:
            logger.error(f"🧠 Failed to get usage patterns: {e}")
            return {}

    # Add these methods to your AgentMemory class in utils/ai_agent.py

    def store_page_creation(self, user_id: str, page_data: Dict) -> bool:
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                logger.debug(f"🧠 Storing page creation for user {user_id}, title: {page_data.get('page_title')}")

                cursor.execute('''
                INSERT INTO page_creations 
                (user_id, operation_type, template_file, page_title, page_id, page_url, 
                 space_key, parent_page_id, success, error_message, generation_time_seconds, 
                 timestamp, source, ai_agent_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                    user_id,
                    page_data.get('operation_type', 'unknown'),
                    page_data.get('template_file', 'unknown'),
                    page_data.get('page_title', ''),
                    page_data.get('page_id', ''),
                    page_data.get('page_url', ''),
                    page_data.get('space_key', ''),
                    page_data.get('parent_page_id', ''),
                    page_data.get('success', False),
                    page_data.get('error_message', ''),
                    page_data.get('generation_time_seconds', 0.0),
                    datetime.now().isoformat(),
                    page_data.get('source', 'ai_agent'),
                    page_data.get('ai_agent_used', True)
                ))

                conn.commit()
                logger.debug(f"🧠 Page creation stored successfully for user {user_id}")
                return True
        except sqlite3.Error as e:
            logger.error(f"🧠 Failed to store page creation: {e}\n{traceback.format_exc()}")
            return False
        except Exception as e:
            logger.error(f"🧠 Failed to store page creation: {e}\n{traceback.format_exc()}")
            return False

def get_dashboard_statistics(self) -> Dict:
    """Get real-time dashboard statistics"""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Total pages created
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE success = 1')
        total_pages = cursor.fetchone()[0]

        # Success rate
        cursor.execute('SELECT COUNT(*) FROM page_creations')
        total_attempts = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE success = 1')
        successful_attempts = cursor.fetchone()[0]
        success_rate = (successful_attempts / max(total_attempts, 1)) * 100

        # Average generation time
        cursor.execute('SELECT AVG(generation_time_seconds) FROM page_creations WHERE success = 1')
        avg_time_result = cursor.fetchone()[0]
        avg_time = round(avg_time_result or 0, 1)

        # AI calls made (approximate)
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE ai_agent_used = 1')
        ai_calls = cursor.fetchone()[0]

        # Recent activity (last 7 days)
        from datetime import timedelta
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM page_creations WHERE timestamp > ? AND success = 1', (week_ago,))
        recent_pages = cursor.fetchone()[0]

        # Operation type distribution
        cursor.execute('''
            SELECT operation_type, COUNT(*) 
            FROM page_creations 
            WHERE success = 1 
            GROUP BY operation_type 
            ORDER BY COUNT(*) DESC
        ''')
        operation_distribution = dict(cursor.fetchall())

        # Unique users
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM page_creations')
        unique_users = cursor.fetchone()[0]

        conn.close()

        return {
            'total_pages': total_pages,
            'success_rate': round(success_rate, 1),
            'avg_generation_time': avg_time,
            'ai_calls_made': ai_calls,
            'recent_pages_week': recent_pages,
            'operation_distribution': operation_distribution,
            'unique_users': unique_users,
            'last_updated': datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"📊 Failed to get dashboard statistics: {e}")
        return {
            'total_pages': 0,
            'success_rate': 0,
            'avg_generation_time': 0,
            'ai_calls_made': 0,
            'recent_pages_week': 0,
            'operation_distribution': {},
            'unique_users': 0,
            'last_updated': datetime.now().isoformat()
        }

def get_recent_activity(self, limit: int = 10) -> List[Dict]:
    """Get recent page creation activity"""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT operation_type, template_file, page_title, success, 
                   generation_time_seconds, timestamp, space_key, page_url
            FROM page_creations 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()
        conn.close()

        activities = []
        for row in results:
            activities.append({
                'operation_type': row[0],
                'template_file': row[1],
                'page_title': row[2],
                'success': bool(row[3]),
                'duration': f"{row[4]:.1f}s" if row[4] else "N/A",
                'timestamp': row[5],
                'time_ago': self._calculate_time_ago(row[5]),
                'space_key': row[6],
                'page_url': row[7]
            })

        return activities
    except Exception as e:
        logger.error(f"📊 Failed to get recent activity: {e}")
        return []

class AgentLearner:
    """🎓 Agent learning system"""

    def __init__(self):
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.user_feedback_patterns = defaultdict(list)

    def update_preferences(self, interaction: Interaction, user_id: str):
        """Update user preferences based on interaction"""
        if not interaction:
            return
        logger.debug(f"🎓 Updating preferences for user {user_id} based on {interaction.operation_type}")

    def reinforce_successful_pattern(self, interaction: Interaction):
        """Reinforce patterns that led to success"""
        if not interaction:
            return

        pattern_key = f"{interaction.operation_type}_{interaction.template_used}"
        self.success_patterns[pattern_key].append({
            'timestamp': interaction.timestamp,
            'user_input': interaction.user_input,
            'success': True
        })

    def learn_from_failure(self, interaction: Interaction):
        """Learn from failed interactions"""
        if not interaction:
            return

        pattern_key = f"{interaction.operation_type}_{interaction.template_used}"
        self.failure_patterns[pattern_key].append({
            'timestamp': interaction.timestamp,
            'user_input': interaction.user_input,
            'success': False
        })

    def learn_from_feedback(self, feedback: Dict, user_id: str):
        """Learn from user feedback"""
        if not feedback:
            return

        self.user_feedback_patterns[user_id].append({
            'timestamp': datetime.now(),
            'feedback': feedback
        })

    def get_insights(self, user_id: str) -> Dict:
        """Get learning insights for user"""
        return {
            'success_rate': self._calculate_success_rate(user_id),
            'common_patterns': self._get_common_patterns(user_id),
            'improvement_areas': self._get_improvement_areas(user_id)
        }

    def _calculate_success_rate(self, user_id: str) -> float:
        """Calculate success rate for user based on interaction history"""
        try:
            interactions = self.memory.get_recent_interactions(user_id, limit=100)
            if not interactions:
                return 0.8  # Default for new users
            success_count = sum(1 for i in interactions if i.success)
            return success_count / len(interactions)
        except Exception as e:
            logger.error(f"🎓 Failed to calculate success rate: {e}")
            return 0.8

    def _get_common_patterns(self, user_id: str) -> List[str]:
        """Get common patterns for user based on interaction history"""
        try:
            patterns = self.memory.get_usage_patterns(user_id)
            return [op for op, stats in patterns.items() if stats['count'] > 3]
        except Exception as e:
            logger.error(f"🎓 Failed to get common patterns: {e}")
            return ["template_usage", "operation_timing"]

    def submit_for_approval(self, page_data: Dict, workflow_tool: str = "jira"):
        """Submit generated page for approval"""
        try:
            if workflow_tool == "jira":
                # Placeholder for Jira integration
                logger.info(f"📋 Submitting page {page_data.get('title')} to Jira")
                return {"success": True, "ticket_id": "JIRA-123"}
            raise ValueError(f"Unsupported workflow tool: {workflow_tool}")
        except Exception as e:
            logger.error(f"📋 Approval submission failed: {e}")
            return {"success": False, "error": str(e)}

    def _get_improvement_areas(self, user_id: str) -> List[str]:
        """Get improvement areas for user"""
        return ["template_selection", "input_validation"]  # Placeholder

class AgentPlanner:
    """📋 Agent planning system"""

    def __init__(self, model):
        self.model = model

    def create_plan(self, intent_analysis: Dict, user_input: Dict) -> Dict:
        """Create execution plan based on intent analysis"""
        start_time = datetime.now()
        logger.info(f"📋 Creating plan for intent: {intent_analysis.get('primary_intent', 'unknown')}")

        if not intent_analysis:
            intent_analysis = {}
        if not user_input:
            user_input = {}

        if not self.model:
            logger.warning("📋 Model not available, using fallback planning")
            return {
                "template_selected": user_input.get('operation_type', 'default'),
                "execution_steps": ["analyze_template", "generate_content", "create_page"],
                "risk_factors": ["template_complexity"],
                "optimization_strategies": ["use_fallback_if_needed"],
                "success_probability": 0.7,
                "estimated_duration": "3-5 minutes",
                "user_expertise": "intermediate",
                "recommendations": ["follow_standard_process"]
            }

        planning_prompt = f"""Create detailed execution plan for Confluence page generation.
    INTENT ANALYSIS: {json.dumps(intent_analysis, indent=2)}
    USER INPUT: {json.dumps(user_input, indent=2)}
    Create a step-by-step execution plan considering:
    1. User expertise level
    2. Operation complexity
    3. Potential challenges
    4. Optimization opportunities
    5. Success probability
    Return JSON plan:
    {{
      "template_selected": "best_template_choice",
      "execution_steps": ["step1", "step2", "step3"],
      "risk_factors": ["risk1", "risk2"],
      "optimization_strategies": ["opt1", "opt2"],
      "success_probability": 0.85,
      "estimated_duration": "2-3 minutes",
      "user_expertise": "intermediate",
      "recommendations": ["rec1", "rec2"]
    }}"""

        try:
            logger.info("📋 Sending planning prompt to LLM")
            response = self.model.generate_content(planning_prompt)
            if not response or not response.text:
                raise ValueError("Empty model response")

            plan = json.loads(self._clean_json_response(response.text))
            logger.info(f"📋 Created execution plan with {len(plan.get('execution_steps', []))} steps in {(datetime.now() - start_time).total_seconds():.2f}s")
            return plan
        except Exception as e:
            logger.error(f"📋 Planning failed: {e}\n{traceback.format_exc()}")
            return {
                "template_selected": user_input.get('operation_type', 'default'),
                "execution_steps": ["analyze_template", "generate_content", "create_page"],
                "risk_factors": ["template_complexity"],
                "optimization_strategies": ["use_fallback_if_needed"],
                "success_probability": 0.7,
                "estimated_duration": "3-5 minutes",
                "user_expertise": "intermediate",
                "recommendations": ["follow_standard_process"]
            }

    def _clean_json_response(self, response_text: str) -> str:
        """Clean JSON response from LLM"""
        if not response_text:
            return "{}"

        if response_text.startswith('```'):
            lines = response_text.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip().startswith('```'):
                lines = lines[:-1]
            response_text = '\n'.join(lines)

        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        if start_idx >= 0 and end_idx >= 0:
            response_text = response_text[start_idx:end_idx + 1]
        else:
            return "{}"

        return response_text.strip()

class AgentAdapter:
    """🔄 Agent adaptation system"""

    def __init__(self):
        self.adaptation_history = []
        self.template_modifications = {}

    def consider_template_adaptation(self, interaction: Interaction):
        """Consider if templates need adaptation"""
        if not interaction:
            return
        logger.debug(f"🔄 Considering template adaptation for {interaction.operation_type}")

    def adapt_from_feedback(self, feedback: Dict):
        """Adapt agent behavior based on feedback"""
        if not feedback:
            return
        logger.debug(f"🔄 Adapting from feedback: {list(feedback.keys())}")

    def get_template_suggestions(self, user_id: str) -> List[str]:
        """Get template improvement suggestions"""
        return [
            "Consider adding more detailed steps for complex operations",
            "Simplify status indicators for better readability",
            "Add more context-aware content suggestions"
        ]