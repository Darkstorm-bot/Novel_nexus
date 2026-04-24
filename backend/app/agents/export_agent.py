"""
Export Agent - Phase 9 of the pipeline.
Exports final story in various formats.
"""

from typing import Dict, Any, List, Optional
import json
import io

from app.agents.base_agent import BaseAgent, AgentResponse
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ExportAgent(BaseAgent):
    """
    Agent responsible for exporting final stories.
    
    Tasks:
    - Generate EPUB format
    - Generate PDF format
    - Generate Markdown/HTML
    - Create metadata
    - Prepare cover information
    """
    
    def __init__(self):
        super().__init__("ExportAgent")
    
    async def execute(
        self,
        story_id: str,
        context: Dict[str, Any],
    ) -> AgentResponse:
        try:
            logger.info("Starting export", story_id=story_id)
            
            consistency_data = context.get("consistency_data", {})
            polished_data = consistency_data.get("polished_data", {})
            
            if not polished_data:
                return self._create_response(
                    success=False,
                    errors=["No final draft data provided."],
                )
            
            export_formats = context.get("export_formats", ["epub", "markdown", "html"])
            
            system_prompt = self._build_system_prompt()
            prompt = self._build_export_prompt(polished_data, context)
            
            llm_response = await self._get_llm_response(prompt, system_prompt)
            export_metadata = self._parse_export_response(llm_response)
            
            export_result = await self._generate_exports(
                story_id=story_id,
                polished_data=polished_data,
                metadata=export_metadata,
                formats=export_formats,
            )
            
            return self._create_response(
                success=True,
                data=export_result,
                requires_approval=False,
                metadata={"phase": "export", "export_complete": True}
            )
            
        except Exception as e:
            logger.error("Export failed", story_id=story_id, error=str(e))
            return self._create_response(success=False, errors=[str(e)])
    
    def _build_system_prompt(self) -> str:
        return """You are an expert book formatter and metadata specialist.
Generate proper metadata and formatting information for export.

Format as JSON:
{
    "title": "string",
    "author": "string",
    "description": "string",
    "genre": "string",
    "tags": ["list"],
    "language": "en",
    "publisher": "Narrative Nexus",
    "isbn_placeholder": "string",
    "cover_description": "string"
}"""
    
    def _build_export_prompt(
        self,
        polished_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        concept_data = context.get("concept_data", {})
        title = concept_data.get("title", "Untitled Story")
        
        return f"Generate export metadata for: {title}. Include all necessary formatting info."
    
    def _parse_export_response(self, response: str) -> Dict[str, Any]:
        try:
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1
            if start_idx >= 0 and end_idx > start_idx:
                return json.loads(response[start_idx:end_idx])
        except json.JSONDecodeError:
            pass
        return {}
    
    async def _generate_exports(
        self,
        story_id: str,
        polished_data: Dict[str, Any],
        metadata: Dict[str, Any],
        formats: List[str],
    ) -> Dict[str, Any]:
        """Generate exports in requested formats."""
        export_result = {
            "formats_generated": [],
            "files": {},
            "metadata": metadata,
        }
        
        chapters = polished_data.get("chapters", [])
        
        # Generate Markdown (always available)
        if "markdown" in formats or "md" in formats:
            md_content = self._generate_markdown(chapters, metadata)
            export_result["files"]["markdown"] = md_content
            export_result["formats_generated"].append("markdown")
        
        # Generate HTML
        if "html" in formats:
            html_content = self._generate_html(chapters, metadata)
            export_result["files"]["html"] = html_content
            export_result["formats_generated"].append("html")
        
        # Generate EPUB structure (placeholder - would need ebooklib)
        if "epub" in formats:
            epub_structure = self._prepare_epub_structure(chapters, metadata)
            export_result["files"]["epub_structure"] = epub_structure
            export_result["formats_generated"].append("epub")
        
        # Generate PDF structure (placeholder - would need weasyprint)
        if "pdf" in formats:
            pdf_structure = self._prepare_pdf_structure(chapters, metadata)
            export_result["files"]["pdf_structure"] = pdf_structure
            export_result["formats_generated"].append("pdf")
        
        export_result["total_word_count"] = sum(
            ch.get("word_count", 0) for ch in chapters
        )
        
        return export_result
    
    def _generate_markdown(
        self,
        chapters: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate Markdown formatted content."""
        lines = []
        
        # Title page
        lines.append(f"# {metadata.get('title', 'Untitled')}")
        lines.append("")
        lines.append(f"**By {metadata.get('author', 'Unknown')}**")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for chapter in chapters:
            title = chapter.get("title", f"Chapter {chapter.get('chapter_number', '?')}")
            lines.append(f"- [{title}](#chapter-{chapter.get('chapter_number', '')})")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Chapters
        for chapter in chapters:
            ch_num = chapter.get("chapter_number", 0)
            ch_title = chapter.get("title", f"Chapter {ch_num}")
            content = chapter.get("content", "")
            
            lines.append(f"\n## Chapter {ch_num}: {ch_title}\n")
            lines.append(content)
            lines.append("\n---\n")
        
        return "\n".join(lines)
    
    def _generate_html(
        self,
        chapters: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate HTML formatted content."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html lang=\"en\">",
            "<head>",
            f"  <title>{metadata.get('title', 'Untitled')}</title>",
            "  <meta charset=\"UTF-8\">",
            "  <style>",
            "    body { font-family: Georgia, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "    h1 { text-align: center; }",
            "    .chapter { margin-bottom: 40px; page-break-before: always; }",
            "    .chapter-title { color: #333; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>{metadata.get('title', 'Untitled')}</h1>",
            f"  <p class=\"author\">By {metadata.get('author', 'Unknown')}</p>",
            "  <hr>",
        ]
        
        for chapter in chapters:
            ch_num = chapter.get("chapter_number", 0)
            ch_title = chapter.get("title", f"Chapter {ch_num}")
            content = chapter.get("content", "")
            
            html_parts.append(f'  <div class="chapter" id="chapter-{ch_num}">')
            html_parts.append(f'    <h2 class="chapter-title">Chapter {ch_num}: {ch_title}</h2>')
            html_parts.append(f"    {content}")
            html_parts.append("  </div>")
        
        html_parts.extend([
            "</body>",
            "</html>",
        ])
        
        return "\n".join(html_parts)
    
    def _prepare_epub_structure(
        self,
        chapters: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare EPUB structure (for ebooklib)."""
        return {
            "title": metadata.get("title", "Untitled"),
            "author": metadata.get("author", "Unknown"),
            "language": metadata.get("language", "en"),
            "chapters": [
                {
                    "title": ch.get("title", f"Chapter {ch.get('chapter_number', '?')}"),
                    "content": ch.get("content", ""),
                }
                for ch in chapters
            ],
            "metadata": metadata,
        }
    
    def _prepare_pdf_structure(
        self,
        chapters: List[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare PDF structure (for weasyprint)."""
        return {
            "title": metadata.get("title", "Untitled"),
            "author": metadata.get("author", "Unknown"),
            "chapters": chapters,
            "css_suggestions": [
                "@page { size: A5; margin: 2cm; }",
                "body { font-family: Garamond, serif; font-size: 11pt; }",
                "h1 { font-size: 24pt; text-align: center; }",
                "h2 { font-size: 16pt; page-break-before: always; }",
            ],
        }
    
    async def postprocess_result(self, result: AgentResponse) -> AgentResponse:
        if result.success and result.data:
            formats = result.data.get("formats_generated", [])
            word_count = result.data.get("total_word_count", 0)
            result.data["summary"] = f"Export complete: {len(formats)} formats ({', '.join(formats)}), {word_count} words"
        return result
