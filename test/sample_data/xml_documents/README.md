# XML Sample Documents

This directory contains sample XML documents used for testing the XML parser functionality in RAGFlow.

## Files

### judicial_cost_calculation.xml

A sample XML document representing judicial data for medical cost calculations. This file demonstrates the hierarchical structure typical of legal/medical documentation with:

- **Document metadata** (header, patient info)
- **Medical procedures** with nested cost calculations
- **Fee summaries** with itemized breakdowns
- **Legal notes** with paragraph structures

The document structure includes various XML elements that are commonly used as chunk boundaries:
- `procedure` - Individual medical procedures
- `cost_calculation` - Cost breakdown sections
- `paragraph` - Text paragraphs in legal notes
- `section` - Organizational sections
- `item` - Individual fee items

## Usage in Tests

This sample data is used by the XML parser tests located in `test/testcases/test_parsers/test_xml_parser.py` to verify:

1. **Parser functionality** - Basic XML parsing and content extraction
2. **Hierarchical chunking** - Respecting XML document structure when creating chunks
3. **Target elements** - Using specific XML elements as chunk boundaries
4. **Structure preservation** - Maintaining XML tag information in chunks
5. **Error handling** - Graceful handling of malformed XML

## Adding New Test Files

When adding new XML test files:

1. Use meaningful filenames that describe the document type
2. Include a variety of XML structures and nesting levels
3. Add test cases in the parser test file to cover new scenarios
4. Document the purpose and structure of new files in this README

## XML Structure Guidelines

For optimal testing, XML documents should include:

- Multiple levels of nesting
- Various element types (containers, text content, attributes)
- Elements suitable for use as chunk boundaries
- Content that can be meaningfully extracted and indexed
- Real-world document structures representative of target use cases 