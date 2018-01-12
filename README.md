# Triple Pattern Fragment Profiler

The Triple Pattern Fragment Profiler is used to study the performance w.r.t. response time of Triple Pattern Fragments (TPFs). The profiler samples as set of triples from a given TPF and derives a set of triple patterns from those triples by replacing RDF terms with variables. Thereafter, these triple patterns are used to measure the response time of the TPF and record additional metadata. 

## Setup

Prerequisites:
- Unix-based OS (Linux / Mac OS)
- Python 2.7
- pip

Follow these steps to setup and run the profiler:
1. Download or clone this git repository
2. `cd tpf_profiler`
3. Install virtual environment package: `[sudo] pip install virtualenv`
4. Activate the virtual environment: `. venv/bin/activate`
5. Optional: Edit the `sources.json` to specify the mappings for TPF server pairs (local and remote)
6. See the command line tool options via `python run_study.py -h`
7. Use command line to run the profiler. E.g. `python run_study --url http://data.linkeddatafragments.org/dblp -s 10 -w 1`

Setting up the controlled Environment:
- Find the installation guide for setting up a local TPF server using Node.js [here](https://github.com/LinkedDataFragments/Server.js)
- HDT Files:
	* [DBLP](http://downloads.linkeddatafragments.org/hdt/dblp-20170124.hdt)
	* [DBpedia](http://downloads.linkeddatafragments.org/hdt/dbpedia2014_en_multi.hdt)
	* [GeoNames](http://downloads.linkeddatafragments.org/hdt/geonames-11-11-2012.hdt)
	* [Wiktionary](http://downloads.linkeddatafragments.org/hdt/wiktionary_en_2012-07-21.hdt)	

## Study Results

- The raw data of our study is provided freely available [here](https://figshare.com/articles/study_data_csv/5774163)

