"""
Interview Preparation Platform
Real-time interview simulation with scheduling, code compilation, and AI interviewer
"""

from .simulation_engine import (
    InterviewSimulationEngine,
    InterviewMode,
    CompanyRole,
    CodingProblem,
    TestCase
)

from .compiler import (
    CodeCompiler,
    InterviewCodeValidator,
    ExecutionResult
)

from .scheduler import (
    InterviewScheduler,
    ScheduledInterview,
    InterviewStatus,
    InterviewFrequency
)

__all__ = [
    "InterviewSimulationEngine",
    "InterviewMode",
    "CompanyRole",
    "CodingProblem",
    "TestCase",
    "CodeCompiler",
    "InterviewCodeValidator",
    "ExecutionResult",
    "InterviewScheduler",
    "ScheduledInterview",
    "InterviewStatus",
    "InterviewFrequency"
]

__version__ = "1.0.0"
