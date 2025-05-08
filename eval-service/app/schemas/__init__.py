# eval-service/app/schemas/__init__.py

from .evaluation import EvaluateTicketRequest, EvaluateTicketResponse

# Define which symbols are exported when using 'from app.schemas import *'
# More importantly, signifies these are the main schemas of this package.
__all__ = [
    "EvaluateTicketRequest",
    "EvaluateTicketResponse",
]