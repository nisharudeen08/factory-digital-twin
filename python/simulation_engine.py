import simpy
import numpy as np
from typing import List, Dict, Any, Optional
from math_engine import StationMetric, ShiftResult, identify_bottleneck

class Station:
    """Represents a machine/station in the factory."""
    def __init__(self, env: simpy.Environment, config: Dict[str, Any]):
        self.env = env
        self.id = config["id"]
        self.name = config["name"]
        self.name_ta = config.get("name_ta", self.name)
        self.cycle_time_mean = config["cycle_time_sec"]
        self.mtbf_hours = config.get("mtbf_hours", 8)
        self.mttr_hours = config.get("mttr_hours", 0.5)
        
        self.resource = simpy.Resource(env, capacity=config.get("num_machines", 1))
        
        self.total_processed = 0
        self.total_wait_time = 0.0
        self.total_process_time = 0.0
        self.status = "idle"
        self.broken = False

    def process_job(self, env: simpy.Environment, job_id: int):
        """Simulate processing a single job."""
        arrival_time = env.now
        
        with self.resource.request() as req:
            yield req
            
            # Queue time
            wait_time = env.now - arrival_time
            self.total_wait_time += wait_time
            
            self.status = "running"
            
            # Processing time with some variation
            cycle_time = max(1.0, np.random.normal(self.cycle_time_mean, self.cycle_time_mean * 0.15))
            yield env.timeout(cycle_time)
            
            # Check for breakdown
            breakdown_prob = 1.0 / (self.mtbf_hours * 3600 / self.cycle_time_mean) if self.mtbf_hours else 0
            if np.random.random() < breakdown_prob:
                self.broken = True
                self.status = "broken"
                repair_time = self.mttr_hours * 3600
                yield env.timeout(repair_time)
                self.broken = False
                
            self.total_process_time += cycle_time
            self.total_processed += 1
            self.status = "idle"

class ProductionLine:
    """Manages the SimPy environment and stations."""
    def __init__(self, config_data: Dict[str, Any]):
        self.config = config_data
        self.stations: List[Station] = []
        self.env: Optional[simpy.Environment] = None
        
    def run_shift(self, shift_hours: float, demand: int, seed: Optional[int] = None) -> ShiftResult:
        if seed is not None:
            np.random.seed(seed)
            
        self.env = simpy.Environment()
        self.stations = [Station(self.env, s) for s in self.config.get("stations", [])]
        
        def job_generator(env: simpy.Environment, stations: List[Station]):
            job_id = 0
            while job_id < demand:
                # Arrival rate based on shift hours and demand
                interarrival = (shift_hours * 3600) / demand
                yield env.timeout(max(1.0, np.random.exponential(interarrival)))
                
                # Flow through stations sequentially
                env.process(process_through_line(env, stations, job_id))
                job_id += 1

        def process_through_line(env: simpy.Environment, stations: List[Station], job_id: int):
            for station in stations:
                yield env.process(station.process_job(env, job_id))

        self.env.process(job_generator(self.env, self.stations))
        
        total_time = shift_hours * 3600
        self.env.run(until=total_time)
        
        # Calculate metrics
        metrics = []
        for s in self.stations:
            util = min(1.0, s.total_process_time / total_time) if total_time > 0 else 0.0
            queue = len(s.resource.queue)
            avg_wait = s.total_wait_time / max(1, s.total_processed)
            metrics.append(StationMetric(
                id=s.id, name=s.name, name_ta=s.name_ta, utilization=util,
                queue_length=queue, wait_time_mean=avg_wait,
                is_bottleneck=False, status=s.status
            ))
            
        bottleneck = identify_bottleneck(metrics)
        if bottleneck:
            for m in metrics:
                if m.id == bottleneck.id:
                    m.is_bottleneck = True
                    
        # Throughput is determined by the last station
        throughput = self.stations[-1].total_processed if self.stations else 0
        lead_time = sum(m.wait_time_mean + s.cycle_time_mean for m, s in zip(metrics, self.stations))
        
        return ShiftResult(
            throughput=throughput,
            stations=metrics,
            bottleneck_id=bottleneck.id if bottleneck else -1,
            bottleneck_name=bottleneck.name if bottleneck else "",
            lead_time_mean=lead_time,
            shift_completion_pct=1.0
        )
