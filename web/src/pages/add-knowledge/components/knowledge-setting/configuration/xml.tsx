import {
  AutoKeywordsItem,
  AutoQuestionsItem,
} from '@/components/auto-keywords-item';
import { DatasetConfigurationContainer } from '@/components/dataset-configuration-container';
import MaxTokenNumber from '@/components/max-token-number';
import PageRank from '@/components/page-rank';
import ParseConfiguration from '@/components/parse-configuration';
import GraphRagItems from '@/components/parse-configuration/graph-rag-items';
import { useTranslate } from '@/hooks/common-hooks';
import { Card, Checkbox, Divider, Form, Input, Select, Tag } from 'antd';
import { TagItems } from '../tag-item';
import { ChunkMethodItem, EmbeddingModelItem } from './common-item';

const { TextArea } = Input;

export function XmlConfiguration() {
  const { t } = useTranslate('dataset');

  const defaultTargetElements = [
    'paragraph',
    'section',
    'article',
    'item',
    'entry',
    'cost',
    'calculation',
    'fee',
    'procedure',
    'diagnosis',
    'treatment',
    'p',
    'div',
    'span',
  ];

  return (
    <section className="space-y-4 mb-4">
      <DatasetConfigurationContainer>
        <EmbeddingModelItem></EmbeddingModelItem>
        <ChunkMethodItem></ChunkMethodItem>
        <MaxTokenNumber></MaxTokenNumber>

        <Form.Item
          label="Preserve XML Structure"
          name={['parser_config', 'preserve_structure']}
          valuePropName="checked"
          initialValue={true}
          tooltip="Whether to preserve XML element structure information in chunks"
        >
          <Checkbox>Include XML tag information in chunks</Checkbox>
        </Form.Item>

        <Form.Item
          label="Target Elements"
          name={['parser_config', 'target_elements']}
          initialValue={defaultTargetElements}
          tooltip="XML element names that should be treated as chunk boundaries. Each of these elements will form separate chunks."
        >
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="Enter XML element names (e.g., paragraph, section, cost)"
            tokenSeparators={[',']}
            options={defaultTargetElements.map((element) => ({
              label: element,
              value: element,
            }))}
          />
        </Form.Item>
      </DatasetConfigurationContainer>

      <Divider></Divider>

      <DatasetConfigurationContainer>
        <PageRank></PageRank>
        <AutoKeywordsItem></AutoKeywordsItem>
        <AutoQuestionsItem></AutoQuestionsItem>
        <TagItems></TagItems>
      </DatasetConfigurationContainer>

      <Divider></Divider>

      <DatasetConfigurationContainer>
        <ParseConfiguration></ParseConfiguration>
      </DatasetConfigurationContainer>

      <Divider></Divider>

      <GraphRagItems></GraphRagItems>

      <Card title="XML Parsing Help" size="small" style={{ marginTop: 16 }}>
        <div className="text-sm text-gray-600">
          <p>
            <strong>Target Elements:</strong> Specify XML element names that
            should be treated as natural chunk boundaries. For judicial
            documents with cost calculations, consider elements like:
          </p>
          <div style={{ marginTop: 8 }}>
            {[
              'cost',
              'calculation',
              'fee',
              'procedure',
              'diagnosis',
              'treatment',
            ].map((element) => (
              <Tag key={element} color="blue" style={{ margin: 2 }}>
                {element}
              </Tag>
            ))}
          </div>
          <p style={{ marginTop: 8 }}>
            <strong>Preserve Structure:</strong> When enabled, XML tag
            information will be included in chunks to maintain context about the
            document structure.
          </p>
        </div>
      </Card>
    </section>
  );
}
