[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1211622.svg)](https://doi.org/10.5281/zenodo.1211622)

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
6. See the command line tool options via `python run_study.py -h``

## Setting up the Experimental Settings

Setting up the controlled Environment:
- Find the installation guide for setting up a local TPF server using Node.js [here](https://github.com/LinkedDataFragments/Server.js)
- HDT Files:
	* [DBLP](http://downloads.linkeddatafragments.org/hdt/dblp-20170124.hdt)
	* [DBpedia](http://downloads.linkeddatafragments.org/hdt/dbpedia2014_en_multi.hdt)
	* [GeoNames](http://downloads.linkeddatafragments.org/hdt/geonames-11-11-2012.hdt)
	* [Wiktionary](http://downloads.linkeddatafragments.org/hdt/wiktionary_en_2012-07-21.hdt)	
- [HDT Tools](https://github.com/rdfhdt/hdt-cpp) for generating RDF files from HDT files
- [Virtuoso SPARQL Endpoint](https://virtuoso.openlinksw.com/dataspace/doc/dav/wiki/Main/VOSSparqlProtocol)

## Examples

Use command line to run the profiler and set the options to specify the profiler settings.
 
Example:  
`
- DBLP TPF with 10 samples and 1 run:

```bash
python run_study --url http://data.linkeddatafragments.org/dblp -s 10 -r -1
```


- DBpedia TPF with 100 samples, 2 runs and write the results to a CSV file:
`````bash
python run_study --url http://data.linkeddatafragments.org/dbpedia -s 100 -r -2 -w 1
`````



## How to Cite

````text
@misc{HelingTPFP2018,
  author = {Heling, Lars},
  title = {Triple Pattern Fragment Profiler},
  year = {2018},
  publisher = {GitHub},
  journal = {GitHub repository},
  doi = {\url{https://doi.org/10.5281/zenodo.1211622}},
  howpublished = {\url{https://github.com/Lars-H/tpf_profiler}}
  }
````


## Study Results

- The raw data create for the evaluation of TPF servers in our study is provided freely available [here](https://ndownloader.figshare.com/files/10991108) as a raw CSV file.
- The statistical analysis providing the basis for our evaluation is available in the `notebooks` directory as a Jupyter Notebook.
- The visulaizations for the publication is also provided in the `notebooks` directory 

## License

This work is licensed under [GNU/GPL v2](https://www.gnu.org/licenses/gpl-2.0.html).