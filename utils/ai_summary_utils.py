import tiktoken
from tqdm import tqdm
from typing import List, Optional, Tuple


def tokenize(text: str) -> List[str]:
    encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    return encoding.encode(text)


def chunk_on_delimiter(input_string: str,
                       max_tokens: int,
                       delimiter: str) -> List[str]:
    chunks = input_string.split(delimiter)
    combined_chunks, _, dropped_chunk_count = combine_chunks_with_no_minimum(
        chunks, max_tokens, chunk_delimiter=delimiter,
        add_ellipsis_for_overflow=True
    )
    if dropped_chunk_count > 0:
        print(f"warning: {dropped_chunk_count}"
              "chunks were dropped due to overflow")
    combined_chunks = [f"{chunk}{delimiter}" for chunk in combined_chunks]
    return combined_chunks


def combine_chunks_with_no_minimum(
        chunks: List[str],
        max_tokens: int,
        chunk_delimiter="\n\n",
        header: Optional[str] = None,
        add_ellipsis_for_overflow=False,
) -> Tuple[List[str], List[int]]:
    dropped_chunk_count = 0
    output = []  # list to hold the final combined chunks
    output_indices = []  # list to hold the indices of the combined chunks
    candidate = (
        [] if header is None else [header]
    )  # list to hold the current combined chunk candidate
    candidate_indices = []
    for chunk_i, chunk in enumerate(chunks):
        chunk_with_header = [chunk] if header is None else [header, chunk]
        if len(tokenize(chunk_delimiter.join(chunk_with_header))) > max_tokens:
            print("warning: chunk overflow")
            if (
                    add_ellipsis_for_overflow
                    and len(tokenize(
                        chunk_delimiter.join(
                            candidate + ["..."]))) <= max_tokens
            ):
                candidate.append("...")
                dropped_chunk_count += 1
            continue  # this case would break downstream assumptions
        # estimate token count with the current chunk added
        extended_candidate_token_count = len(tokenize(
            chunk_delimiter.join(candidate + [chunk])))
        # If the token count exceeds max_tokens,
        # add the current candidate to output and start a new candidate
        if extended_candidate_token_count > max_tokens:
            output.append(chunk_delimiter.join(candidate))
            output_indices.append(candidate_indices)
            candidate = chunk_with_header  # re-initialize candidate
            candidate_indices = [chunk_i]
        # otherwise keep extending the candidate
        else:
            candidate.append(chunk)
            candidate_indices.append(chunk_i)
    # add the remaining candidate to output if it's not empty
    if (header is not None and len(candidate) > 1)\
            or (header is None and len(candidate) > 0):
        output.append(chunk_delimiter.join(candidate))
        output_indices.append(candidate_indices)
    return output, output_indices, dropped_chunk_count


def get_chat_completion(messages, client, model='deepseek-chat'):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def summarize(text: str,
              client,
              detail: float = 0,
              model: str = 'deepseek-chat',
              additional_instructions: Optional[str] = None,
              minimum_chunk_size: Optional[int] = 500,
              chunk_delimiter: str = ".",
              summarize_recursively=False,
              verbose=False,
              ):

    # check detail is set correctly
    assert 0 <= detail <= 1

    # interpolate the number of chunks based to get specified level of detail
    max_chunks = len(chunk_on_delimiter(text,
                                        minimum_chunk_size, chunk_delimiter))
    min_chunks = 1
    num_chunks = int(min_chunks + detail * (max_chunks - min_chunks))

    # adjust chunk_size based on interpolated number of chunks
    document_length = len(tokenize(text))
    chunk_size = max(minimum_chunk_size, document_length // num_chunks)
    text_chunks = chunk_on_delimiter(text, chunk_size, chunk_delimiter)
    if verbose:
        print(f"Splitting the text into {len(text_chunks)}"
              " chunks to be summarized.")
        print(f"Chunk lengths are {[len(tokenize(x)) for x in text_chunks]}")

    # set system message

    system_message_content = """Summarize the following public company
    disclosure in Indonesian. The summary must adhere to these rules:

1.  **Language:** Indonesian.
2.  **Format:** Use standard paragraph structure primarily. Avoid text
formatting like **bold** or *italics*. Using lists (e.g., bullet points) is
acceptable if appropriate for clarity or summarizing specific points.
Multiple paragraphs are acceptable, but keep the overall summary concise.
3.  **Length:** Concise and strictly under 1000 characters in total across all
paragraphs and list items. Do not mention the character
 limit in the generated summary.
4.  **Stock Code:** If a stock code is mentioned in the document
(e.g., BBCA, TLKM), include *only* the stock code in the summary,
not the full company name associated with it.
5.  **Exclusions:** Do not include any information about:
    * Signatories of the document.
    * The intended recipient(s) of the document.
    * The document type (e.g., electronic submission, physical letter).
    * The company's address or contact information (phone, fax, email).
6.  **Output Purity:** The output must contain *only* the summary content
itself. Do not include any additional notes, explanations,
or commentary about the summarization process, how the rules were followed,
 or what was excluded
 (e.g., avoid phrases like *"Ringkasan ini disusun sesuai permintaan..."*
 or *"Detail X tidak disertakan..."*).

"""
    if additional_instructions is not None:
        system_message_content += f"\n\n{additional_instructions}"

    accumulated_summaries = []
    for chunk in tqdm(text_chunks):
        if summarize_recursively and accumulated_summaries:
            # Creating a structured prompt for recursive summarization
            accumulated_summaries_string = '\n\n'.join(accumulated_summaries)
            user_message_content = "Previous summaries:\n\n"
            f"{accumulated_summaries_string}\n\n"
            f"Text to summarize next:\n\n{chunk}"
        else:
            # Directly passing the chunk for summarization
            #  without recursive context
            user_message_content = chunk

        # Constructing messages based on whether recursive
        # summarization is applied
        messages = [
            {"role": "system", "content": system_message_content},
            {"role": "user", "content": user_message_content}
        ]

        # Assuming this function gets the completion and works as expected
        response = get_chat_completion(messages, model=model, client=client)
        accumulated_summaries.append(response)

    # Compile final summary from partial summaries
    final_summary = '\n\n'.join(accumulated_summaries)

    return final_summary
