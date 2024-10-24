import openai
import json
import os
from constants import *

# Set up OpenAI API Key
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to split text into chunks based on token limits
def split_text_into_chunks(text, max_chunk_size=1000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_chunk_size = 0

    for word in words:
        current_chunk.append(word)
        current_chunk_size += len(word) + 1  # Adding 1 for space
        if current_chunk_size >= max_chunk_size:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_chunk_size = 0

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

# Function to analyze a single chunk of chat for service needs
def analyze_chat_chunk(chunk, service_types):
    # Use OpenAI's GPT to analyze chat content using the correct chat-completions endpoint
    prompt = (f"The following is a group chat conversation. Identify if any user is seeking help related to the following services: "
              f"{', '.join(service_types)}. The users may not explicitly mention these services directly but might describe issues, damage, or problems "
              f"they might describe issues such as "
              f"something being broken, damaged, malfunctioning, in need of repair, installation, or help. "
              f"Your task is to infer their needs based on the context. "
              f"Look for mentions of issues or problems, even if the service is not directly mentioned. For example, "
              f"if someone has his solar plates broken, infer that they need solar panel services. "
              f"Similarly, if someone mentions that their CCTV isn't working or has been damaged, infer that they need CCTV services. "
              f"if someone is ill, sick or unwell, infer that they need doctor. "
              f"Also, understand related terms or synonyms. For example, 'solar plate' may refer to solar panels, "
              f"and 'AC' could imply air conditioning services. " 
              f"and there could be wrong spellings of some words such as brocken instead of broken, damagd instead of damaged, so you have to "
              f"correctly understand the meaning of the conversation. "
              f"Sometimes group member chat with group mates and tell them about his problem so also trace such problems so that we can provide helpful suggessions to them. "
              f"trace those conversations in which we can give some helpful suggessions to user. "
              f"Sometimes the context will be related to attachments of the things such as 'the stand of bridge is broken', infer that they need welder not AC/Fridge service. "
              f"Provide the user_id and the inferred service they need. The conversation is: \n\n{chunk}\n\n"
              f"Output the result as a JSON object where the keys are the user_id and the values are the services they need.")
    
    response = openai.chat.completions.create(
        model="gpt-4",  # Change to 'gpt-3.5-turbo' if necessary
        messages=[
            {"role": "system", "content": "You are a helpful assistant who carefully tracs person who may need some help or assistance using prompt details"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

# Function to analyze chat and extract service needs
def analyze_chat_for_services(chat_file):
    # Predefined list of services to identify
    service_types = services
    
    # Read chat file
    with open(chat_file, 'r') as file:
        chat_content = file.read()

    # Split chat content into smaller chunks to avoid token limits
    chunks = split_text_into_chunks(chat_content)

    # Initialize a list to hold the results
    all_results = []

    # Process each chunk
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1} of {len(chunks)}...")
        result_text = analyze_chat_chunk(chunk, service_types)
        
        # Attempt to convert response to JSON
        try:
            result_json = json.loads(result_text)
            all_results.append(result_json)
        except json.JSONDecodeError:
            print(f"Failed to parse GPT response for chunk {i + 1}. Raw output:", result_text)
            continue
    
    all_results = format_list(all_results)
    return all_results

def analyze_chat_text(chat_text):
    # Predefined list of services to identify
    service_types = services
    
    # Initialize a list to hold the results
    all_results = []

    # Analyze the entire chat text
    result_text = analyze_chat_chunk(chat_text, service_types)
    
    # Attempt to convert response to JSON
    try:
        result_json = json.loads(result_text)
        all_results.append(result_json)
    except json.JSONDecodeError:
        print("Failed to parse GPT response. Raw output:", result_text)
    
    all_results = format_list(all_results)
    return all_results


def format_list(dicts_list):
    # Initialize an empty dictionary to store the result
    merged_dict = {}

    # Iterate over each dictionary in the input list
    for d in dicts_list:
        for key, value in d.items():
            # Ensure the key is in the merged_dict, if not, initialize with an empty list
            if key not in merged_dict:
                merged_dict[key] = []
            
            # If the value is a list, extend the list, otherwise append the single value
            if isinstance(value, list):
                merged_dict[key].extend(value)
            else:
                merged_dict[key].append(value)

    return merged_dict

