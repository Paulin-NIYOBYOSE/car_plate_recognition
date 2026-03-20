"""
temporal.py — Temporal Confirmation Module

Implements temporal validation for the ANPR pipeline.
Collects valid plate readings over multiple frames and confirms
via majority vote before logging.

Usage:
    from temporal import TemporalBuffer, majority_vote
    
    buffer = TemporalBuffer(size=5, cooldown=10)
    
    # In loop:
    if valid_plate:
        buffer.add(valid_plate)
        confirmed = buffer.get_confirmed()
        if confirmed and buffer.should_save(confirmed):
            # Save to CSV
            buffer.mark_saved(confirmed)
"""

import time
from collections import Counter
from typing import Optional


class TemporalBuffer:
    """
    Rolling buffer for temporal plate confirmation.
    
    Collects valid readings over multiple frames and confirms
    via majority vote. Includes cooldown to prevent duplicates.
    """
    
    def __init__(self, size: int = 5, cooldown: float = 10.0):
        """
        Initialize temporal buffer.
        
        Args:
            size: Number of frames to collect before voting
            cooldown: Seconds before same plate can be saved again
        """
        self.size = size
        self.cooldown = cooldown
        self._buffer = []
        self._last_saved_plate: Optional[str] = None
        self._last_saved_time: float = 0.0
    
    def add(self, plate: str) -> None:
        """Add a valid plate reading to the buffer."""
        self._buffer.append(plate)
        if len(self._buffer) > self.size:
            self._buffer.pop(0)
    
    def get_confirmed(self) -> Optional[str]:
        """
        Get confirmed plate via majority vote.
        
        Returns:
            Most common plate in buffer, or None if buffer empty
        """
        return majority_vote(self._buffer)
    
    def should_save(self, plate: str) -> bool:
        """
        Check if plate should be saved (cooldown + duplicate check).
        
        Args:
            plate: Plate string to check
            
        Returns:
            True if plate should be saved to CSV
        """
        now = time.time()
        if plate != self._last_saved_plate:
            return True
        if (now - self._last_saved_time) > self.cooldown:
            return True
        return False
    
    def mark_saved(self, plate: str) -> None:
        """Mark plate as saved with current timestamp."""
        self._last_saved_plate = plate
        self._last_saved_time = time.time()
    
    def clear(self) -> None:
        """Clear the buffer."""
        self._buffer = []
    
    def __len__(self) -> int:
        """Return current buffer size."""
        return len(self._buffer)


def majority_vote(buffer: list) -> Optional[str]:
    """
    Return most common element in buffer via majority vote.
    
    Args:
        buffer: List of plate strings
        
    Returns:
        Most common plate, or None if buffer is empty
        
    Example:
        >>> majority_vote(["RAA123A", "RAA123A", "RAB456C"])
        'RAA123A'
    """
    if not buffer:
        return None
    return Counter(buffer).most_common(1)[0][0]


# Simple cooldown tracker for standalone usage
class CooldownTracker:
    """Simple tracker for plate saving cooldown."""
    
    def __init__(self, cooldown_seconds: float = 10.0):
        self.cooldown = cooldown_seconds
        self._last_plate: Optional[str] = None
        self._last_time: float = 0.0
    
    def can_save(self, plate: str) -> bool:
        """Check if enough time has passed to save this plate."""
        now = time.time()
        if plate != self._last_plate:
            return True
        return (now - self._last_time) > self.cooldown
    
    def record_save(self, plate: str) -> None:
        """Record that a plate was just saved."""
        self._last_plate = plate
        self._last_time = time.time()


if __name__ == "__main__":
    # Demo/test
    print("Testing TemporalBuffer...")
    
    buf = TemporalBuffer(size=5, cooldown=2.0)
    
    # Simulate readings
    test_plates = ["RAA123A", "RAA123A", "RAA123A", "RAB456C", "RAA123A"]
    
    for plate in test_plates:
        buf.add(plate)
        confirmed = buf.get_confirmed()
        print(f"Added: {plate}, Buffer: {list(buf._buffer)}, Confirmed: {confirmed}")
    
    confirmed = buf.get_confirmed()
    print(f"\nFinal confirmed plate: {confirmed}")
    print(f"Should save: {buf.should_save(confirmed)}")
    
    buf.mark_saved(confirmed)
    print(f"After saving, should save again: {buf.should_save(confirmed)}")
    
    print("\nTemporal module test complete.")
