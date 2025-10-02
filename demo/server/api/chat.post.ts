import { streamText, UIMessage, convertToModelMessages, tool } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import { z } from 'zod';

const JAGUAR_API_URL = 'http://localhost:8000';

const ripgrepTool = tool({
  description: 'Search for text patterns in uploaded documents using ripgrep. Use this to find specific content, keywords, or regex patterns within documents.',
  inputSchema: z.object({
    pattern: z.string().describe('The text or regex pattern to search for'),
    file_id: z.string().optional().describe('Optional file ID to search within a specific file'),
    case_sensitive: z.boolean().optional().default(false).describe('Whether the search should be case sensitive'),
    context: z.number().optional().default(0).describe('Number of context lines to show around matches (0-10)'),
  }),
  execute: async ({ pattern, file_id, case_sensitive, context }) => {
    try {
      const params = new URLSearchParams({
        pattern,
        case_sensitive: case_sensitive?.toString() || 'false',
        context: context?.toString() || '0',
      });

      if (file_id) {
        params.append('file_id', file_id);
      }

      const response = await $fetch(`${JAGUAR_API_URL}/search/ripgrep/?${params}`);
      return {
        success: true,
        pattern,
        file_id,
        total_matches: response.total_matches,
        results: response.results,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        pattern,
        file_id,
      };
    }
  }
});

const findTool = tool({
  description: 'Search for files by name patterns, file types, or size filters in the processed documents directory.',
  inputSchema: z.object({
    name_pattern: z.string().optional().describe('File name pattern to search for (e.g., "*.md", "*.json")'),
    file_type: z.enum(['f', 'd', '']).optional().describe('File type filter: "f" for files, "d" for directories, empty for any'),
    size: z.string().optional().describe('File size filter (e.g., "+1M" for files larger than 1MB, "-100k" for files smaller than 100KB)'),
  }),
  execute: async ({ name_pattern, file_type, size }) => {
    try {
      const params = new URLSearchParams();

      if (name_pattern) params.append('name_pattern', name_pattern);
      if (file_type) params.append('file_type', file_type);
      if (size) params.append('size', size);

      const response = await $fetch(`${JAGUAR_API_URL}/search/find/?${params}`);
      return {
        success: true,
        search_parameters: response.search_parameters,
        results: response.results,
        count: response.count,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        search_parameters: { name_pattern, file_type, size },
      };
    }
  }
});

const jqTool = tool({
  description: 'Query JSON metadata of uploaded documents using JQ expressions. Use this to extract specific information from document structure and metadata.',
  inputSchema: z.object({
    file_id: z.string().describe('The file ID to query metadata for'),
    jq_filter: z.string().describe('JQ filter expression (e.g., "length", ".[].category", ".[] | select(.category == \\"Title\\")")'),
  }),
  execute: async ({ file_id, jq_filter }) => {
    try {
      const params = new URLSearchParams({
        file_id,
        jq_filter,
      });

      const response = await $fetch(`${JAGUAR_API_URL}/search/jq/?${params}`);
      return {
        success: true,
        file_id,
        jq_filter,
        result: response.result,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        file_id,
        jq_filter,
      };
    }
  }
});

const listFilesTool = tool({
  description: 'List all uploaded files with their metadata. Use this to see what files are available for searching.',
  inputSchema: z.object({}),
  execute: async () => {
    try {
      const response = await $fetch(`${JAGUAR_API_URL}/files/`);
      return {
        success: true,
        files: response.files.map((file: any) => ({
          file_id: file.file_id,
          filename: file.original_filename,
          size: file.size,
          status: file.processing_result?.status,
          element_count: file.processing_result?.element_count,
        })),
        total_count: response.files.length,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }
});

const getFileInfoTool = tool({
  description: 'Get detailed information about a specific uploaded file, including processing results and content preview.',
  inputSchema: z.object({
    file_id: z.string().describe('The file ID to get information for'),
  }),
  execute: async ({ file_id }) => {
    try {
      const response = await $fetch(`${JAGUAR_API_URL}/files/${file_id}`);
      return {
        success: true,
        file_info: {
          file_id: response.file_id,
          filename: response.original_filename,
          size: response.size,
          content_type: response.content_type,
          processing_status: response.processing_result?.status,
          element_count: response.processing_result?.element_count,
          content_preview: response.processing_result?.content_preview,
        },
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        file_id,
      };
    }
  }
});

export default defineLazyEventHandler(async () => {
  const apiKey = useRuntimeConfig().openaiApiKey;
  if (!apiKey) throw new Error('Missing OpenAI API key');
  const openai = createOpenAI({
    apiKey: apiKey,
  });

  return defineEventHandler(async (event: any) => {
    const { messages }: { messages: UIMessage[] } = await readBody(event);

    console.log(messages);

    const result = streamText({
      model: openai('gpt-4o'),
      messages: convertToModelMessages(messages),
      tools: {
        ripgrep: ripgrepTool,
        find: findTool,
        jq: jqTool,
        listFiles: listFilesTool,
        getFileInfo: getFileInfoTool,
      },
    });

    return result.toUIMessageStreamResponse();
  });
});