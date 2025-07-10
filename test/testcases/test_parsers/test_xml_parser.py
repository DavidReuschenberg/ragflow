import os
import sys
from pathlib import Path

import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class TestXMLParser:
    """Test cases for the XML parser functionality"""
    
    @pytest.fixture
    def sample_xml_path(self):
        """Path to the sample XML file"""
        return project_root / "test" / "sample_data" / "xml_documents" / "judicial_cost_calculation.xml"
    
    @pytest.fixture
    def sample_xml_content(self, sample_xml_path):
        """Load sample XML content"""
        with open(sample_xml_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def sample_xml_binary(self, sample_xml_path):
        """Load sample XML as binary"""
        with open(sample_xml_path, 'rb') as f:
            return f.read()
    
    def test_xml_parser_import(self):
        """Test that XML parser can be imported"""
        try:
            from deepdoc.parser import XmlParser
            assert XmlParser is not None
        except ImportError as e:
            pytest.skip(f"Could not import XmlParser: {e}")
    
    def test_xml_parser_initialization(self):
        """Test XML parser initialization with different parameters"""
        try:
            from deepdoc.parser import XmlParser

            # Test default initialization
            parser = XmlParser()
            assert parser.max_chunk_size == 2000
            assert parser.min_chunk_size == 200
            assert parser.preserve_structure == True
            assert 'paragraph' in parser.target_elements
            
            # Test custom initialization
            custom_parser = XmlParser(
                max_chunk_size=1000,
                min_chunk_size=100,
                preserve_structure=False,
                target_elements=['cost', 'procedure']
            )
            assert custom_parser.max_chunk_size == 1000
            assert custom_parser.min_chunk_size == 100
            assert custom_parser.preserve_structure == False
            assert custom_parser.target_elements == ['cost', 'procedure']
            
        except ImportError as e:
            pytest.skip(f"Could not import XmlParser: {e}")
    
    def test_xml_parser_with_sample_file(self, sample_xml_path, sample_xml_binary):
        """Test XML parser with the sample judicial XML file"""
        try:
            from deepdoc.parser import XmlParser
            
            parser = XmlParser()
            
            # Test parsing from binary
            sections = parser(binary=sample_xml_binary)
            assert isinstance(sections, list)
            assert len(sections) > 0
            
            # Test parsing from file path
            sections_from_file = parser(filename=str(sample_xml_path))
            assert isinstance(sections_from_file, list)
            assert len(sections_from_file) > 0
            
            # Content should be similar (though may not be identical due to processing)
            assert len(sections) == len(sections_from_file)
            
        except ImportError as e:
            pytest.skip(f"Could not import XmlParser: {e}")
    
    def test_xml_parser_content_extraction(self, sample_xml_binary):
        """Test that XML parser extracts meaningful content"""
        try:
            from deepdoc.parser import XmlParser
            
            parser = XmlParser(target_elements=['procedure', 'cost_calculation', 'paragraph'])
            sections = parser(binary=sample_xml_binary)
            
            # Should extract multiple sections
            assert len(sections) >= 3
            
            # Check for expected content in sections
            all_content = ' '.join(sections)
            
            # Should contain medical procedure information
            assert 'Initial Consultation' in all_content or 'consultation' in all_content.lower()
            assert 'cost' in all_content.lower() or 'fee' in all_content.lower()
            assert 'procedure' in all_content.lower() or 'treatment' in all_content.lower()
            
            # Should contain cost calculation information
            assert any('180.00' in section or '325.00' in section or '600.00' in section for section in sections)
            
        except ImportError as e:
            pytest.skip(f"Could not import XmlParser: {e}")
    
    def test_xml_chunk_function(self, sample_xml_path):
        """Test the XML chunk function"""
        try:
            from rag.app import xml

            # Test callback functionality
            callback_messages = []
            def test_callback(progress, message):
                callback_messages.append((progress, message))
            
            # Test chunking
            chunks = xml.chunk(
                filename=str(sample_xml_path),
                callback=test_callback,
                lang='English',
                parser_config={
                    'chunk_token_num': 512,
                    'preserve_structure': True,
                    'target_elements': ['procedure', 'cost_calculation', 'paragraph']
                }
            )
            
            # Should have called callback
            assert len(callback_messages) > 0
            assert any(msg[1] == 'XML chunking completed.' for msg in callback_messages)
            
            # Should return list of chunk dictionaries
            assert isinstance(chunks, list)
            assert len(chunks) > 0
            
            # Each chunk should have expected keys
            for chunk in chunks:
                assert isinstance(chunk, dict)
                assert 'content_with_weight' in chunk
                assert 'docnm_kwd' in chunk
                assert 'title_tks' in chunk
            
            # Should contain expected content
            all_chunk_content = ' '.join(chunk['content_with_weight'] for chunk in chunks)
            assert 'cost' in all_chunk_content.lower() or 'fee' in all_chunk_content.lower()
            
        except ImportError as e:
            pytest.skip(f"Could not import xml module: {e}")

if __name__ == "__main__":
    pytest.main([__file__]) 