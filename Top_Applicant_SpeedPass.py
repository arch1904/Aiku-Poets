from tempfile import TemporaryDirectory
from pathlib import Path
 
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

import sys
import concurrent.futures

import openai

with open('OPEN_AI_KEY.txt') as f:
    lines = f.readlines()
openai.api_key = lines[0]

def get_resume_text(resume_file):
    """
    Worker Function Parse Single Resume PDF into text

    resume_file: str Filename

    returns str containing plaintext resume
    """
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

def parse_all_resumes(resumes):
    """
    Parse PDF resumes (image/text based) into text

    resumes: list [] : File names of the Resumes

    return a list [] of strings containing each resume in textformat per element
    """
    res_text_compiled = []
    for i in range(len(resumes)):
        resume = resumes[i]
        curr = get_resume_text(resume)
        if len(curr) == 0:
            continue 
        res_text_compiled.append(curr)
    return res_text_compiled

def summarize_resume(text_resume):
    """
    Summarize a single text resume using the text-davinci-003 model

    text_resume: str : Parsed resume in string format

    returns a str with the summary of the provided resume
    """
    model_engine_summary = "text-davinci-003"
    max_tokens = 1024
    prompt = "Summarize the following Text Resume: " + text_resume
    completion = openai.Completion.create(
        engine=model_engine_summary,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return completion.choices[0].text

def get_resume_summaries(text_resumes):
    """
    Multi-threaded calls to davinci model to parallelize summarization of resumes

    textresumes: list [] - containing text-resumes converted from pdfs per element

    returns a list [] of summaries for each corresponding textresume
    """
    summaries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        iterator = {executor.submit(summarize_resume, textresume): textresume for textresume in text_resumes}
        for i in concurrent.futures.as_completed(iterator):
            # full_resume = iterator[i]
            # summaries.append((full_resume,i.result()))
            summaries.append(i.result())

    return summaries

def assess_single_resume(text_resume, question_completion):
    """
    Use GPT3.5-Turbo to assess a candidates resume in regards to provided criteria
    Questions in the form of {Is this candidate a good fit for} user-input(for ex: a Marketing Manager Role? ***, given certain criteria*** optional)

    text_resume: str - plaintext format text-resume
    question_completion: str - question from user to assess on

    returns str containing GPT3.5-Turbo's assessment based on the given criteria
    """
    model_engine_assessment = "gpt-3.5-turbo"
    summary = summarize_resume(text_resume)

    response = openai.ChatCompletion.create(
    model = model_engine_assessment,
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Consider the following text-resume from a Candidate: " + summary},
            {"role": "user", "content": "Is this candidate a good fit for " + question_completion}
        ]
    )
    return response['choices'][0]['message']['content']

def generate_resume_messages(textresumes, question_completion):
    """
    Worker Function to Generate Messages in the Chat Completion format 

    text_resumes: list [] - list containing plaintext format text-resumes
    question_completion: str - question from user to assess on

    returns list [] of {}  containing messages formatted in the compatible format
    """
    base_sys_msg = "You are a helpful assistant."
    messages=[{"role": "system", "content": base_sys_msg}]
    summaries = get_resume_summaries(textresumes)
    for i in range(len(summaries)):
        messages.append({"role": "user", "content": "Consider the following text-resume from Candidate: " + str(i+1) +" " + summaries[i]}) #Format prompt, provide candidate id, and summary to bot
    
    messages.append({"role": "user", "content": "Given these candidates, which of these candidates is a good fit for " + question_completion})

    return messages
    
def assess_multiple_resumes(text_resumes ,question_completion):
    """
    Use GPT3.5-Turbo to assess a candidates resume in regards to provided criteria
    Questions in the form of {Is this candidate a good fit for} user-input(for ex: a Marketing Manager Role? ***, given certain criteria*** optional)

    text_resumes: list [] - list containing plaintext format text-resumes
    question_completion: str - question from user to assess on

    returns str containing GPT3.5-Turbo's assessment based on the given criteria
    """
    model_engine_assessment = "gpt-3.5-turbo"
    response = openai.ChatCompletion.create(
    model = model_engine_assessment,
    messages=generate_resume_messages(text_resumes, question_completion)
    )

    return response['choices'][0]['message']['content']

if __name__ == "__main__":
    resumes = sys.argv[1:len(sys.argv)-1]
    question = sys.argv[len(sys.argv) - 1]

    text_resumes = parse_all_resumes(resumes)
    if len(text_resumes > 1):
        print(assess_multiple_resumes(text_resumes, question))
    else:
        print(assess_single_resume(text_resumes[0], question))


