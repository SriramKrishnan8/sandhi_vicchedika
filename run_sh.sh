# For sandhi_vicchedika: Segmentation
#python3 sandhi_vicchedika.py WX roma sent first -t "kaSciwkAnwAvirahaguruNA svAXikArAwpramawwaH"
#python3 sandhi_vicchedika.py WX roma sent best -t "kaSciwkAnwAvirahaguruNA svAXikArAwpramawwaH"
#python3 sandhi_vicchedika.py DN deva sent first -t "कश्चित्कान्ताविरहगुरुणा स्वाधिकारात्प्रमत्तः"
#python3 sandhi_vicchedika.py WX roma word best -t "rAmAlayaH"
#python3 sandhi_vicchedika.py WX deva sent best -t "rAmAlayaH"
#python3 sandhi_vicchedika.py DN roma sent first -i sample_input_text_dev.txt -o sample_output_text_iast.txt
#python3 sandhi_vicchedika.py RN deva sent first -i sample_input_text_iast.txt
#python3 sandhi_vicchedika.py RN deva sent best -i sample_input_text_iast.txt -o sample_output_text_deva.txt
#python3 sandhi_vicchedika.py DN roma sent best -t "वैधर्म्याच्च न स्वप्नादिव' दित्यादिसूत्रेश्च विश्वस्य सत्यत्वप्रतिपादनादिति"
#python3 sandhi_vicchedika.py DN deva sent first -t "कश्चित्कान्ताविरहगुरुणा स्वाधिकारात्प्रमत्तः शापेनास्तङ्गमितमहिमा वर्षभोग्येन भर्तुः यक्षश्चक्रे जनकतनयास्नानपुण्योदकेषु स्निग्धच्छायतरुषु वसतिं रामगिर्याश्रमेषु"  for timeout

# For pada_vishleshika: Morphological Analysis
# python3 pada_vishleshika.py WX WX best -t "vi-balam"
# python3 pada_vishleshika.py WX WX best -t "rawnaXAwamam"
# python3 pada_vishleshika.py WX roma best -t "gacCawi"
# python3 pada_vishleshika.py WX roma best -t "vakrIBavawi"
# python3 pada_vishleshika.py WX deva best -t "gacMCawi"
# python3 pada_vishleshika.py DN WX best -t "त्व‍ा॒"
# python3 pada_vishleshika.py DN WX best -t "इन्द्रगाँ"
# python3 pada_vishleshika.py DN deva best -t "इन्द्रꣳ"
# python3 pada_vishleshika.py RN WX best -t "prāṇān"
# python3 pada_vishleshika.py DN deva best -t "वीडो इति"
# python3 pada_vishleshika.py DN deva best -t "अकः"
# python3 pada_vishleshika.py DN WX best -t "ते त्व‍ा॒ म॒न्थ॒न्तु॒ प्र॒जया॑ स॒ह इ॒ह गृ॒हा॒ण"
# python3 pada_vishleshika.py DN deva best -t "तन्वम्"
# python3 pada_vishleshika.py DN deva best -t "हितम्" -o dt_out_best.tsv
# python3 pada_vishleshika.py DN deva first -t "हितम्" -o dt_out_first.tsv
# python3 pada_vishleshika.py DN deva best -i sample_input_pada_dev.txt -o sample_padas_out.tsv
# python3 pada_vishleshika.py DN deva best -t "अजनिष्ठाः"
