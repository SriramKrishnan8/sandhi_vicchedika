#!/usr/bin/env python3

import os
import sys

import signal
import psutil

import subprocess as sp

import argparse

import re
import json

from tqdm import tqdm

import devtrans as dt


sentence_modes = {
    "sent" : "t",
    "word" : "f"
}

segmentation_modes = {
    "first" : "s",
    "best" : "l"
}

cgi_file = "./interface2"
    
svaras = [ '\uA8E1', '\uA8E2', '\uA8E3', '\uA8E4', '\uA8E5', '\uA8E6', '\uA8E7', '\uA8E8', '\uA8E9', '\uA8E0', '\uA8EA', '\uA8EB', '\uA8EC', '\uA8EE', '\uA8EF', '\u030D', '\u0951', '\u0952', '\u0953', '\u0954', '\u0945' ]

special_characters = [ '\uf15c', '\uf193', '\uf130', '\uf1a3', '\uf1a2', '\uf195', '\uf185', '\u200d', '\u200c', '\u1CD6', '\u1CD5', '\u1CE1', '\u030E', '\u035B', '\u0324', '\u1CB5', '\u0331', '\u1CB6', '\u032B', '\u0308', '\u030D', '\u0942', '\uF512', '\uF693', '\uF576', '\uF11E', '\u1CD1', '\u093C', '\uF697', '\uF6AA', '\uF692' ]

chandrabindu = [ '\u0310' ]

def remove_svaras(text):
    """ Removes svaras by iterating through the text
    """
    new_text = []
    for char in text:
        if char in (svaras + special_characters):
            continue
        new_text.append(char)
   
    modified_text = "".join(new_text)
    return modified_text


def handle_input(input_text, input_encoding):
    """ Modifies input based on the requirement of the Heritage Engine
    """
    
    # Remove svaras in the input text as these are not analysed 
    # properly by the Sanskrit Heritage Segmenter
    modified_input = remove_svaras(input_text)
    
    # Replace special characters with "." since Heritage Segmenter
    # does not accept special characters except "|", "!", "."
    modified_input = re.sub(r'[$@#%&*()\[\]=+:;"}{?/,\\।॥]', ' ', modified_input)
    if not (input_encoding == "RN"):
        modified_input = modified_input.replace("'", " ")
    
    # The following condition is added to replace chandrabindu
    # which comes adjacent to characters, with m or .m 
    # depending upon its position
    if input_encoding == "DN":
        chandrabindu = "ꣳ"
        if chandrabindu in modified_input:
            if modified_input[-1] == chandrabindu:
                modified_input = modified_input.replace("ꣳ", "म्")
            else:
                modified_input = modified_input.replace("ꣳ", "ं")
        else:
            pass
    else:
        pass
    
    normalized_input = re.sub(r'M$', 'm', modified_input)
    normalized_input = re.sub(r'\.m$', '.m', normalized_input)
    
    return normalized_input


def input_transliteration(input_text, input_enc):
    """ Converts input in any given notation to WX  
    """
    
    trans_input = ""
    trans_enc = ""
    
    if input_enc == "DN":
        trans_input = dt.dev2wx(input_text)
        trans_input = trans_input.replace("ळ", "d")
        trans_enc = "WX"
    elif input_enc == "RN":
        trans_input = dt.iast2wx(input_text)
        trans_enc = "WX"
    else:
        trans_input = input_text
        trans_enc = input_enc
        
    # The following condition makes sure that the other chandrabindu
    # which comes on top of other characters is replaced with m
    if "z" in trans_input:
        if trans_input[-1] == "z":
            trans_input = trans_input.replace("z", "m")
        else:
            trans_input = trans_input.replace("z", "M")
    
    return (trans_input, trans_enc)


def output_transliteration(output_text, output_enc):
    """ Converts the output which is always in WX to 
        deva or roma
    """
    
    trans_output = ""
    trans_enc = ""
    
    output_text = output_text.replace("#", "?")
    
    if output_enc == "deva":
        trans_output = dt.wx2dev(output_text)
        num_map = str.maketrans('०१२३४५६७८९', '0123456789')
        trans_output = trans_output.translate(num_map)
        trans_enc = "deva"
    elif output_enc == "roma":
        trans_output = dt.wx2iast(output_text)
        trans_enc = "roma"
    else:
        trans_output = output_text
        trans_enc = output_enc
    
    return (trans_output, trans_enc)


def run_sh(cgi_file, input_text, input_encoding, lex="MW", sentence_mode="t",
            us="f", output_encoding="roma", segmentation_mode="l",
            pipeline="t"):
    """ Runs the cgi file with a given word/sentence.  
        
        Returns a JSON
    """
    
    time_out = 30
    
    out_enc = output_encoding if output_encoding in ["roma", "deva"] else "roma"
    
    env_vars = [
        "lex=" + lex,
        "st=" + sentence_mode,
        "us=" + us,
        "font=" + out_enc,
        "t=" + input_encoding,
        "text=" + input_text,#.replace(" ", "+"),
        "mode=" + segmentation_mode,
        "pipeline=" + pipeline
    ]
    
    query_string = "QUERY_STRING=\"" + "&".join(env_vars) + "\""
    command = query_string + " " + cgi_file
    
    try:
        p = sp.Popen(command, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
        outs, errs = p.communicate(timeout=time_out)
    except sp.TimeoutExpired:
        parent = psutil.Process(p.pid)
        for child in parent.children(recursive=True):
            child.terminate()
            parent.terminate()
        result = ""
        status = "Timeout"
    except Exception as e:
        result = ""
        status = "Failure"
    else:
        result = outs.decode('utf-8')
        status = "Success"
    
    return result, status
    

def handle_result(input_sent, result, status, output_encoding):
    """ Returns the results from the JSON
    """
    
    result_json = {}
    
    trans_input = output_transliteration(input_sent, output_encoding)[0]
    
    if status == "Success":
        try:
            result_str = result.split("\n")[-1]
            result_json = json.loads(result_str)
        except e:
            result_json = {}
    
        segs = result_json.get("segmentation", [ input_sent ])
        
        if "error" in segs[0]:
            trans_segs = [ "Error: " + trans_input ]
        else:
            trans_segs = [ output_transliteration(seg, output_encoding)[0] for seg in segs ]
    elif status == "Timeout":
        trans_segs = [ ("Timeout: " + trans_input) ]
    elif status == "Failure":
        trans_segs = [ ("Failure: " + trans_input) ]
    else:
        trans_segs = [ ("Unknown: " + trans_input) ]
    
    return trans_segs
    

def run_sh_text(cgi_file, input_sent, input_encoding, lex="MW",
                sentence_mode="t", us="f", output_encoding="roma",
                segmentation_mode="l", pipeline="t"):
    """ Handles segmentation for the given input sentence
    """
    
    # SH does not accept special characters in the input sequence.  
    # And it results errors if such characters are found.  
    # Uncomment the following to segment the sentence by ignoring  
    # the special characters.  Currently, the following is commented
    # and the same input is returned as the output.
    
    input_sent = handle_input(input_sent.strip(), input_encoding)
    
    trans_input, trans_enc = input_transliteration(input_sent, input_encoding)
    
    result, status = run_sh(
        cgi_file, trans_input, trans_enc, lex, sentence_mode, us,
        output_encoding, segmentation_mode, pipeline
    )
    
    segmentation = handle_result(input_sent, result, status, output_encoding)
    
    print(segmentation)


def run_sh_file(cgi_file, input_file, output_file, input_encoding, lex="MW",
                sentence_mode="t", us="f", output_encoding="roma",
                segmentation_mode="l", pipeline="t"):
    """ Handles segmentation for all the sentences in a file
    """

    try:
        ifile = open(input_file, 'r')
    except OSError as e:
        print(f"Unable to open {path}: {e}", file=sys.stderr)
        sys.exit(1)
        
    input_text = ifile.read()
    ifile.close()

    if input_text.strip() == "":
        print("Specified input file does not have any sentence.")
        sys.exit(1)
    
    t_i_text, t_i_enc = input_transliteration(input_text.strip(), input_encoding)
    i_list = [sent.split(".") for sent in t_i_text.split("\n")]
    i_list_flattened = [item.strip() for sublist in i_list for item in sublist]
    input_list = list(filter(None, i_list_flattened))
    
    output_list = []
    for i in tqdm(range(len(input_list))):
        input_sent = input_list[i].strip()
        
        # SH does not accept special characters in the input sequence.  
        # And it results errors if such characters are found.  
        # Uncomment the following to segment the sentence by ignoring  
        # the special characters.  Currently, the following is commented
        # and the same input is returned as the output.
        
        # input_sent = handle_input(input_sent.strip(), input_encoding)
        
        # print(input_sent)
        
        result, status = run_sh(
            cgi_file, input_sent, t_i_enc, lex, sentence_mode, us,
            output_encoding, segmentation_mode, pipeline
        )
        
        segmentation = handle_result(input_sent, result, status, output_encoding)
                
        output_list.append(segmentation)
    
    # delimiter = " . " if output_encoding == "roma" else " । "
    # Temporarily setting the output delimiter as newline
    delimiter = "\n"
    output_list_updated = [ ",".join(items) for items in output_list ]
    output_str = delimiter.join(output_list_updated)
    
    ofile = open(output_file, 'w')
    
    ofile.write(output_str)
    print("Output written to file: " + output_file)
    ofile.close()


def main():
    """ """
    
    # Parsing Arguments
    parser = argparse.ArgumentParser()
    
    # Mandatory Arguments
    parser.add_argument(
        "input_enc", default="WX",
        choices=["DN", "KH", "RN", "SL", "VH", "WX"],
        help="input encoding"
    )
    parser.add_argument(
        "output_enc", default="roma",
        choices=["deva", "roma", "WX"],
        help="output encoding"
    )
    parser.add_argument(
        "sent_mode", default="sent",
        choices=["sent", "word"],
        help="sentence / word segmentation"
    )
    parser.add_argument(
        "seg_mode", default="first",
        choices=["first", "best"],
        help="first - first solution; or best - best (10) solutions"
    )
    
    # Options (one of -t or -i, -o is mandatory)
    parser.add_argument(
        "-t", "--input_text", type=str,
        help="input string"
    )
    parser.add_argument(
        "-i", "--input_file", type=argparse.FileType('r', encoding='UTF-8'),
        help="reads from file if specified"
    )
    parser.add_argument(
        "-o", "--output_file", type=argparse.FileType('w', encoding='UTF-8'),
        help="for writing to file"
    )
    
    args = parser.parse_args()
    
    if args.input_file and args.input_text:
        print("Please specify either input text ('-t') or input file ('-i, -o')")
        sys.exit()
    
    input_enc = args.input_enc
    output_enc = args.output_enc
    sent_mode = sentence_modes.get(args.sent_mode, "t")
    seg_mode = segmentation_modes.get(args.seg_mode, "s")
    
    if args.input_file:
        i_file = args.input_file.name
        o_file = args.output_file.name if args.output_file else "output.txt"
        run_sh_file(
            cgi_file, i_file, o_file, input_enc, lex="MW",
            sentence_mode=sent_mode, us="f", output_encoding=output_enc,
            segmentation_mode=seg_mode, pipeline="t"
        )
    elif args.input_text:
        run_sh_text(
            cgi_file, args.input_text, input_enc, lex="MW",
            sentence_mode=sent_mode, us="f", output_encoding=output_enc,
            segmentation_mode=seg_mode, pipeline="t"
        )
    else:
        print("Please specify one of text ('-t') or file ('-i & -o')")
        sys.exit()
    

if __name__ == "__main__":
    main()
