from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rag.generation import GenerationError

from .serializers import AskRequestSerializer, QARecordSerializer
from .services import ask


class AskView(APIView):
    def post(self, request: Request) -> Response:
        """POST {"question": "..."} → 201 with the saved record, 400 if invalid, 503 if the LLM fails."""
        ask_request_serializer = AskRequestSerializer(data=request.data)
        ask_request_serializer.is_valid(raise_exception=True)
        try:
            record = ask(ask_request_serializer.validated_data["question"])
            serialized_record = QARecordSerializer(record)
            return Response(data=serialized_record.data, status=status.HTTP_201_CREATED)
        except GenerationError: 
            return Response({"detail": "The answer generation service is temporarily unavailable."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
            
