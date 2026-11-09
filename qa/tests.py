"""Ask and history API tests. The LLM and retrieval are mocked, so tests are fast and repeatable."""
from django.test import override_settings
from .models import QARecord
from rag.answering import AnswerResult
from rag.generation import GenerationError
from rest_framework.test import APITestCase
from unittest.mock import patch


@override_settings(OPENROUTER_MODEL="test-model")
class AskApiTests(APITestCase):
    @patch("qa.services.answer_question")
    @patch("qa.services.build_chat_model")
    def test_success_returns_201_and_saves_the_record(self, mock_build, mock_answer) -> None:
        mock_build.return_value = object()
        mock_answer.return_value = AnswerResult("Paris", [{}])
        response = self.client.post("/api/ask/", {"question": "where is the capital of France?"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["answer"], "Paris")
        self.assertEqual(QARecord.objects.count(), 1)
    
    def test_blank_question_returns_400_and_saves_nothing(self) -> None:
        response = self.client.post("/api/ask/", {"question": ""}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(QARecord.objects.count(), 0)
    
    @patch("qa.services.answer_question")
    @patch("qa.services.build_chat_model")
    def test_generation_failure_returns_503_and_saves_nothing(self, mock_build, mock_answer) -> None:
        mock_build.return_value = object()
        mock_answer.side_effect = GenerationError("down")
        response = self.client.post("/api/ask/", {"question": "where is the capital of France?"}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(QARecord.objects.count(), 0)

class HistoryApiTests(APITestCase):
    def test_history_lists_saved_records(self) -> None:
        record = QARecord.objects.create(
            question="where is the capital of France?",
            answer="Paris",
            sources=[],
            model_name="test-model",
            latency_ms=10,
        )
        response = self.client.get("/api/history/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["question"], record.question)
    
    def test_history_rejects_post_with_405(self) -> None:
        response = self.client.post("/api/history/")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(QARecord.objects.count(), 0)
