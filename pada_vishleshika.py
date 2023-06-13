import os
import sys
import subprocess as sp

import argparse

import re
import json

# import devtrans as dt
from devconvert import dev2wx, dev2slp, iast2slp, slp2iast, slp2wx, slp2dev, wx2slp, slp2tex
# Import roots when deeper roots are required
# import roots as rt


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
        trans_out = wx2dev(output_text)
        num_map = str.maketrans('०१२३४५६७८९', '0123456789')
        trans_output = trans_out.translate(num_map)
        trans_enc = "deva"
    elif output_enc == "roma":
        trans_output = wx2iast(output_text)
        trans_enc = "roma"
    else:
        trans_output = output_text
        trans_enc = output_enc
    
    return (trans_output, trans_enc)


def run_sh(cgi_file, input_text, input_encoding, lex="MW", us="f",
           output_encoding="roma", segmentation_mode="b", stemmer="t"):
    """ Runs the cgi file with a given word.  
        
        Returns a JSON
    """
    
    time_out = 30
    
    out_enc = output_encoding if output_encoding in ["roma", "deva"] else "roma"
    
    env_vars = [
        "lex=" + lex,
        "us=" + us,
        "font=" + out_enc,
        "t=" + input_encoding,
        "text=" + input_text,#.replace(" ", "+"),
        "mode=" + segmentation_mode,
        "stemmer=" + stemmer
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


def identify_stem_root(d_stem, base, d_morph, i_morphs):
    """ The output JSON object keys derived_stem and base are modified
        to stem and root based on the inflectional and derivational
        morphological analyses
    """

    root = ""
    stem = ""

    verb_identifiers = [
        "pr.", "imp.", "opt.", "impft.", "inj.", "subj.", "pft.", "plp.",
        "fut.", "cond." "aor.", "ben.", "abs.", "inf."
    ]

    noun_identifiers = [
        "nom.", "acc.", "i.", "dat.", "abl.", "g.", "loc.", "voc.", "iic.",
        "iiv.", "part.", "prep.", "conj.", "adv.", "tasil", "ind."
    ]

    if d_morph:
        root = base
        stem = d_stem
    else:
        morph_keys = " ".join(i_morphs).split(" ")
        for m in morph_keys:
            if m in verb_identifiers:
                root = d_stem
                break
            if m in noun_identifiers:
                stem = d_stem
                
                # The following conditions are present for stems which
                # are derived from roots but SH does not produce a 
                # derivational morphological analysis
                # if d_stem in rt.sh_roots:
                #     root = d_stem
                # elif d_stem.split("#")[0] in rt.scl_roots:
                #     root = d_stem.split("#")[0]
                # else:
                #     stem = d_stem
                break
    
    return (root, stem)


def get_morphological_analyses(input_out_enc, result_json, out_enc):
    """ Returns the results from the JSON
    """
    
    analysis_json = {}

    seg = result_json.get("segmentation", [])
    morphs = result_json.get("morph", [])

    if morphs:
        new_morphs = []

        for m in morphs:
            word = m.get("word", "")
            d_stem = m.get("derived_stem", "")
            base = m.get("base", "")
            d_morph = m.get("derivational_morph", "")
            i_morphs = m.get("inflectional_morphs", [])

            root, stem = identify_stem_root(d_stem, base, d_morph, i_morphs)
            
            new_item = {}
            new_item["word"] = output_transliteration(word, out_enc)[0]
            new_item["stem"] = output_transliteration(stem, out_enc)[0]
            new_item["root"] = output_transliteration(root, out_enc)[0]
            new_item["derivational_morph"] = d_morph
            new_item["inflectional_morphs"] = i_morphs

            new_morphs.append(new_item)
        
        words = [output_transliteration(wrd, out_enc)[0] for wrd in seg]
        analysis_json["input"] = input_out_enc
        analysis_json["status"] = "success"
        analysis_json["segmentation"] = words
        analysis_json["morph"] = new_morphs

    return analysis_json
    

def handle_result(result, input_word, output_enc):
    """ Returns the results from the JSON
    """
    
    result_json = {}
    status = "Failure"

    # print(result)

    if result:
        try:
            result_str = result.split("\n")[-1]
            result_json = json.loads(result_str)
        except e:
            result_json = {}
    else:
        status = "Timeout"
    
    seg = result_json.get("segmentation", [])
    morphs = result_json.get("morph", [])

    if not morphs and not seg:
        status = "Unknown Anomaly"
    elif seg:
        if "error" in seg[0]:
            status = "Error"
        elif "#" in seg[0]:
            status = "Unrecognized"
        else:
            status = "Success"
    else:
        status = "Unknown Anomaly"

    morph_analysis = {}
    
    input_out_enc = output_transliteration(input_word, output_enc)[0]
    if status in ["Failure", "Timeout", "Unknown Anomaly"]:
        morph_analysis["input"] = input_out_enc
        morph_analysis["status"] = "failed"
    elif status == "Error":
        morph_analysis["input"] = input_out_enc
        morph_analysis["status"] = "error"
        morph_analysis["error"] = seg[0]
    elif status == "Unrecognized":
        morph_analysis["input"] = input_out_enc
        morph_analysis["status"] = "unrecognized"
    else: # Success
        morph_analysis = get_morphological_analyses(input_out_enc, result_json, output_enc)
    
    return morph_analysis


def run_sh_text(cgi_file, input_word, input_encoding, lex="MW",
                us="f", output_encoding="roma",
                segmentation_mode="b", stemmer="t"):
    """ Handles morphological analyses for the given input word
    """
    
    # SH does not accept special characters in the input sequence.  
    # And it results errors if such characters are found.  
    # Uncomment the following to find the morphological analyses of the
    # word by ignoring the special characters.  
    
    i_word = handle_input(input_word.strip(), input_encoding)
    
    trans_input, trans_enc = input_transliteration(i_word, input_encoding)
    
    result = run_sh(
        cgi_file, trans_input, trans_enc, lex, us, output_encoding, 
        segmentation_mode, stemmer
    )
    
    morph_analysis = handle_result(result, input_word, output_encoding)
    
    print(json.dumps(morph_analysis, ensure_ascii=False))


def run_sh_file(cgi_file, input_file, output_file, input_encoding, lex="MW",
                us="f", output_encoding="roma", segmentation_mode="b",
                stemmer="t"):
    """ Handles morphological analyses for all the sentences in a file
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
    i_list = [word for word in t_i_text.split("\n")]
    input_list = list(filter(None, i_list))
    
    output_list = []
    for i in range(len(input_list)):
        input_word = input_list[i].strip()
        
        # SH does not accept special characters in the input sequence.  
        # And it results errors if such characters are found.  
        # Uncomment the following to get the morphological analysis of
        # the word by ignoring the special characters.  
        
        # input_word = handle_input(input_word.strip(), input_encoding)
        
        print(output_transliteration(input_word, output_encoding)[0])
        
        result = run_sh(
            cgi_file, input_word, t_i_enc, lex, us,
            output_encoding, segmentation_mode, stemmer
        )
        
        morph_analysis = handle_result(result, input_word, output_encoding)
        
        output_list.append(morph_analysis)
    
    with open(output_file, 'w', encoding='utf-8') as out_file:
        json.dump(output_list, out_file, ensure_ascii=False)


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
    seg_mode = segmentation_modes.get(args.seg_mode, "f")
    
    if args.input_file:
        i_file = args.input_file.name
        o_file = args.output_file.name if args.output_file else "output.txt"
        run_sh_file(
            cgi_file, i_file, o_file, input_enc, lex="MW",
            us="f", output_encoding=output_enc,
            segmentation_mode=seg_mode, stemmer="t"
        )
    elif args.input_text:
        run_sh_text(
            cgi_file, args.input_text, input_enc, lex="MW",
            us="f", output_encoding=output_enc,
            segmentation_mode=seg_mode, stemmer="t"
        )
    else:
        print("Please specify one of text ('-t') or file ('-i & -o')")
        sys.exit()
    

if __name__ == "__main__":
    main()