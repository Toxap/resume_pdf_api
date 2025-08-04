"""
API для генерации резюме в формате PDF
--------------------------------------

Этот модуль реализует API‑сервис на FastAPI, который принимает 
структурированные данные о кандидатах (имя, опыт работы, навыки) и 
возвращает PDF‑файл с отформатированным резюме. HTML‑шаблон 
обрабатывается через Jinja2, а затем конвертируется в PDF с помощью 
pdfkit/wkhtmltopdf.

Важно: для корректной работы pdfkit требуется установленный бинарник 
`wkhtmltopdf`. В контейнере агента его нет, поэтому PDF не будет 
генерироваться в тестовой среде. На вашей машине установите пакет 
`wkhtmltopdf` из официальных репозиториев (например, `apt install 
wkhtmltopdf` на Debian/Ubuntu).
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit
import io
import os


app = FastAPI(
    title="Resume PDF Generator",
    description="Сервис для генерации резюме в формате PDF из JSON данных",
    version="0.1.0",
)

# Настраиваем Jinja2 для загрузки шаблонов из каталога templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


class ResumeRequest(BaseModel):
    """Модель входных данных для генерации резюме."""

    name: str = Field(..., description="Имя и фамилия кандидата")
    experience: List[str] = Field(
        ..., description="Список описаний опыта работы (каждый элемент — отдельный пункт)"
    )
    skills: List[str] = Field(..., description="Список навыков")
    template: Optional[str] = Field(
        "resume_default",
        description="Название HTML‑шаблона (без расширения) в каталоге templates",
    )

    # Дополнительные поля для более сложных шаблонов (например, resume_modern.html)
    position: Optional[str] = Field(
        None, description="Желаемая должность или специализация кандидата"
    )
    education: Optional[List[str]] = Field(
        None, description="Список пунктов образования/курсов"
    )


def render_to_pdf(template_name: str, context: dict) -> bytes:
    """Рендерит HTML шаблон с данными и превращает его в PDF.

    Parameters
    ----------
    template_name : str
        Имя файла шаблона (без каталога).
    context : dict
        Данные для передачи в шаблон Jinja2.

    Returns
    -------
    bytes
        PDF‑документ в виде набора байт.
    """
    # Загружаем шаблон
    try:
        template = env.get_template(f"{template_name}.html")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Шаблон '{template_name}' не найден: {exc}")
    # Рендерим HTML
    html_content = template.render(**context)
    # Генерируем PDF. Если wkhtmltopdf не установлен, будет исключение.
    try:
        pdf_bytes = pdfkit.from_string(html_content, False)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации PDF: {exc}")
    return pdf_bytes


@app.post(
    "/generate-pdf",
    response_class=StreamingResponse,
    summary="Сгенерировать PDF‑резюме",
)
async def generate_pdf(data: ResumeRequest) -> StreamingResponse:
    """Создаёт резюме на основе переданных данных и возвращает PDF файл.

    Получает JSON с данными кандидата, подставляет их в HTML‑шаблон и
    конвертирует результат в PDF. Возвращает потоковый ответ с MIME‑типом
    `application/pdf` и заголовком для скачивания файла.
    """
    context = {
        "name": data.name,
        "experience": data.experience,
        "skills": data.skills,
        # Дополнительные поля могут быть None
        "position": data.position,
        "education": data.education,
    }
    pdf_bytes = render_to_pdf(data.template, context)
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=resume.pdf"},
    )