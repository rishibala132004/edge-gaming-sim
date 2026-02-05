# edge-gaming-sim
Edge Gaming Simulator

Built a simulator for multiplayer gaming on edge nodes. Used real Enchede/Hengelo network maps. 

Key numbers:
- Got latency down to <3ms  
- 99.9% fairness score (Jain's index)
- Handled ~30M tasks total

What I did:
- Mixed fast/slow edge servers
- Compared round-robin vs capacity scheduling
- Measured latency vs energy trade-offs

Files:
main.py = main simulator
results/ = graphs from MintEDGE runs

Tech: Python, MintEDGE, edge computing
