## For sandhi_vicchedika: Segmentation
#python3 sandhi_vicchedika.py WX roma sent first -t "kaSciwkAnwAvirahaguruNA svAXikArAwpramawwaH"
#python3 sandhi_vicchedika.py WX roma sent best -t "kaSciwkAnwAvirahaguruNA svAXikArAwpramawwaH"
#python3 sandhi_vicchedika.py DN deva sent first -t "कश्चित्कान्ताविरहगुरुणा स्वाधिकारात्प्रमत्तः"
#python3 sandhi_vicchedika.py WX roma word best -t "rAmAlayaH"
#python3 sandhi_vicchedika.py WX deva sent best -t "rAmAlayaH"
#python3 sandhi_vicchedika.py DN roma sent first -i sample_input_text_dev.txt -o sample_output_text_iast.txt
#python3 sandhi_vicchedika.py RN deva sent first -i sample_input_text_iast.txt
#python3 sandhi_vicchedika.py RN deva sent best -i sample_input_text_iast.txt -o sample_output_text_deva.txt
#python3 sandhi_vicchedika.py DN roma sent best -t "वैधर्म्याच्च न स्वप्नादिव' दित्यादिसूत्रेश्च विश्वस्य सत्यत्वप्रतिपादनादिति"
#python3 sandhi_vicchedika.py DN deva sent first -t "कश्चित्कान्ताविरहगुरुणा स्वाधिकारात्प्रमत्तः शापेनास्तङ्गमितमहिमा वर्षभोग्येन भर्तुः यक्षश्चक्रे जनकतनयास्नानपुण्योदकेषु स्निग्धच्छायतरुषु वसतिं रामगिर्याश्रमेषु"  # for timeout

## For sandhi_vicchedika_vedic: Segmentation (Vedic) # NOTE: to be modified according sandhi_vicchedika.py
#python3 sandhi_vicchedika_vedic.py DN deva sent best -t "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम् । होतारं रत्नधातमम् ॥"
#python3 sandhi_vicchedika_vedic.py DN deva sent first -t "अग्निमीळे पुरोहितं यज्ञस्य देवमृत्विजम् । होतारं रत्नधातमम् ॥"
#python3 sandhi_vicchedika_vedic.py DN deva sent first -t "अ॒ग्निमी॑ळे पु॒रोहि॑तं य॒ज्ञस्य॑ दे॒वमृ॒त्विज॑म् । होता॑रं रत्न॒धात॑मम् ॥"

## For pada_vishleshika: Morphological Analysis
#python3 pada_vishleshika.py WX WX word best -t "vi-balam"
#python3 pada_vishleshika.py WX WX word best -t "rawnaXAwamam"
#python3 pada_vishleshika.py WX roma word best -t "gacCawi"
#python3 pada_vishleshika.py WX roma word best -t "vakrIBavawi"
#python3 pada_vishleshika.py WX deva word best -t "gacMCawi"
#python3 pada_vishleshika.py DN WX word best -t "त्व‍ा॒"
#python3 pada_vishleshika.py DN WX word best -t "इन्द्रगाँ"
#python3 pada_vishleshika.py DN deva word best -t "इन्द्रꣳ"
#python3 pada_vishleshika.py RN WX word best -t "prāṇān"
#python3 pada_vishleshika.py DN deva word best -t "वीडो इति"
#python3 pada_vishleshika.py DN deva word best -t "अकः"
#python3 pada_vishleshika.py DN WX sent best -t "ते त्व‍ा॒ म॒न्थ॒न्तु॒ प्र॒जया॑ स॒ह इ॒ह गृ॒हा॒ण"
#python3 pada_vishleshika.py DN deva word best -t "तन्वम्"
python3 pada_vishleshika.py DN deva word best -t "हितम्" -o dt_out_best.tsv
python3 pada_vishleshika.py DN deva word first -t "हितम्" -o dt_out_first.tsv
#python3 pada_vishleshika.py DN deva word best -i sample_input_pada_dev.txt -o sample_padas_out.tsv
#python3 pada_vishleshika.py DN deva word best -t "अजनिष्ठाः"
