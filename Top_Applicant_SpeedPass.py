import platform
from tempfile import TemporaryDirectory
from pathlib import Path
 
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import sys

import openai

with open('OPEN_AI_KEY.txt') as f:
    lines = f.readlines()
openai.api_key = lines[0]
model_engine = "text-davinci-003"
max_tokens = 3072

def get_resume_text(resume_file):
    PDF_file = Path(resume_file)
    image_file_list = []
    
    with TemporaryDirectory() as tempdir: # Create a temporary directory to hold our temporary images.
        pdf_dpi = 500
        pdf_pages = convert_from_path(PDF_file, pdf_dpi) # Read in the PDF file at set DPI

        for page_enumeration, page in enumerate(pdf_pages, start=1): # Iterate through all the pages stored above
            # enumerate() "counts" the pages for us.
            # Create a file name to store the image
            filename = f"{tempdir}\page_{page_enumeration:03}.jpg"

            # Declaring filename for each page of PDF as JPG
            # For each page, filename will be:
            # PDF page 1 -> page_001.jpg
            # Save the image of the page in system
            page.save(filename, "JPEG")
            image_file_list.append(filename)
    resume_text = ""
    for image_file in image_file_list:

        text = str(((pytesseract.image_to_string(Image.open(image_file)))))

        text = text.replace("-\n", "")
        text= text.replace("\n\n", "----")
        resume_text += text
    return resume_text

resumes = sys.argv[1:len(sys.argv)-1]
question = sys.argv[len(sys.argv) - 1]
def parse_all_resumes(resumes):
    res_text_compiled = ""
    for resume in resumes:
        curr = get_resume_text(resume)
        if len(curr) == 0:
            break
        curr = "----Begin Candidate:" + curr + "End Candidate----\n    "
        res_text_compiled += curr
    return res_text_compiled

def make_prompt(resumes, question):
    res_text_compiled = parse_all_resumes(resumes)
    prompt = "Given all those resumes marked with ----Begin Candidate: and End Candidate----\n assess" + question
    return prompt

prompt = make_prompt(resumes, question)
completion = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    max_tokens=max_tokens,
    temperature=0.5,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

print(completion.choices[0].text)
        


