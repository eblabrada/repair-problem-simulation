import heapq
import numpy as np
from enum import Enum
from collections import deque

class EventType(Enum):
    BREAKDOWN = "breakdown"
    REPAIR_COMPLETE = "repair_complete"

class Event:
    def __init__(self, time: float, event_type: EventType):
        self.time = time
        self.event_type = event_type

    def __lt__(self, other):
        return self.time < other.time

class Snapshot:
    def __init__(self, time, down, in_repair_queue, next_repair_time):
        self.time = time
        self.down = down               
        self.in_repair_queue = in_repair_queue
        self.next_repair_time = next_repair_time

class RepairSystem:
    def __init__(self, n_operating, n_spares, time_to_breakdown, time_to_repair, capture_states=False):
        self.n_operating = n_operating
        self.n_spares = n_spares
        self.time_to_breakdown = time_to_breakdown
        self.time_to_repair = time_to_repair
        self.capture_states = capture_states

        self.current_time = 0.0
        self.down = 0
        self.event_queue = []
        self.repair_queue = 0
        self.repair_in_progress = False
        self.next_repair_time = np.inf
        self.snapshots = []

    def schedule_initial_events(self):
        for _ in range(self.n_operating):
            t_fail = self.time_to_breakdown()
            heapq.heappush(self.event_queue, Event(t_fail, EventType.BREAKDOWN))

    def record_snapshot(self):
        snap = Snapshot(self.current_time, self.down, self.repair_queue, self.next_repair_time)
        self.snapshots.append(snap)

    def run(self):
        self.schedule_initial_events()
        if self.capture_states:
            self.record_snapshot()

        while True:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time

            if event.event_type == EventType.BREAKDOWN:
                self.handle_breakdown()
            else:
                self.handle_repair_complete()

            if self.capture_states:
                self.record_snapshot()

            if self.down > self.n_spares:
                break

        return self.current_time

    def handle_breakdown(self):
        self.down += 1
        if self.down <= self.n_spares:
            t_fail = self.current_time + self.time_to_breakdown()
            heapq.heappush(self.event_queue, Event(t_fail, EventType.BREAKDOWN))

        if not self.repair_in_progress:
            self.repair_in_progress = True
            self.next_repair_time = self.current_time + self.time_to_repair()
            heapq.heappush(self.event_queue, Event(self.next_repair_time, EventType.REPAIR_COMPLETE))
        else:
            self.repair_queue += 1

    def handle_repair_complete(self):
        self.down -= 1
        if self.repair_queue > 0:
            self.repair_queue -= 1
            self.next_repair_time = self.current_time + self.time_to_repair()
            heapq.heappush(self.event_queue, Event(self.next_repair_time, EventType.REPAIR_COMPLETE))
        else:
            self.repair_in_progress = False
            self.next_repair_time = np.inf