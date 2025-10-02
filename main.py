import os
import subprocess
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional, Union
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

# Unstructured imports
from unstructured.partition.auto import partition
from unstructured.staging.base import elements_to_json
from unstructured.chunking.title import chunk_by_title

app = FastAPI(
    title="File Search API",
    description="Upload files and search through them using command line tools",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Directory to store uploaded files and their processed versions
UPLOAD_DIR = Path("/app/uploads")
PROCESSED_DIR = Path("/app/processed")

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Store file metadata
file_registry = {}


@app.get("/")
def read_root():
    return {
        "message": "File Search API",
        "endpoints": {
            "upload": "POST /upload/",
            "search_ripgrep": "GET /search/ripgrep/",
            "search_find": "GET /search/find/",
            "search_jq": "GET /search/jq/",
            "list_files": "GET /files/",
            "get_file": "GET /files/{file_id}",
        },
    }


async def process_file_with_unstructured(file_path: Path, file_id: str) -> dict:
    """Process uploaded file using Unstructured to extract text and convert to markdown"""
    try:
        # Partition the document
        elements = partition(filename=str(file_path))

        # Convert elements to markdown-style text
        markdown_content = ""
        for element in elements:
            element_type = element.category
            text = element.text.strip()

            if not text:
                continue

            # Format based on element type
            if element_type == "Title":
                markdown_content += f"# {text}\n\n"
            elif element_type == "NarrativeText":
                markdown_content += f"{text}\n\n"
            elif element_type == "ListItem":
                markdown_content += f"- {text}\n"
            elif element_type == "Table":
                markdown_content += f"```\n{text}\n```\n\n"
            else:
                markdown_content += f"{text}\n\n"

        # Save processed markdown
        markdown_path = PROCESSED_DIR / f"{file_id}.md"
        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Save JSON metadata
        json_path = PROCESSED_DIR / f"{file_id}.json"
        elements_to_json(elements=elements, filename=str(json_path))

        return {
            "status": "success",
            "markdown_path": str(markdown_path),
            "json_path": str(json_path),
            "element_count": len(elements),
            "content_preview": markdown_content[:500] + "..."
            if len(markdown_content) > 500
            else markdown_content,
        }

    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file and process it with Unstructured"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Save uploaded file
    file_path = UPLOAD_DIR / f"{file_id}_{file.filename}"

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Process file with Unstructured
        processing_result = await process_file_with_unstructured(file_path, file_id)

        # Store file metadata
        file_registry[file_id] = {
            "original_filename": file.filename,
            "file_path": str(file_path),
            "file_id": file_id,
            "processing_result": processing_result,
            "size": len(contents),
            "content_type": file.content_type,
        }

        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(contents),
            "processing_result": processing_result,
        }

    except Exception as e:
        # Clean up on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/files/")
def list_files():
    """List all uploaded files"""
    return {"files": list(file_registry.values())}


@app.get("/files/{file_id}")
def get_file_info(file_id: str):
    """Get information about a specific file"""
    if file_id not in file_registry:
        raise HTTPException(status_code=404, detail="File not found")
    return file_registry[file_id]


@app.get("/search/ripgrep/")
async def search_with_ripgrep(
    pattern: str = Query(..., description="Search pattern for ripgrep"),
    file_id: Optional[str] = Query(
        None, description="Search in specific file (optional)"
    ),
    case_sensitive: bool = Query(False, description="Case sensitive search"),
    context: int = Query(0, description="Number of context lines to show"),
):
    """Search through processed files using ripgrep"""
    try:
        # Build ripgrep command
        cmd = ["rg", "--json"]

        if not case_sensitive:
            cmd.append("-i")

        if context > 0:
            cmd.extend(["-C", str(context)])

        cmd.append(pattern)

        # Determine search path
        if file_id:
            if file_id not in file_registry:
                raise HTTPException(status_code=404, detail="File not found")
            search_path = PROCESSED_DIR / f"{file_id}.md"
            if not search_path.exists():
                raise HTTPException(status_code=404, detail="Processed file not found")
        else:
            search_path = PROCESSED_DIR

        cmd.append(str(search_path))

        # Execute ripgrep
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode not in [0, 1]:  # 1 means no matches found
            raise HTTPException(
                status_code=500, detail=f"Ripgrep error: {stderr.decode()}"
            )

        # Parse JSON output
        results = []
        for line in stdout.decode().strip().split("\n"):
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

        return {
            "pattern": pattern,
            "file_id": file_id,
            "results": results,
            "total_matches": len([r for r in results if r.get("type") == "match"]),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.get("/search/find/")
async def search_with_find(
    name_pattern: Optional[str] = Query(None, description="File name pattern"),
    file_type: Optional[str] = Query(
        None, description="File type (f for files, d for directories)"
    ),
    size: Optional[str] = Query(
        None, description="File size filter (e.g., +1M, -100k)"
    ),
):
    """Search for files using find command"""
    try:
        cmd = ["find", str(PROCESSED_DIR)]

        if name_pattern:
            cmd.extend(["-name", name_pattern])

        if file_type:
            cmd.extend(["-type", file_type])

        if size:
            cmd.extend(["-size", size])

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise HTTPException(
                status_code=500, detail=f"Find error: {stderr.decode()}"
            )

        files = [
            line.strip() for line in stdout.decode().strip().split("\n") if line.strip()
        ]

        return {
            "search_parameters": {
                "name_pattern": name_pattern,
                "file_type": file_type,
                "size": size,
            },
            "results": files,
            "count": len(files),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Find error: {str(e)}")


@app.get("/search/jq/")
async def search_with_jq(
    file_id: str = Query(..., description="File ID to search in"),
    jq_filter: str = Query(..., description="JQ filter expression"),
):
    """Search through JSON metadata using jq"""
    try:
        if file_id not in file_registry:
            raise HTTPException(status_code=404, detail="File not found")

        json_path = PROCESSED_DIR / f"{file_id}.json"
        if not json_path.exists():
            raise HTTPException(status_code=404, detail="JSON metadata not found")

        cmd = ["jq", jq_filter, str(json_path)]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=f"JQ error: {stderr.decode()}")

        try:
            result = json.loads(stdout.decode())
        except json.JSONDecodeError:
            result = stdout.decode().strip()

        return {"file_id": file_id, "jq_filter": jq_filter, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JQ search error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
