<img src="https://github.com/user-attachments/assets/c1e9073b-5a96-4a66-afa5-b7c4510cb9c3" alt="Jaguar Logo" style="width: 100px; height: 100px; margin-left: auto; margin-right: auto; display: block;">

# Jaguar - Command Line Based Search API For AI Agents

State of the art coding agents like [ClaudeCode](https://github.com/anthropics/claude-code) use tools like `ripgrep`, `jq` and `find` instead of vector embedding based search to provide context to the underlying models.

So far this approach has only been possible for text based files like code and when the agent is running locally on the user's machine. The goal of jaguar is to provide this type of search for all filetypes (pdf, docx etc..) while being possible to use from anywhere via it's REST API.

Jaguar is a Dockerized FastAPI service that allows humans and AI agents to upload files and search through them using powerful command-line tools like `ripgrep`, `jq`, and `find`. Files are automatically processed using the [Unstructured](https://docs.unstructured.io/open-source/introduction/quick-start) library to extract text and convert it to searchable markdown format.

## Features

- **File Upload**: Upload documents of various formats (PDF, DOCX, HTML, TXT, etc.)
- **Automatic Processing**: Files are processed using Unstructured to extract text and metadata
- **Markdown Conversion**: Documents are converted to searchable markdown format
- **Command Line Tools**: Integrated search using:
  - **ripgrep**: Fast text search with regex support
  - **jq**: JSON query processing for metadata
  - **find**: File system search
- **REST API**: Clean REST endpoints for all operations
- **Docker**: Fully containerized with all dependencies

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd jaguar
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. The API will be available at `http://localhost:8000`

### Using Docker

1. Build the image:
```bash
docker build -t jaguar-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 jaguar-api
```

### Local Development

1. Install uv (if not already installed):
```bash
curl -fsSL https://get.uv.dev | bash
```

2. Install dependencies:
```bash
uv sync
```

3. Run the application:
```bash
uv run uvicorn main:app --reload
```

## API Endpoints

### Base URL
- **GET** `/` - API information and available endpoints

### File Management
- **POST** `/upload/` - Upload a file for processing
- **GET** `/files/` - List all uploaded files
- **GET** `/files/{file_id}` - Get information about a specific file

### Search Endpoints
- **GET** `/search/ripgrep/` - Search through files using ripgrep
- **GET** `/search/find/` - Search for files using find command
- **GET** `/search/jq/` - Query JSON metadata using jq

## Usage Examples

### 1. Upload a File

```bash
curl -X POST "http://localhost:8000/upload/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

Response:
```json
{
  "file_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "size": 1048576,
  "processing_result": {
    "status": "success",
    "element_count": 42,
    "content_preview": "# Document Title\n\nThis is the content..."
  }
}
```

### 2. Search with Ripgrep

Search for text across all files:
```bash
curl "http://localhost:8000/search/ripgrep/?pattern=machine%20learning"
```

Search in a specific file with context:
```bash
curl "http://localhost:8000/search/ripgrep/?pattern=neural%20network&file_id=123e4567-e89b-12d3-a456-426614174000&context=2"
```

### 3. Search with Find

Find files by pattern:
```bash
curl "http://localhost:8000/search/find/?name_pattern=*.md&file_type=f"
```

### 4. Query Metadata with JQ

Extract specific information from document metadata:
```bash
curl "http://localhost:8000/search/jq/?file_id=123e4567-e89b-12d3-a456-426614174000&jq_filter=.[].metadata.page_number"
```

### 5. List Files

```bash
curl "http://localhost:8000/files/"
```

## Supported File Types

The Unstructured library supports many file formats including:

- **Text**: `.txt`, `.md`, `.rst`
- **Documents**: `.pdf`, `.docx`, `.doc`, `.odt`, `.rtf`
- **Presentations**: `.pptx`, `.ppt`
- **Spreadsheets**: `.xlsx`, `.xls`, `.csv`, `.tsv`
- **Web**: `.html`, `.xml`
- **Images**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`, `.heic`
- **E-books**: `.epub`
- **Email**: `.eml`, `.msg`

## API Documentation

Once the service is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **Alternative docs**: `http://localhost:8000/redoc`

## Architecture

The service consists of:

1. **FastAPI Server**: Handles HTTP requests and responses
2. **File Storage**: Stores uploaded files in `/app/uploads`
3. **Processing Pipeline**: Uses Unstructured to extract text and metadata
4. **Processed Storage**: Stores markdown and JSON in `/app/processed`
5. **Search Integration**: Executes command-line tools for searching

## Search Tools Details

### Ripgrep (rg)
- Fast text search with regex support
- JSON output for structured results
- Case-sensitive/insensitive options
- Context lines around matches

### Find
- File system search by name, type, size
- Supports glob patterns
- Directory traversal

### JQ
- JSON query and manipulation
- Filter and transform metadata
- Extract specific fields

## Development

### Project Structure
```
jaguar/
├── main.py              # FastAPI application
├── pyproject.toml       # Python dependencies
├── Dockerfile           # Container definition
├── docker-compose.yml   # Multi-container setup
├── README.md           # This file
└── uploads/            # Uploaded files (created at runtime)
└── processed/          # Processed files (created at runtime)
```

### Adding New Features

1. **New Search Tool**: Add a new endpoint in `main.py` following the existing pattern
2. **File Processing**: Modify `process_file_with_unstructured()` function
3. **Dependencies**: Update `pyproject.toml` and rebuild container

### Testing

```bash
# Install test dependencies
uv sync --dev

# Run tests
uv run pytest
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONUNBUFFERED` | `1` | Ensure stdout/stderr are unbuffered |

## Security Considerations

- The container runs as a non-root user (`appuser`)
- Files are stored in isolated directories
- No direct file system access from API
- Health checks ensure service availability

## Troubleshooting

### Common Issues

1. **Build fails**: Ensure Docker has enough memory allocated
2. **Upload fails**: Check file size limits and supported formats
3. **Search returns no results**: Verify file was processed successfully
4. **Permission errors**: Ensure proper file permissions in mounted volumes

### Logs

View container logs:
```bash
docker-compose logs -f
```

### Health Check

The service includes a health check endpoint. Check status:
```bash
curl http://localhost:8000/
```

