# MOOSQE - Repository

Ideas on multi-objective optimization for federated SPARQL query engines.


## Notes

Potential directions:
- Source selection: 
	* Latencies for large federations (e.g. all available web sources)
	* Triple Pattern Fragments endpoints
	* --> Observing latency cost for triple pattern fragments	

- Profiler:
	* Triple patterns to estimate the cost must be derived from the source
	* Idea: Sample constants (for predicates, uris, literals) by randomly selecting triple from the sources (via ?s ?p ?o)
	* Based on the sampled constants, generate a test set of triple patterns