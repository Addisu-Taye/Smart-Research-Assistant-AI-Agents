# -*- coding: utf-8 -*-
# Developed by: Addisu Taye & Kidist Demessie
# Date: 2024-06-15
# Purpose: Shared utility functions
# Key Features:
#   - Error logging
#   - Text processing
#   - Validation helpers

import logging

def log_error(message: str):
    """Log errors with timestamp."""
    logging.basicConfig(filename='errors.log', level=logging.ERROR)
    logging.error(message)

def normalize_text(text: str) -> str:
    """Clean and normalize raw text."""
    return ' '.join(text.split())