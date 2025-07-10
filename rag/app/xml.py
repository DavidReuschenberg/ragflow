#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import logging
import re

from deepdoc.parser import XmlParser
from rag.nlp import rag_tokenizer, tokenize_chunks


def chunk(filename, binary=None, from_page=0, to_page=100000,
          lang="Chinese", callback=None, **kwargs):
    """
    Supported file formats: XML files.
    This method applies hierarchical XML parsing to chunk files while preserving XML structure.
    XML elements are parsed and organized into chunks that respect the document hierarchy.
    """
    
    callback(0.1, "Start to parse XML.")
    
    # DEBUG: Check what we're receiving
    logging.info(f"XML chunker called with filename={filename}, binary_type={type(binary)}, binary_is_none={binary is None}")
    if binary is not None:
        logging.info(f"Binary length: {len(binary)}")
    
    # Get parser configuration
    parser_config = kwargs.get("parser_config", {})
    
    # XML-specific configuration
    chunk_token_num = int(parser_config.get("chunk_token_num", 512))
    preserve_structure = parser_config.get("preserve_structure", True)
    target_elements = parser_config.get("target_elements", [
        "paragraph", "section", "article", "item", "entry", "cost", "calculation", 
        "fee", "procedure", "diagnosis", "treatment", "p", "div", "span"
    ])
    
    # Initialize document metadata
    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
    }
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])
    
    # Initialize XML parser with configuration
    xml_parser = XmlParser(
        max_chunk_size=chunk_token_num * 4,  # Rough character to token ratio
        min_chunk_size=max(chunk_token_num // 4, 50),
        preserve_structure=preserve_structure,
        target_elements=target_elements
    )
    
    try:
        # Parse XML file
        logging.info(f"About to call XML parser with filename={filename}, binary={binary is not None}")
        sections = xml_parser(filename, binary)
        callback(0.6, "XML parsing completed.")
        
        if not sections:
            callback(-1, "No content extracted from XML file.")
            return []
        
        # Convert sections to tuples for processing
        sections = [(section, "") for section in sections if section.strip()]
        
        callback(0.8, "Structuring chunks.")
        
        # Determine if content is English
        is_english = lang.lower() == "english"
        
        # Create chunks using the standard tokenization process
        chunks = []
        for section_text, _ in sections:
            if len(section_text.strip()) > 0:
                chunks.append(section_text)
        
        callback(0.9, "Finalizing chunks.")
        
        # Use standard tokenization
        result = tokenize_chunks(chunks, doc, is_english)
        
        callback(1.0, "XML chunking completed.")
        logging.info(f"XML chunking completed for {filename}: {len(result)} chunks created")
        
        return result
        
    except Exception as e:
        error_msg = f"Error processing XML file {filename}: {str(e)}"
        logging.error(error_msg)
        callback(-1, error_msg)
        raise 