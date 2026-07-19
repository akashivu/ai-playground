import time
from utils.logger import logger
from auth.schemas import CurrentUser
from models.ai_response import AIResponse
from models.conversation_state import ConversationState
from langchain_components.routing.intent_router import route_question
from core.dependencies import conversation_store
from services.recommendation_session_service import recommendation_session_service
from services.booking_session_service import booking_session_service
from services.itinerary_session_service import itinerary_session_service
from services.usage_tracking_service import usage_tracking_service
from services.token_tracking_service import token_tracking_service
from services.cost_estimation_service import cost_estimation_service
from config.settings import settings
from langchain_components.routing.intent_router import execute_workflow
from langchain_components.routing.intent_types import IntentType
from langchain_components.routing.conversation_control import classify_conversation_control
from langchain_components.routing.conversation_control_prompt import ConversationControl

class ConversationManager:
    """Central orchestration service for AI conversations."""

    def process_message(
        self,
        current_user: CurrentUser,
        session_id: str,
        question: str,
    ) -> AIResponse:
        state = self._build_state(current_user, session_id, question)
        result = self._execute_workflow(state)
        self._track_usage(current_user.user_id, session_id, result)
        self._persist(current_user.user_id, session_id, question, result)
        return self._build_response(session_id, result)

    # --- private methods ---

    def _build_state(
        self,
        current_user: CurrentUser,
        session_id: str,
        question: str,
    ) -> ConversationState:
        user_id = current_user.user_id

        history = conversation_store.get_messages(
            user_id=user_id,
            session_id=session_id,
        )
        booking_details = booking_session_service.get_booking(
            user_id=user_id,
            session_id=session_id,
        )
        previous_recommendation = recommendation_session_service.get(
            user_id=user_id,
            session_id=session_id,
        )
        previous_itinerary = itinerary_session_service.get(
            user_id=user_id,
            session_id=session_id,
        )

        return ConversationState(
            session_id=session_id,
            user_id=user_id,
            email=current_user.email,
            role=current_user.role,
            question=question,
            history=history,
            booking_details=booking_details,
            recommendation_details=previous_recommendation,
            itinerary_details=previous_itinerary,
        )

    def _execute_workflow(self, state: ConversationState) -> dict:
        start = time.perf_counter()

        if state.booking_details:
            result = self._handle_active_booking(state)
        elif state.itinerary_details:
            result = execute_workflow(
                intent=IntentType.ITINERARY,
                state=state.model_dump(),
            )
        else:
            result = route_question(state.model_dump())

        latency = time.perf_counter() - start

        logger.info(
            "Intent=%s User=%s Session=%s Latency=%.2fms",
            result.get("intent"),
            state.user_id,
            state.session_id,
            latency * 1000,
        )

        return {
            **result,
            "latency": latency,
        }

    def _handle_active_booking(self, state: ConversationState) -> dict:
        """
        There is an active booking in progress for this session. Before routing
        to the booking workflow, check whether the user's message is actually a
        control signal (cancel/pause/interrupt) rather than a direct answer to
        the current booking question.
        """
        control = classify_conversation_control(state.question)

        logger.info(
            "ConversationControl=%s User=%s Session=%s",
            control,
            state.user_id,
            state.session_id,
        )

        if control == ConversationControl.CANCEL:
            return {
                "answer": "I've cancelled your booking request. How else can I help you?",
                "intent": IntentType.BOOKING,
                "completed": True,
                "booking_details": None,
            }

        if control == ConversationControl.PAUSE:
            # Keep booking_details as-is (do NOT clear) so it can be resumed later.
            return {
                "answer": (
                    "No problem, I've paused your booking. "
                    "Just say 'continue' whenever you're ready to pick it back up."
                ),
                "intent": IntentType.BOOKING,
                "completed": False,
            }

        if control == ConversationControl.INTERRUPT:
            faq_result = route_question(state.model_dump())
            faq_answer = faq_result.get("answer", "")
            return {
                **faq_result,
                "answer": (
                    f"{faq_answer}\n\n"
                    "We were in the middle of your booking. Would you like to continue?"
                ),
                # booking_details untouched -> booking stays active for next turn
                "completed": False,
            }

        # RESUME or NONE: treat the message as a direct answer to the booking
        # workflow's current question (RESUME is just an explicit confirmation
        # to keep going; NONE means no control signal was detected at all).
        return execute_workflow(
            intent=IntentType.BOOKING,
            state=state.model_dump(),
        )

    def _track_usage(
        self,
        user_id: str,
        session_id: str,
        result: dict,
    ) -> None:
        usage_tracking_service.log_request(
            user_id=user_id,
            session_id=session_id,
            intent=result.get("intent", "UNKNOWN"),
            latency=result["latency"],
        )

        token_usage = result.get("token_usage", {})
        if not token_usage:
            return

        model = token_usage.get("model", settings.OPENAI_MODEL)
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)

        token_tracking_service.log_usage(
            user_id=user_id,
            session_id=session_id,
            intent=result.get("intent", "UNKNOWN"),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=token_usage.get("total_tokens", 0),
            estimated_cost=cost_estimation_service.estimate(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model=model,
            ),
        )

    def _persist(
        self,
        user_id: str,
        session_id: str,
        question: str,
        result: dict,
    ) -> None:
        if result.get("booking_details"):
            booking_session_service.save_booking(
                user_id=user_id,
                session_id=session_id,
                booking=result["booking_details"],
            )

        if "recommendation_details" in result:
            recommendation_session_service.save(
                user_id=user_id,
                session_id=session_id,
                recommendation=result["recommendation_details"],
            )

        if "itinerary_details" in result:
            itinerary_session_service.save(
                user_id=user_id,
                session_id=session_id,
                itinerary=result["itinerary_details"],
            )

        if result.get("completed"):
            booking_session_service.clear_booking(
                user_id=user_id,
                session_id=session_id,
            )
            recommendation_session_service.clear(
                user_id=user_id,
                session_id=session_id,
            )
            itinerary_session_service.clear(
                user_id=user_id,
                session_id=session_id,
            )

        conversation_store.add_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=question,
        )
        conversation_store.add_message(
            user_id=user_id,
            session_id=session_id,
            role="assistant",
            content=result.get("answer", "I was unable to generate a response."),
        )

    def _build_response(self, session_id: str, result: dict) -> AIResponse:
        return AIResponse(
            session_id=session_id,
            answer=result.get("answer", "I was unable to generate a response."),
            intent=result.get("intent"),
            completed=result.get("completed", False),
        )


conversation_manager = ConversationManager()