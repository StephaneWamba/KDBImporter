#!/usr/bin/env python3
import os
import json
from typing import List, Optional
from dotenv import load_dotenv
from openai import OpenAI
from config import get_logger

logger = get_logger("Logger4ScrappingoQo", level="DEBUG")

# Load environment variables
load_dotenv() 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise EnvironmentError("OPENAI_API_KEY not set in environment")

client = OpenAI(api_key=OPENAI_API_KEY)

MODEL = "gpt-4o-mini"
MAX_TOKENS = 512
TEMPERATURE = 0.7


tags =[
    "Quantum Algorithm",
    "Quantum Key Distribution (QKD)",
    "Regulatory",
    "Standards",
    "Quantum Computing",
    "Quantum Hardware",
    "Quantum Communication",
    "Post Quantum Cryptography (PQC)",
    "Cybersecurity",
    "Cryptography",
    "Quantum Benchmarking",
    "Noisy Intermediate-Scale Quantum (NISQ)",
    "Quantum Error Correction",
    "IBM Qiskit",
    "Google Cirq",
    "Rigetti Forest, Quil",
    "Microsoft Q#, QDK",
    "Xanadu PennyLane",
    "Amazon Braket",
    "D-Wave Ocean SDK",
    "QuTiP",
    "ProjectQ",
    "OpenFermion",
    "Quantum Cloud Computing",
    "Quantum Networking",
    "Quantum AI",
    "Quantum Blockchain",
    "Quantum Ethics",
    "Quantum Supremacy and Advantage",
    "Quantum Programming Languages",
    "Quantum Operating Systems"
]

def metadata_generator(
    text: str,
    include_keywords: bool = True,
    include_tags: bool = True,
    include_categories: bool = False,
    available_tags: Optional[List[str]] = None,
    available_categories: Optional[List[str]] = None
) -> dict:
    """
    Use OpenAI to generate metadata fields for the given text, restricted to provided tag and category lists.

    Args:
        text: The document text content to process.
        available_tags: List of tag names the model may choose from.
        available_categories: List of category names the model may choose from.
        include_keywords: Whether to generate the 'Keywords' field.
        include_tags: Whether to generate the 'Tags' list.
        include_categories: Whether to generate the 'Categories' field.

    Returns:
        A dict containing only the requested metadata keys:
          - 'Keywords': A short, concise string of keywords (<=100 characters) relevant to quantum computing and cybersecurity.
          - 'Tags': A list of tag strings selected from available_tags, or empty if none fit.
          - 'Categories': A string selected from available_categories, or empty if none fit #deprectated- to be removed in future versions.
    """
    # Build system message with context
    system_content = (
        "You are a metadata extraction assistant specialized in quantum computing and quantum cybersecurity. "
        "Generate a JSON object containing only the requested fields. "
        "Valid keys are 'Keywords' (string), 'Tags' (array of strings) "
        f"The tags should correspond to the context of the text and must be choosen only in the list of {len(available_tags)} tags given, select the ones only revelant to our valid Tags."
        "Keywords must be short and concise (total length not exceed 100 characters). "
        "Respond with pure JSON and no additional text."
    )
    system_message = {"role": "system", "content": system_content}

    # Build user prompt with available choices
    request_info = []
    request_info.append(f"Include Keywords: {include_keywords}")
    if include_tags:
        request_info.append(f"Include Tags: {include_tags}. Available tags: {available_tags or []}")
    else:
        request_info.append(f"Include Tags: {include_tags}")
    if include_categories:
        request_info.append(f"Include Categories: {include_categories}. Available categories: {available_categories or []}")
    else:
        request_info.append(f"Include Categories: {include_categories}")
    user_content = "\n".join(request_info) + f"\n\nText to analyze:\n{text}"
    user_message = {"role": "user", "content": user_content}

    # Call chat completion
    response = client.chat.completions.create(
        model=MODEL,
        messages=[system_message, user_message],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown fences if present
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse JSON from model response: {raw}")
    return result



def read_lines_to_list(file_path):
    """
    Reads the given text file and returns a list where each entry
    is one line from the file (without the trailing newline).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.rstrip('\n') for line in f]

if __name__ == "__main__":
        
    text= '''
Quantum computers will do extraordinary things. They will create extremely complex digital twins at the molecular level and develop optimization solutions at the global level, allowing us to reshape whole industries, from pharmaceuticals to logistics.

But before we can see any of those benefits, we need a viable quantum computer that can solve hypercomplex problems. The quantum computers we have today can solve problems, but nothing an ordinary computer can’t handle. 

To take the next big leap in quantum computing, we need a stable qubit.

A qubit, or quantum bit, is the most fundamental building block of a quantum computer. It functions much like a transistor on a standard computer chip, but it can calculate in ways no traditional microprocessor ever could. Building a useful quantum computer would require entangling thousands of these qubits.
The problem is qubits are inherently unstable. The most infinitesimal shift in temperature, structure, or electromagnetic field can destabilize a qubit, turning any information it contains into useless noise. The life of most qubits today can be measured in mere milliseconds. 

Nokia Bell Labs, however, is researching a new type of qubit that is extremely stable. Called a topological qubit, it is much more resilient to external stimuli, allowing it to remain viable for a period of hours, if not days or weeks. This topological approach to quantum computing could be revolutionary, drastically reducing the size and cost of future quantum computers, as well as the resources necessary to maintain it. 
'''
    INCLUDE_PATH = os.environ.get("INCLUDE_PATH")
    # l_tag = read_lines_to_list(os.path.join(INCLUDE_PATH,"../tags.txt"))
    l_tags = available_tags
    # l_cat = read_lines_to_list(os.path.join(INCLUDE_PATH,"categories.txt"))
    logger.debug(metadata_generator(text, True, True, True, l_tag))