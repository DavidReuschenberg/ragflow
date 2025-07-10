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

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

from rag.nlp import find_codec


class RAGFlowXmlParser:
    def __init__(
        self, 
        max_chunk_size: int = 2000,
        min_chunk_size: int = 200,
        preserve_structure: bool = True,
        target_elements: List[str] = None
    ):
        """
        Initialize XML parser for hierarchical chunking.
        
        Args:
            max_chunk_size: Maximum size for chunks in characters
            min_chunk_size: Minimum size for chunks in characters
            preserve_structure: Whether to preserve XML structure information
            target_elements: List of element names to treat as chunk boundaries (e.g., ['paragraph', 'section'])
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.preserve_structure = preserve_structure
        self.target_elements = target_elements or ['paragraph', 'section', 'article', 'item', 'entry']
    
    def __call__(self, filename: Optional[str] = None, binary: Optional[bytes] = None) -> List[str]:
        """
        Parse XML document and return hierarchical chunks.
        
        Args:
            filename: Path to XML file (if not using binary)
            binary: Binary content of XML file
            
        Returns:
            List of text chunks that respect XML structure
        """
        if binary:
            encoding = find_codec(binary)
            xml_content = binary.decode(encoding, errors="ignore")
        else:
            with open(filename, 'r', encoding='utf-8') as f:
                xml_content = f.read()
        
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            # If XML parsing fails, fall back to treating as text with basic structure
            return self._fallback_parsing(xml_content)
        
        sections = self._extract_hierarchical_sections(root)
        return sections
    
    def _extract_hierarchical_sections(self, root: ET.Element) -> List[str]:
        """
        Extract sections from XML while preserving hierarchical structure.
        """
        sections = []
        
        # Process root element
        current_section = self._process_element(root, level=0)
        if current_section.strip():
            sections.append(current_section)
        
        # Process child elements recursively
        for child in root:
            child_sections = self._process_element_recursively(child, level=1)
            sections.extend(child_sections)
        
        # Merge small sections and split large ones
        return self._optimize_sections(sections)
    
    def _process_element_recursively(self, element: ET.Element, level: int = 0) -> List[str]:
        """
        Process XML element and its children recursively.
        """
        sections = []
        
        # Check if this element should be treated as a chunk boundary
        if element.tag.lower() in [tag.lower() for tag in self.target_elements]:
            # This element and its children form a chunk
            element_text = self._element_to_text(element, level)
            if element_text.strip():
                sections.append(element_text)
        else:
            # Process element content
            element_content = self._get_element_content(element, level)
            if element_content.strip():
                sections.append(element_content)
            
            # Process children
            for child in element:
                child_sections = self._process_element_recursively(child, level + 1)
                sections.extend(child_sections)
        
        return sections
    
    def _process_element(self, element: ET.Element, level: int = 0) -> str:
        """
        Process a single element and return its text representation.
        """
        return self._element_to_text(element, level)
    
    def _element_to_text(self, element: ET.Element, level: int = 0) -> str:
        """
        Convert XML element to text representation with structure preservation.
        """
        lines = []
        
        # Add element information if preserving structure
        if self.preserve_structure and element.tag:
            indent = "  " * level
            tag_info = f"{indent}[{element.tag}"
            
            # Add important attributes
            important_attrs = ['id', 'type', 'name', 'class', 'title']
            attrs = []
            for attr in important_attrs:
                if attr in element.attrib:
                    attrs.append(f"{attr}='{element.attrib[attr]}'")
            
            if attrs:
                tag_info += f" {' '.join(attrs)}"
            tag_info += "]"
            lines.append(tag_info)
        
        # Add element text
        if element.text and element.text.strip():
            text = element.text.strip()
            if self.preserve_structure:
                indent = "  " * (level + 1)
                lines.append(f"{indent}{text}")
            else:
                lines.append(text)
        
        # Process children
        for child in element:
            child_text = self._element_to_text(child, level + 1)
            if child_text.strip():
                lines.append(child_text)
            
            # Add tail text if exists
            if child.tail and child.tail.strip():
                tail_text = child.tail.strip()
                if self.preserve_structure:
                    indent = "  " * (level + 1)
                    lines.append(f"{indent}{tail_text}")
                else:
                    lines.append(tail_text)
        
        return "\n".join(lines)
    
    def _get_element_content(self, element: ET.Element, level: int = 0) -> str:
        """
        Get the direct text content of an element (not including children).
        """
        content_parts = []
        
        if element.text and element.text.strip():
            content_parts.append(element.text.strip())
        
        # Add attributes as context if they contain meaningful information
        if element.attrib:
            attr_text = []
            for key, value in element.attrib.items():
                if key.lower() in ['title', 'description', 'name', 'type'] and value.strip():
                    attr_text.append(f"{key}: {value}")
            
            if attr_text:
                if self.preserve_structure:
                    content_parts.append(f"[{', '.join(attr_text)}]")
                else:
                    content_parts.extend(attr_text)
        
        return " ".join(content_parts)
    
    def _optimize_sections(self, sections: List[str]) -> List[str]:
        """
        Optimize sections by merging small ones and splitting large ones.
        """
        optimized = []
        current_section = ""
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # If adding this section would exceed max_chunk_size, finalize current section
            if current_section and len(current_section) + len(section) > self.max_chunk_size:
                if len(current_section) >= self.min_chunk_size:
                    optimized.append(current_section)
                    current_section = section
                else:
                    # Current section is too small, but adding would be too big
                    # Split the new section and add part to current
                    remaining_space = self.max_chunk_size - len(current_section)
                    if remaining_space > 100:  # Only if meaningful space left
                        split_point = self._find_split_point(section, remaining_space)
                        current_section += "\n" + section[:split_point]
                        optimized.append(current_section)
                        current_section = section[split_point:].strip()
                    else:
                        optimized.append(current_section)
                        current_section = section
            else:
                # Safe to add to current section
                if current_section:
                    current_section += "\n" + section
                else:
                    current_section = section
        
        # Add final section
        if current_section.strip():
            if len(current_section) > self.max_chunk_size:
                # Split large final section
                split_sections = self._split_large_section(current_section)
                optimized.extend(split_sections)
            else:
                optimized.append(current_section)
        
        return [section for section in optimized if len(section.strip()) >= self.min_chunk_size]
    
    def _find_split_point(self, text: str, max_length: int) -> int:
        """
        Find a good point to split text, preferring sentence or line boundaries.
        """
        if len(text) <= max_length:
            return len(text)
        
        # Try to split at sentence boundaries
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        best_split = 0
        
        for ending in sentence_endings:
            pos = text.rfind(ending, 0, max_length)
            if pos > best_split:
                best_split = pos + len(ending)
        
        if best_split > 0:
            return best_split
        
        # Try to split at line boundaries
        line_pos = text.rfind('\n', 0, max_length)
        if line_pos > 0:
            return line_pos + 1
        
        # Try to split at word boundaries
        space_pos = text.rfind(' ', 0, max_length)
        if space_pos > 0:
            return space_pos + 1
        
        # Last resort: hard cut
        return max_length
    
    def _split_large_section(self, section: str) -> List[str]:
        """
        Split a section that's too large into smaller chunks.
        """
        chunks = []
        remaining = section
        
        while len(remaining) > self.max_chunk_size:
            split_point = self._find_split_point(remaining, self.max_chunk_size)
            chunk = remaining[:split_point].strip()
            if chunk:
                chunks.append(chunk)
            remaining = remaining[split_point:].strip()
        
        if remaining:
            chunks.append(remaining)
        
        return chunks
    
    def _fallback_parsing(self, xml_content: str) -> List[str]:
        """
        Fallback parsing when XML structure can't be parsed.
        """
        # Remove XML tags but preserve structure
        text_lines = []
        lines = xml_content.split('\n')
        
        for line in lines:
            # Remove XML tags but keep the content
            clean_line = re.sub(r'<[^>]+>', ' ', line).strip()
            if clean_line:
                text_lines.append(clean_line)
        
        # Join lines and split into reasonable chunks
        full_text = '\n'.join(text_lines)
        return self._split_large_section(full_text) 