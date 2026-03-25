import simpy
import numpy as np
import statistics
import time


class Station:
    """A factory station with SimPy Resource-backed machines."""

    def __init__(self, env, station_config):
        self.env = env
        self.id = station_config.get('id', 0)
        self.name = station_config.get('name', 'Station')
        self.name_ta = station_config.get('name_ta', '')
        self.num_machines = station_config.get('num_machines', 1)
        self.cycle_time_mean = station_config.get('cycle_time_sec', 60.0)
        self.mtbf = station_config.get('mtbf_hours', 10.0) * 3600.0
        self.mttr = station_config.get('mttr_hours', 1.0) * 3600.0
        self.variability = station_config.get('variability', 0.15)
        
        self.resource = simpy.PriorityResource(env, capacity=self.num_machines)
        self.jobs_completed = 0
        self.wait_times = []
        self.cycle_times = []
        self.busy_time = 0.0
        self.breakdowns = 0
        self.down_time = 0.0
        self.current_status = 'running'
        
        # Start breakdown process
        self.env.process(self._breakdown_loop())

    def _breakdown_loop(self):
        """Simulate machines breaking down and being repaired."""
        while True:
            # Time until next breakdown
            yield self.env.timeout(np.random.exponential(self.mtbf / max(self.num_machines, 1)))
            
            # Request a machine to 'break'
            with self.resource.request(priority=-1) as req:
                yield req
                self.breakdowns += 1
                self.current_status = 'broken'
                
                repair_time = np.random.normal(self.mttr, self.mttr * 0.3)
                repair_time = max(60.0, repair_time)
                
                yield self.env.timeout(repair_time)
                self.down_time += repair_time
                self.current_status = 'running'

    def process_job(self, job_id):
        arrival_time = self.env.now
        
        with self.resource.request() as req:
            yield req
            
            wait_time = self.env.now - arrival_time
            self.wait_times.append(wait_time)
            
            # Variability: Apply variability to cycle time using normal distribution
            import random
            actual_cycle = random.gauss(self.cycle_time_mean, self.cycle_time_mean * self.variability)
            actual_cycle = max(actual_cycle, self.cycle_time_mean * 0.5)
            self.cycle_times.append(actual_cycle)
            
            yield self.env.timeout(actual_cycle)
            self.busy_time += actual_cycle
            self.jobs_completed += 1

    def get_metrics(self, sim_duration):
        util = min(self.busy_time / max(sim_duration * self.num_machines, 1.0), 0.999)
        avg_wait = statistics.mean(self.wait_times) if self.wait_times else 0.0
        
        # Little's Law: L = lambda * W
        # lambda (arrival rate) approx = jobs_completed / sim_duration
        arrival_rate = len(self.wait_times) / max(sim_duration, 1.0)
        avg_queue = arrival_rate * avg_wait

        return {
            'station_id': self.id,
            'station_name': self.name,
            'station_name_ta': self.name_ta,
            'utilization': round(util, 4),
            'jobs_completed': self.jobs_completed,
            'status': self.current_status,
            'breakdowns': self.breakdowns,
            'avg_queue': avg_queue,
            'cycle_time_sec': self.cycle_time_mean,
            'num_machines': self.num_machines
        }


def run_replications(config_dict, demand, shift_hours, condition, n_reps=100):
    """Run simulation n_reps times for Monte Carlo analysis."""
    throughputs = []
    all_station_metrics_list = []
    
    for rep in range(n_reps):
        np.random.seed(rep * 42 + 7)
        env = simpy.Environment()
        shift_seconds = shift_hours * 3600.0
        
        stations = [Station(env, sc) for sc in config_dict.get('stations', [])]
        if not stations: continue
        
        inter_arrival = shift_seconds / max(demand, 1)
        
        def job_gen():
            for jid in range(demand):
                if env.now >= shift_seconds: break
                env.process(run_job(jid))
                gap = np.random.exponential(inter_arrival)
                yield env.timeout(gap)
        
        def run_job(job_id):
            for station in stations:
                yield env.process(station.process_job(job_id))
        
        env.process(job_gen())
        env.run(until=shift_seconds)
        
        throughputs.append(stations[-1].jobs_completed)
        all_station_metrics_list.append([s.get_metrics(shift_seconds) for s in stations])
    
    if not throughputs:
        return {'throughput_mean': 0, 'bottleneck_ids': [], 'station_metrics': [], 'replications': n_reps}

    tp_mean = statistics.mean(throughputs)
    
    # Identify MULTIPLE bottlenecks from the last replication or average
    last_metrics = all_station_metrics_list[-1]
    
    # Enrichment logic for Phase 2
    max_util = max(m['utilization'] for m in last_metrics) if last_metrics else 0.001
    shift_seconds = shift_hours * 3600.0
    
    enriched_metrics = []
    bottleneck_ids = []

    for m in last_metrics:
        utilization = m['utilization']
        # BNI (Bottleneck Intensity) = utilization / max(utilization across all stations)
        bni_score = utilization / max(max_util, 0.001)
        is_bottleneck = (utilization >= max_util and utilization > 0)
        
        if is_bottleneck:
            bottleneck_ids.append(m['station_id'])
            
        # daily_production_loss calculation:
        # max_capacity = (shift_seconds / cycle_time_sec) * num_machines
        # actual_output = max_capacity * utilization
        # daily_production_loss = max(0, int(demand - actual_output))
        
        ct = m.get('cycle_time_sec', 60.0)
        nm = m.get('num_machines', 1)
        max_cap = (shift_seconds / max(ct, 0.1)) * nm
        act_out = max_cap * utilization
        loss_u = max(0, int(demand - act_out))

        enriched_metrics.append({
            "station_id": m['station_id'],
            "station_name": m['station_name'],
            "utilization": round(utilization, 4),
            "queue_length": int(m.get('avg_queue', 0)),
            "status": m['status'],
            "is_bottleneck": bool(is_bottleneck),
            "bni": round(bni_score, 4),
            "daily_production_loss": int(loss_u),
            "throughput_contribution": round(float(m['jobs_completed']), 2)
        })

    return {
        'throughput_mean': round(tp_mean, 1),
        'bottleneck_ids': bottleneck_ids,
        'bottleneck_station_id': bottleneck_ids[0] if bottleneck_ids else -1,
        'station_metrics': enriched_metrics,
        'replications': n_reps
    }
