# Sandhi-Vicchedika - Sanskrit Sandhi Splitter (Powered by Sanskrit Heritage Engine)

The package contains binaries from [Sanskrit Heritage Engine (SH)](https://sanskrit.inria.fr/) and [Samsaadhanii Tools (SCL)](https://sanskrit.uohyd.ac.in/scl/) that aid and perform the morphological analysis of given word(s) and segmentation of given sentence(s). The following are the constituents:

1. interface2 &rarr; binary file from SH that performs segmentation and is invoked from pada\_vishleshika.py and sandhi\_vicchedika.py
2. data/ &rarr; contains all the required .rem files (binaries for interface2)
3. sandhi\_vicchedika.py &rarr; a python wrapper for segmentation of SH
4. pada\_vishleshika.py &rarr; a python wrapper for morphological analysis of SH
6. run.sh &rarr; sample commands to perform the segmentation task with various parameters
7. sample\_input\_text\_dev.txt, sample\_input\_text\_iast.txt, sample\_input\_pada\_dev.txt &rarr; sample input files

## Pre-requisites

1. ocaml, ocamlbuild, camlp4
    
    For Ubuntu 19.10 and older, install ocaml(4.07.1), ocamlbuild(0.14.0), camlp4(4.07.1). For Ubuntu 20.04 and later:
```
sudo apt install ocaml ocamlbuild camlp4
```
    
2. python3
3. devtrans (used for transliteration to and fro various notations, installed via pip)

```
pip3 install devtrans
```

## Instructions

To run sandhi\_vicchedika.py:

```
python3 sandhi_vicchedika.py <input_encoding> <output_encoding> <segmentation_mode> <result_mode> [-t text] [-i input_file] [-o output_file]
```

To run pada\_vishleshika.py:

```
python3 pada_vishleshika.py <input_encoding> <output_encoding> <result_mode> [-t text] [-i input_file] [-o output_file]
```

Options for:
* input\_encoding &rarr; WX, DN, RN, SL, KH, VH
* output\_encoding &rarr; deva, roma
* segmentation_mode &rarr; word, sent
* result_mode &rarr; first, best

Examples are provided in run.sh

## Output format

sandhi\_vicchedika &rarr; list of segmentations 

pada\_vishleshika

* input 
* status &rarr; ["success", "failed", "error", "unrecognized"]
* segmentation
* morph
    * word &rarr; pada
    * derived\_stem &rarr; stem / prātipadika
    * base &rarr; root / dhātu
    * derivational\_morph 
    * inflectional\_morphs &rarr; list of analyses


## To be Noted

This is an experimental version of the Sanskrit Heritage Segmenter which ranks the best possible solutions from the results of the original Segmenter. The ranking is based on the statistics derived from [Digital Corpus of Sanskrit (DCS)](http://www.sanskrit-linguistics.org/dcs/). Hence, the first segmentation solution need not always be the intended segmentation. In such cases the result\_mode "best" can be used which ranks the best 10 segmentations based on the statistics. 

pada\_vishleshika generates all the possible morphological analysis of given word(s) and ranks them using the ranking mentioned above.

The Heritage Segmenter has certain limitations. It does not accept the special characters except "-", ".", "|" and "!". While "-" is a compound constituents separator and "." & "|" are accepted as sentence separators, "!" is suffixed to vocative nouns (referring sambodhana) like "raama! iti". It is necessary to remove all other characters before running the segmenter. Another limitation is with respect to Out Of Vocabulary words. A "#" is added as a prefix to indicate the unrecognized chunks in the output.

In case of any clarification, suggestion or correction, please contact: sriramk8@gmail.com
