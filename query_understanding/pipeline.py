

from __future__ import annotations

import json
import logging

from .ambiguity_detector import detect_ambiguity
from .category_selector import select_categories
from .entity_extractor import Entity, EntityExtractor, RuleBasedEntityExtractor
from .intent_classifier import IntentClassifier, RuleBasedIntentClassifier
from .language_detector import detect_language
from .models import QueryUnderstanding
from .query_rewriter import QueryRewriter, RuleBasedQueryRewriter, looks_like_followup

logger = logging.getLogger(__name__)


class QueryUnderstandingPipeline:
    def __init__(
        self,
        intent_classifier: IntentClassifier | None = None,
        entity_extractor: EntityExtractor | None = None,
        query_rewriter: QueryRewriter | None = None,
    ):
        self.intent_classifier = intent_classifier or RuleBasedIntentClassifier()
        self.entity_extractor = entity_extractor or RuleBasedEntityExtractor()
        self.query_rewriter = query_rewriter or RuleBasedQueryRewriter()

    def process(
        self, query: str, previous: QueryUnderstanding | None = None
    ) -> QueryUnderstanding:
        language = detect_language(query)

        if language != "en":
            
            result = QueryUnderstanding(
                original_query=query,
                rewritten_query=query,
                intent="GENERAL",
                category=None,
                categories=[],
                entities=[],
                confidence=0.0,
                language=language,
                ambiguous=False,
            )
            self._log(result)
            return result

        intent, confidence = self.intent_classifier.classify(query)
        entities = self.entity_extractor.extract(query)

      
        resolved_from_context = False
        effective_entities = entities
        effective_intent = intent
        if not entities and previous and previous.entities and looks_like_followup(query):
            effective_entities = previous.entities
            effective_intent = intent if intent != "GENERAL" else previous.intent
            confidence = max(confidence, previous.confidence)
            resolved_from_context = True

        categories = select_categories(
            effective_intent, [e.label for e in effective_entities]
        )
        category = categories[0][0] if categories else None

        ambiguous, options = detect_ambiguity(
            query, effective_entities, effective_intent, confidence
        )

        if ambiguous:
            rewritten = query
        else:
            rewritten = self.query_rewriter.rewrite(
                query, entities, previous_entities=previous.entities if previous else None
            )

        result = QueryUnderstanding(
            original_query=query,
            rewritten_query=rewritten,
            intent=effective_intent,
            category=category,
            categories=categories,
            entities=effective_entities,
            confidence=confidence,
            language=language,
            ambiguous=ambiguous,
            clarification_options=options,
            resolved_from_context=resolved_from_context,
        )
        self._log(result)
        return result

    @staticmethod
    def _log(result: QueryUnderstanding) -> None:
        logger.info(json.dumps(result.to_log_dict(), default=str))
