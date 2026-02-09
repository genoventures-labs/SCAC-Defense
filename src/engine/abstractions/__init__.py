"""
Reasoning Abstraction Layers for SCAC Defense System

This package provides abstract interfaces for reasoning components,
enabling strategy pattern implementation and future Mavaia integration.
"""

from .threat_assessor import ThreatAssessor
from .response_selector import ResponseSelector
from .pattern_recognizer import PatternRecognizer

__all__ = [
    'ThreatAssessor',
    'ResponseSelector',
    'PatternRecognizer',
]
