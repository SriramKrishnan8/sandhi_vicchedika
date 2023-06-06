#!/usr/bin/env python3

import os
import sys
import subprocess as sp

import argparse

import re
import json

#import devtrans as dt
from devconvert import dev2wx, dev2slp, iast2slp, slp2iast, slp2wx, slp2dev, wx2slp, slp2tex


sentence_modes = {
    "sent" : "t",
    "word" : "f"
}

segmentation_modes = {
    "first" : "s",
    "best" : "l"
}

cgi_file = "./interface2"


def wx2dev(text):
    """
    """
    
    return slp2dev.convert(wx2slp.convert(text))
    

def iast2wx(text):
    """
    """
    
    return slp2wx.convert(iast2slp.convert(text))
    

def wx2iast(text):
    """
    """
    
    return slp2iast.convert(wx2slp.convert(text))
    

def handle_input(input_text, input_encoding):
    """ Modifies input based on the requirement of the Heritage Engine
    """
    
    # Replace special characters with "." since Heritage Segmenter
    # does not accept special characters except "|", "!", "."
    modified_input = re.sub(r'[$@#%&*()\[\]=+:;"}{?/,\\]', ' ', input_text)
    if not (input_encoding == "RN"):
        modified_input = modified_input.replace("'", " ")
    
    normalized_input = re.sub(r'M$', 'm', modified_input)
    normalized_input = re.sub(r'\.m$', '.m', normalized_input)
    
    return normalized_input


def input_transliteration(input_text, input_enc):
    """ Converts input in any given notation to WX  
    """
    
    trans_input = ""
    trans_enc = ""
    
    if input_enc == "DN":
        trans_input = dev2wx.convert(input_text)
        trans_enc = "WX"
    elif input_enc == "RN":
        trans_input = iast2wx(input_text)
        trans_enc = "WX"
    else:
        trans_input = input_text
        trans_enc = input_enc
    
    return (trans_input, trans_enc)


def output_transliteration(output_text, output_enc):
    """ Converts the output which is always in WX to 
        deva or roma
    """
    
    trans_output = ""
    trans_enc = ""
    
    if output_enc == "deva":
        trans_output = wx2dev(output_text)
        trans_enc = "deva"
    elif output_enc == "roma":
        trans_output = wx2iast(output_text)
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
    
    p = sp.Popen(command, stdout=sp.PIPE, shell=True)
    try:
        outs, errs = p.communicate(timeout=time_out)
    except sp.TimeoutExpired:
        kill(p.pid)
        result = ""
    else:
        result = outs.decode('utf-8')
    
    return result
    

def handle_result(result):
    """ Returns the results from the JSON
    """
    
    result_json = {}
    status = "Failure"
    
    if result:
        try:
            result_str = result.split("\n")[-1]
            result_json = json.loads(result_str)
            status = "Success"
        except e:
            result_json = {}
    else:
        status = "Timeout"
    
    return (status, result_json)


def get_segmentations(input_text, result, out_enc):
    """ Returns the results from the JSON
    """
    
    result_json = {}
    
    if result:
        try:
            result_str = result.split("\n")[-1]
            result_json = json.loads(result_str)
        except e:
            result_json = {}
    
    results = result_json.get("segmentation", [])
    segs = results if results else [ input_text ]
    
    segs_2 = [ input_text ] if "error" in segs[0] else segs
    
    segmentations = [output_transliteration(x, out_enc)[0] for x in segs_2]
    
    return segmentations
    

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
    
    result = run_sh(
        cgi_file, trans_input, trans_enc, lex, sentence_mode, us,
        output_encoding, segmentation_mode, pipeline
    )
    
    segmentations = get_segmentations(input_sent, result, output_encoding)
    
    print(segmentations)


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
    for i in range(len(input_list)):
        input_sent = input_list[i].strip()
        
        # SH does not accept special characters in the input sequence.  
        # And it results errors if such characters are found.  
        # Uncomment the following to segment the sentence by ignoring  
        # the special characters.  Currently, the following is commented
        # and the same input is returned as the output.
        
        # input_sent = handle_input(input_sent.strip(), input_encoding)
        
        print(input_sent)
        
        result = run_sh(
            cgi_file, input_sent, t_i_enc, lex, sentence_mode, us,
            output_encoding, segmentation_mode, pipeline
        )
        
        status, result_json = handle_result(result)
        
        if status in ["Failure", "Timeout"]:
            segs = [ input_sent ]
        else:
            segs = result_json.get("segmentation", [ input_sent ])
        
        first = input_sent if "error" in segs[0] else segs[0]
        first_seg, out_enc = output_transliteration(first, output_encoding)
        output_list.append(first_seg)
    
    # delimiter = " . " if output_encoding == "roma" else " । "
    # Temporarily setting the output delimiter as newline
    delimiter = "\n"
    output_str = delimiter.join(output_list)
    
    ofile = open(output_file, 'w')
    
    ofile.write(output_str)
    print("\nOutput written to file: " + output_file)
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
