# Factory Digital Twin — Debugging Prompts

If you encounter issues during execution, use these prompts to help diagnose the problem with your AI assistant.

## General Issues
"The system is crashing on startup. Here is the traceback: [PASTE TRACEBACK]. The factory config used is [PASTE CONFIG NAME]. What is causing this?"

## SimPy Simulation Issues
"The simulation is running, but the throughput is zero. The factory is configured for 8 hours with 200 demand. Here is `lathe_default.json`. Why are the machines not processing jobs?"

"The bottleneck detection `calc_bottleneck_index` is identifying Station 1, but Station 3 clearly has a longer line. Here are the utilization and Lq numbers: [PASTE NUMBERS]. Is my BNI formula weighting Lq incorrectly?"

## Unity WebSocket Issues
"Unity connects to ws://127.0.0.1:8765 but does not receive any state updates. The Python terminal shows 'Unity client connected'. Why is `async def _broadcast_loop` not sending the JSON?"

## FastAPI Issues
"The POST `/simulate` endpoint is timing out (taking more than 5 seconds) on my machine. I am running 30 replications. Should I reduce `n_reps` or is there a thread-blocking issue in `api_server.py`?"

## Real-Time ERP Issues
"The `CSVDataSource` is not picking up changes when I save `erp_template.csv`. The `watchdog` library is installed. Is it an issue with Windows file locking by Excel?"
