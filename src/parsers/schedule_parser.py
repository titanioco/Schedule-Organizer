"""
Schedule Parser
Parses PDF and HTML files containing class schedules and groups
Supports SIA (Universidad Nacional) PDF course information
"""

from bs4 import BeautifulSoup
import pdfplumber
import os
import re
from typing import List, Dict, Optional
from src.models.schedule import Schedule, Group, Class, TimeSlot

class ScheduleParser:
    """Parser for PDF and HTML schedule files"""
    
    def __init__(self, schedules_dir: str = "data/schedules"):
        """
        Initialize parser
        
        Args:
            schedules_dir: Directory containing schedule PDF/HTML files
        """
        self.schedules_dir = schedules_dir
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.schedules_dir):
            os.makedirs(self.schedules_dir, exist_ok=True)
    
    def get_all_schedules(self) -> List[Dict]:
        """
        Get all available schedules
        
        Returns:
            List of schedule dictionaries
        """
        schedules = []
        
        if not os.path.exists(self.schedules_dir):
            return schedules
        
        for filename in os.listdir(self.schedules_dir):
            if filename.endswith('.pdf') or filename.endswith('.html'):
                try:
                    schedule = self.parse_schedule_file(
                        os.path.join(self.schedules_dir, filename)
                    )
                    if schedule and schedule.groups:
                        schedules.append(schedule.to_dict())
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
        
        return schedules
    
    def get_all_groups(self) -> List[Dict]:
        """
        Get all groups from all schedule files.
        Returns groups as dictionaries ready for the optimizer.
        
        Returns:
            List of group dictionaries with class_info and time_slots
        """
        all_groups = []
        
        if not os.path.exists(self.schedules_dir):
            return all_groups
        
        for filename in os.listdir(self.schedules_dir):
            if filename.endswith('.pdf') or filename.endswith('.html'):
                try:
                    schedule = self.parse_schedule_file(
                        os.path.join(self.schedules_dir, filename)
                    )
                    if schedule and schedule.groups:
                        for group in schedule.groups:
                            group_dict = {
                                'id': group.id,
                                'group_number': group.group_number,
                                'class_info': {
                                    'id': group.class_info.id,
                                    'name': group.class_info.name,
                                    'code': group.class_info.code,
                                    'professor': group.class_info.professor,
                                    'credits': group.class_info.credits,
                                    'content': group.class_info.content,
                                    'description': getattr(group.class_info, 'description', '')
                                },
                                'time_slots': [
                                    {
                                        'day': ts.day,
                                        'start_time': ts.start_time,
                                        'end_time': ts.end_time,
                                        'room': ts.room
                                    }
                                    for ts in group.time_slots
                                ],
                                'capacity': group.capacity,
                                'enrolled': group.enrolled
                            }
                            all_groups.append(group_dict)
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
        
        return all_groups
    
    def get_schedule_by_id(self, schedule_id: str) -> Optional[Dict]:
        """
        Get specific schedule by ID
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Schedule dictionary or None
        """
        schedules = self.get_all_schedules()
        for schedule in schedules:
            if schedule['id'] == schedule_id:
                return schedule
        return None
    
    def parse_schedule_file(self, filepath: str) -> Optional[Schedule]:
        """
        Parse a schedule file (PDF or HTML)
        
        Args:
            filepath: Path to PDF or HTML file
            
        Returns:
            Schedule object or None
        """
        try:
            schedule_id = os.path.splitext(os.path.basename(filepath))[0]
            
            # Check file extension
            if filepath.lower().endswith('.pdf'):
                return self._parse_pdf_schedule(filepath, schedule_id)
            elif filepath.lower().endswith('.html'):
                return self._parse_html_schedule(filepath, schedule_id)
            else:
                print(f"Unsupported file format: {filepath}")
                return None
                
        except Exception as e:
            print(f"Error parsing schedule file {filepath}: {e}")
            return None
    
    def _parse_pdf_schedule(self, filepath: str, schedule_id: str) -> Optional[Schedule]:
        """
        Parse a PDF file containing course information from SIA.
        Extracts course details, syllabus content, and group schedules.
        
        Args:
            filepath: Path to PDF file
            schedule_id: ID for the schedule
            
        Returns:
            Schedule object or None
        """
        try:
            with pdfplumber.open(filepath) as pdf:
                # Extract all text from all pages
                full_text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        full_text += page_text + "\n"
                
                if not full_text.strip():
                    print(f"No text extracted from PDF: {filepath}")
                    return None
                
                # Parse the extracted text
                return self._parse_sia_pdf_content(full_text, schedule_id)
                
        except Exception as e:
            print(f"Error parsing PDF {filepath}: {e}")
            return None
    
    def _parse_sia_pdf_content(self, text: str, schedule_id: str) -> Optional[Schedule]:
        """
        Parse SIA course information from extracted PDF text.
        
        Expected format from SIA course detail PDF:
        - Course name and code
        - Credits, typology
        - Course content (syllabus/chapters)
        - Groups with professors and schedules
        """
        groups = []
        lines = text.split('\n')
        
        # Extract course info
        course_name = ""
        course_code = ""
        credits = 4
        typology = ""
        faculty = ""
        
        # Find course title - usually in format "CourseName (CODE)"
        for i, line in enumerate(lines):
            # Match pattern like "Cálculo diferencial (1000004-B)"
            match = re.search(r'(.+?)\s*\((\d{7}-[A-Z]|\d{7})\)', line)
            if match:
                course_name = match.group(1).strip()
                course_code = match.group(2).strip()
                break
        
        if not course_name:
            # Try to find course name from first meaningful line
            for line in lines[:10]:
                if len(line.strip()) > 5 and not any(skip in line.lower() for skip in ['universidad', 'sia', 'portal', 'servicios']):
                    course_name = line.strip()
                    break
        
        if not course_name:
            course_name = schedule_id
        
        if not course_code:
            # Try to find code pattern
            code_match = re.search(r'(\d{7}-[A-Z]|\d{7})', text)
            if code_match:
                course_code = code_match.group(1)
            else:
                course_code = schedule_id
        
        # Extract credits
        credits_match = re.search(r'Cr[ée]ditos[:\s]*(\d+)', text, re.IGNORECASE)
        if credits_match:
            credits = int(credits_match.group(1))
        
        # Extract typology
        typo_match = re.search(r'Tipolog[íi]a[:\s]*([^\n]+)', text, re.IGNORECASE)
        if typo_match:
            typology = typo_match.group(1).strip()
        
        # Extract faculty
        faculty_match = re.search(r'Facultad[:\s]*([^\n]+)', text, re.IGNORECASE)
        if faculty_match:
            faculty = faculty_match.group(1).strip()
        
        # Extract course content (syllabus)
        course_content = self._extract_pdf_course_content(text)
        
        # Extract groups with schedules
        groups = self._extract_pdf_groups(text, course_name, course_code, credits, typology, course_content)
        
        # If no groups found, create a single group with the course info
        if not groups:
            class_info = Class(
                id=f"class_{course_code}_01",
                name=course_name,
                name_en=course_name,
                code=course_code,
                professor="Por asignar",
                content=course_content,
                content_en="",
                credits=credits,
                description=f"{typology} - {faculty}" if faculty else typology,
                description_en=""
            )
            
            groups.append(Group(
                id=f"group_{course_code}_01",
                group_number="01",
                class_info=class_info,
                time_slots=[],
                capacity=30,
                enrolled=0
            ))
        
        return Schedule(
            id=schedule_id,
            semester="2026-1",
            year=2026,
            period=f"{course_name} ({course_code})",
            groups=groups
        )
    
    def _extract_pdf_course_content(self, text: str) -> str:
        """
        Extract course syllabus/content from PDF text.
        This content is used for AI assistant review.
        
        Looks for chapter structures like:
        - Capítulo 001, Capítulo 002
        - Unidad 1, Unidad 2
        - Tema 1, Tema 2
        - Numbered sections
        """
        content_parts = []
        lines = text.split('\n')
        
        current_chapter = None
        current_content = []
        
        # Patterns for chapter/section headers
        chapter_patterns = [
            r'^Cap[íi]tulo\s*\d+',
            r'^Unidad\s*\d+',
            r'^Tema\s*\d+',
            r'^Contenido de la asignatura',
            r'^\d+\.\s+[A-ZÁÉÍÓÚ]',  # Numbered sections
        ]
        
        # Patterns to skip (headers, footers, etc.)
        skip_patterns = [
            r'^Universidad Nacional',
            r'^Portal de Servicios',
            r'^Página\s*\d+',
            r'^Volver$',
            r'^Imprimir$',
            r'^Información de la asignatura',
            r'^Horarios/Aula',
            r'^Profesor:',
            r'^Facultad:',
            r'^Cupos disponibles',
            r'^Jornada:',
            r'^Duración:',
            r'^Grupo\s+\d+',
            r'^\(\w+-\d+\)',  # Group codes like (TUMA-01)
        ]
        
        in_content_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we should skip this line
            should_skip = any(re.match(pattern, line, re.IGNORECASE) for pattern in skip_patterns)
            if should_skip:
                continue
            
            # Check for chapter header
            is_chapter = any(re.match(pattern, line, re.IGNORECASE) for pattern in chapter_patterns)
            
            if is_chapter:
                # Save previous chapter content
                if current_chapter and current_content:
                    content_parts.append(f"**{current_chapter}**\n" + '\n'.join(current_content))
                
                current_chapter = line
                current_content = []
                in_content_section = True
            elif in_content_section and current_chapter:
                # Check if we've hit a new section (group info, etc.)
                if re.match(r'^(CLASE|LABORATORIO|TALLER|PRÁCTICA)\s+', line, re.IGNORECASE):
                    in_content_section = False
                    if current_content:
                        content_parts.append(f"**{current_chapter}**\n" + '\n'.join(current_content))
                    current_chapter = None
                    current_content = []
                else:
                    current_content.append(line)
        
        # Don't forget the last chapter
        if current_chapter and current_content:
            content_parts.append(f"**{current_chapter}**\n" + '\n'.join(current_content))
        
        # If no structured content found, extract general course description
        if not content_parts:
            # Look for description section
            desc_match = re.search(r'Descripci[óo]n[:\s]*([^\n]+(?:\n(?![A-Z]{2,})[^\n]+)*)', text, re.IGNORECASE)
            if desc_match:
                content_parts.append(desc_match.group(1).strip())
            else:
                # Extract any meaningful text paragraphs
                for line in lines:
                    line = line.strip()
                    if len(line) > 100:  # Likely a content paragraph
                        content_parts.append(line)
                        if len(content_parts) >= 5:
                            break
        
        return '\n\n'.join(content_parts)
    
    def _extract_pdf_groups(self, text: str, course_name: str, course_code: str, 
                           credits: int, typology: str, course_content: str) -> List[Group]:
        """
        Extract groups with schedules from PDF text.
        
        Looks for patterns like:
        - Grupo 1, Grupo 2, etc.
        - (TUMA-01), (AMAZ-02) group codes
        - Professor names
        - Time slots: LUNES de 07:00 a 09:00
        """
        groups = []
        lines = text.split('\n')
        
        # Pattern for group headers
        group_patterns = [
            r'\(([A-Z]{4}-\d{2})\)',  # (TUMA-01) format
            r'Grupo\s+(\d+)',  # Grupo 1 format
        ]
        
        # Pattern for time slots
        time_pattern = r'(LUNES|MARTES|MI[ÉE]RCOLES|JUEVES|VIERNES|S[ÁA]BADO|DOMINGO)\s+de\s+(\d{1,2}:\d{2})\s+a\s+(\d{1,2}:\d{2})'
        
        current_group = None
        current_professor = "Por asignar"
        current_times = []
        current_capacity = 30
        group_idx = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for group code
            for pattern in group_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous group
                    if current_group:
                        groups.append(self._create_group(
                            course_name, course_code, credits, typology, 
                            course_content, current_group, current_professor,
                            current_times, current_capacity, group_idx
                        ))
                        group_idx += 1
                    
                    current_group = match.group(1)
                    current_professor = "Por asignar"
                    current_times = []
                    current_capacity = 30
                    break
            
            # Check for professor
            prof_match = re.search(r'Profesor[:\s]*([^,\n]+)', line, re.IGNORECASE)
            if prof_match and current_group:
                current_professor = prof_match.group(1).strip().rstrip('.')
            
            # Check for time slots
            time_matches = re.findall(time_pattern, line, re.IGNORECASE)
            for day, start, end in time_matches:
                current_times.append({
                    'day': day.capitalize(),
                    'start': start,
                    'end': end
                })
            
            # Check for capacity
            cupos_match = re.search(r'Cupos\s+disponibles[:\s]*(\d+)', line, re.IGNORECASE)
            if cupos_match and current_group:
                current_capacity = int(cupos_match.group(1))
        
        # Save last group
        if current_group:
            groups.append(self._create_group(
                course_name, course_code, credits, typology, 
                course_content, current_group, current_professor,
                current_times, current_capacity, group_idx
            ))
        
        return groups
    
    def _create_group(self, course_name: str, course_code: str, credits: int,
                     typology: str, course_content: str, group_code: str,
                     professor: str, times: List[Dict], capacity: int, idx: int) -> Group:
        """Create a Group object from extracted data."""
        
        # Parse group number from group code
        group_number = "01"
        num_match = re.search(r'(\d+)', group_code)
        if num_match:
            group_number = num_match.group(1).zfill(2)
        
        # Create time slots
        time_slots = []
        for t in times:
            day_map = {
                'Lunes': 'Lunes',
                'Martes': 'Martes',
                'Miércoles': 'Miércoles',
                'Miercoles': 'Miércoles',
                'Jueves': 'Jueves',
                'Viernes': 'Viernes',
                'Sábado': 'Sábado',
                'Sabado': 'Sábado',
                'Domingo': 'Domingo'
            }
            time_slots.append(TimeSlot(
                day=day_map.get(t['day'], t['day']),
                start_time=t['start'],
                end_time=t['end'],
                room=""
            ))
        
        class_info = Class(
            id=f"class_{course_code}_{group_code}",
            name=course_name,
            name_en=course_name,
            code=course_code,
            professor=professor,
            content=course_content,
            content_en="",
            credits=credits,
            description=typology,
            description_en=""
        )
        
        return Group(
            id=f"group_{course_code}_{group_code}_{idx}",
            group_number=group_number,
            class_info=class_info,
            time_slots=time_slots,
            capacity=capacity,
            enrolled=max(0, capacity - 30)  # Estimate
        )
    
    def _parse_html_schedule(self, filepath: str, schedule_id: str) -> Optional[Schedule]:
        """
        Parse an HTML schedule file (legacy support)
        
        Args:
            filepath: Path to HTML file
            schedule_id: ID for the schedule
            
        Returns:
            Schedule object or None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Detect if this is a SIA (Universidad Nacional) HTML save
            is_sia_format = self._is_sia_format(soup)
            
            if is_sia_format:
                # Check if it's a course detail page (with syllabus and groups)
                if self._is_sia_course_detail_format(soup):
                    return self._parse_sia_course_detail(soup, schedule_id)
                return self._parse_sia_schedule(soup, schedule_id)
            
            # Look for schedule metadata in meta tags or specific elements
            semester = self._extract_text(soup, 'semester', default='2024-1')
            year = self._extract_year(soup, default=2024)
            period = self._extract_text(soup, 'period', default='Semester 2024-1')
            
            # Parse groups using legacy format
            groups = self._parse_groups_legacy(soup)
            
            return Schedule(
                id=schedule_id,
                semester=semester,
                year=year,
                period=period,
                groups=groups
            )
        
        except Exception as e:
            print(f"Error parsing HTML file {filepath}: {e}")
            return None
    
    def _is_sia_format(self, soup: BeautifulSoup) -> bool:
        """Detect if HTML is from SIA (Universidad Nacional) system"""
        # Check for SIA-specific markers
        sia_markers = [
            soup.find('a', href=lambda x: x and 'sia.unal.edu.co' in x if x else False),
            soup.find(text=lambda x: x and 'Catálogo' in x if x else False),
            soup.find(text=lambda x: x and 'Buscador de cursos' in x if x else False),
            soup.find('th', text=lambda x: x and 'Código' in x if x else False),
            soup.find('th', text=lambda x: x and 'Asignatura' in x if x else False),
            soup.find(class_=lambda x: x and 'af_table' in x if x else False),
            soup.find(id=lambda x: x and 'pt1:r1:0:t4' in x if x else False),
            # Course detail page markers
            soup.find(text=lambda x: x and 'Información de la asignatura' in x if x else False),
            soup.find(text=lambda x: x and 'Contenido de la asignatura' in x if x else False),
        ]
        return any(sia_markers)
    
    def _is_sia_course_detail_format(self, soup: BeautifulSoup) -> bool:
        """Detect if HTML is from SIA course detail page (with syllabus and groups)"""
        # Check for course detail page specific markers
        markers = [
            soup.find(text=lambda x: x and 'Información de la asignatura' in x if x else False),
            soup.find(text=lambda x: x and 'Contenido de la asignatura' in x if x else False),
            soup.find('span', class_=lambda x: x and 'ficha-docente-titulo' in x if x else False),
        ]
        return any(markers)
    
    def _parse_sia_course_detail(self, soup: BeautifulSoup, schedule_id: str) -> Schedule:
        """Parse SIA course detail page with syllabus content and group schedules"""
        groups = []
        
        # Extract course title - format: "Cálculo diferencial (1000004-B)"
        course_name = ""
        course_code = ""
        
        # Find the main course title (h2 with course name and code)
        title_h2 = soup.find('h2', text=lambda x: x and '(' in x and ')' in x if x else False)
        if title_h2:
            title_text = title_h2.get_text(strip=True)
            # Parse "Cálculo diferencial (1000004-B)" format
            match = re.match(r'(.+?)\s*\(([^)]+)\)', title_text)
            if match:
                course_name = match.group(1).strip()
                course_code = match.group(2).strip()
        
        # Fallback: try to find in ocu-titulo span
        if not course_name:
            titulo_span = soup.find('span', class_=lambda x: x and 'ocu-titulo' in x if x else False)
            if titulo_span:
                h2 = titulo_span.find('h2')
                if h2:
                    title_text = h2.get_text(strip=True)
                    match = re.match(r'(.+?)\s*\(([^)]+)\)', title_text)
                    if match:
                        course_name = match.group(1).strip()
                        course_code = match.group(2).strip()
        
        if not course_name:
            course_name = schedule_id
            course_code = schedule_id
        
        # Extract credits
        credits = 4  # Default
        credits_span = soup.find('span', class_=lambda x: x and 'detass-creditos' in x if x else False)
        if credits_span:
            credits_text = credits_span.get_text(strip=True)
            match = re.search(r'Créditos[:\s]*(\d+)', credits_text)
            if match:
                credits = int(match.group(1))
        
        # Extract typology
        typology = ""
        typology_span = soup.find('span', class_=lambda x: x and 'detass-tipologia' in x if x else False)
        if typology_span:
            typology_text = typology_span.get_text(strip=True)
            typology = typology_text.replace('Tipología:', '').strip()
        
        # Extract faculty
        faculty = ""
        faculty_span = soup.find('span', class_=lambda x: x and 'detass-centro' in x if x else False)
        if faculty_span:
            faculty = faculty_span.get_text(strip=True)
        
        # Extract course content/syllabus (CRITICAL - for AI review)
        course_content = self._extract_sia_course_content(soup)
        
        # Extract groups with time slots
        groups = self._extract_sia_groups(soup, course_name, course_code, credits, typology, course_content)
        
        # Extract metadata
        year = 2026
        semester = "2026-1"
        period = f"{course_name} ({course_code})"
        
        return Schedule(
            id=schedule_id,
            semester=semester,
            year=year,
            period=period,
            groups=groups
        )
    
    def _extract_sia_course_content(self, soup: BeautifulSoup) -> str:
        """Extract course syllabus/content from SIA detail page.
        This content will be used for AI assistant review.
        """
        content_parts = []
        
        # Find all chapter elements (class: ficha-docente-titulo)
        chapter_spans = soup.find_all('span', class_='ficha-docente-titulo')
        
        for chapter_span in chapter_spans:
            chapter_title = chapter_span.get_text(strip=True)
            
            # Find the corresponding content div (sibling or parent's next element)
            parent = chapter_span.find_parent('span', class_='row')
            if parent:
                content_div = parent.find('div', class_='ficha-docente-descripcion')
                if content_div:
                    # Get the inner content div
                    inner_content = content_div.find('div', class_='af_richTextEditor_content')
                    if inner_content:
                        content_text = inner_content.get_text(strip=True)
                        if content_text:  # Only add if there's actual content
                            content_parts.append(f"**{chapter_title}**\n{content_text}")
        
        # Join all content parts
        full_content = "\n\n".join(content_parts)
        
        return full_content
    
    def _extract_sia_groups(self, soup: BeautifulSoup, course_name: str, course_code: str, 
                           credits: int, typology: str, course_content: str) -> List[Group]:
        """Extract groups with schedules from SIA course detail page"""
        groups = []
        
        # Find all group headers - format: "(TUMA-01) Peama - Tumaco - Grupo 1"
        # These are in h2 elements inside af_showDetailHeader
        group_headers = soup.find_all('div', class_=lambda x: x and 'af_showDetailHeader' in x if x else False)
        
        for idx, header_div in enumerate(group_headers):
            # Skip the "Contenido de la asignatura" header
            title_div = header_div.find('div', class_='af_showDetailHeader_title-text-cell')
            if not title_div:
                continue
            
            group_title = title_div.get('title', '')
            if not group_title:
                h2 = title_div.find('h2')
                if h2:
                    group_title = h2.get_text(strip=True)
            
            # Skip non-group headers
            if 'Contenido de la asignatura' in group_title:
                continue
            if 'Capítulo' in group_title or 'Bibliografía' in group_title:
                continue
            
            # Parse group info
            group_match = re.search(r'\(([^)]+)\)', group_title)
            group_code = group_match.group(1) if group_match else f"G{idx+1:02d}"
            
            group_number = "01"
            grupo_match = re.search(r'Grupo\s*(\d+)', group_title, re.IGNORECASE)
            if grupo_match:
                group_number = grupo_match.group(1).zfill(2)
            
            # Extract professor
            professor = "Por asignar"
            content_div = header_div.find('div', class_='af_showDetailHeader_content0')
            if content_div:
                prof_span = content_div.find('span', class_='strong')
                if prof_span:
                    professor = prof_span.get_text(strip=True).rstrip('.')
            
            # Extract time slots
            time_slots = self._extract_sia_time_slots(content_div)
            
            # Extract available spots
            capacity = 30
            enrolled = 0
            if content_div:
                cupos_text = content_div.get_text()
                cupos_match = re.search(r'Cupos disponibles[:\s]*(\d+)', cupos_text)
                if cupos_match:
                    available = int(cupos_match.group(1))
                    capacity = max(30, available)
                    enrolled = capacity - available
            
            # Extract sede/faculty for this group
            sede = ""
            if content_div:
                facultad_span = content_div.find('span', text=lambda x: x and 'Facultad:' in x if x else False)
                if facultad_span:
                    sede_span = facultad_span.find_next('span')
                    if sede_span:
                        sede = sede_span.get_text(strip=True)
            
            # Create class info with course content for AI review
            class_info = Class(
                id=f"class_{course_code}_{group_code}",
                name=course_name,
                name_en=course_name,  # Will be translated if needed
                code=course_code,
                professor=professor,
                content=course_content,  # Full syllabus for AI review
                content_en="",
                credits=credits,
                description=f"{typology} - {sede}" if sede else typology,
                description_en=""
            )
            
            group = Group(
                id=f"group_{course_code}_{group_code}_{idx}",
                group_number=group_number,
                class_info=class_info,
                time_slots=time_slots,
                capacity=capacity,
                enrolled=enrolled
            )
            
            groups.append(group)
        
        return groups
    
    def _extract_sia_time_slots(self, content_div) -> List[TimeSlot]:
        """Extract time slots from SIA group content.
        Format: "LUNES de 07:00 a 09:00."
        """
        time_slots = []
        
        if not content_div:
            return time_slots
        
        # Find all time slot spans - they contain text like "LUNES de 07:00 a 09:00."
        time_spans = content_div.find_all('span', class_='lista-elemento')
        
        for span in time_spans:
            text = span.get_text(strip=True)
            
            # Parse format: "LUNES de 07:00 a 09:00."
            match = re.match(r'(LUNES|MARTES|MIÉRCOLES|JUEVES|VIERNES|SÁBADO|DOMINGO)\s+de\s+(\d{1,2}:\d{2})\s+a\s+(\d{1,2}:\d{2})', text, re.IGNORECASE)
            
            if match:
                day = match.group(1).capitalize()
                start_time = match.group(2)
                end_time = match.group(3)
                
                # Map to standard day names
                day_map = {
                    'Lunes': 'Lunes',
                    'Martes': 'Martes',
                    'Miércoles': 'Miércoles',
                    'Jueves': 'Jueves',
                    'Viernes': 'Viernes',
                    'Sábado': 'Sábado',
                    'Domingo': 'Domingo'
                }
                day_name = day_map.get(day, day)
                
                # Try to extract room info from nearby spans
                room = ""
                room_spans = span.find_all('span', class_='margin-l')
                if room_spans:
                    room_parts = [r.get_text(strip=True).rstrip('.') for r in room_spans[:2]]
                    room = ' '.join(room_parts)
                
                time_slots.append(TimeSlot(
                    day=day_name,
                    start_time=start_time,
                    end_time=end_time,
                    room=room
                ))
        
        return time_slots
    
    def _parse_sia_schedule(self, soup: BeautifulSoup, schedule_id: str) -> Schedule:
        """Parse schedule from SIA (Universidad Nacional) HTML format"""
        groups = []
        
        # Extract course title/category from page if available
        title_elem = soup.find('h1')
        category = title_elem.get_text(strip=True) if title_elem else schedule_id
        
        # Try to find the main data table
        # SIA uses tables with class containing 'af_table' or specific ID patterns
        data_table = None
        
        # Method 1: Find table by specific SIA class patterns
        data_table = soup.find('table', class_=lambda x: x and 'af_table_data-table' in x if x else False)
        
        # Method 2: Look for table with Código/Asignatura headers
        if not data_table:
            for table in soup.find_all('table'):
                headers = table.find_all('th')
                header_texts = [h.get_text(strip=True).lower() for h in headers]
                if any('código' in h or 'codigo' in h for h in header_texts):
                    data_table = table
                    break
        
        # Method 3: Find rows with course data pattern (7-digit code links)
        if data_table:
            rows = data_table.find_all('tr', role='row')
            if not rows:
                rows = data_table.find_all('tr')
        else:
            # Search for all rows that contain course links
            rows = soup.find_all('tr', role='row')
        
        for idx, row in enumerate(rows):
            group = self._parse_sia_row(row, idx)
            if group:
                groups.append(group)
        
        # Extract metadata
        year = 2026  # Current year based on context
        semester = "2026-1"
        period = f"Libre Elección - {category}" if category else "Libre Elección"
        
        return Schedule(
            id=schedule_id,
            semester=semester,
            year=year,
            period=period,
            groups=groups
        )
    
    def _parse_sia_row(self, row, index: int) -> Optional[Group]:
        """Parse a course row from SIA format"""
        try:
            cells = row.find_all('td')
            if len(cells) < 3:
                return None
            
            # SIA format columns: Código, Asignatura, Créditos, Tipología, Descripción
            # Extract course code - usually in a link
            code_cell = cells[0] if cells else None
            code_link = code_cell.find('a') if code_cell else None
            class_code = code_link.get_text(strip=True) if code_link else cells[0].get_text(strip=True)
            
            # Validate it looks like a course code (typically 7-digit or alphanumeric)
            if not class_code or not re.match(r'^[\dA-Z-]+$', class_code, re.IGNORECASE):
                return None
            
            # Extract course name
            name_cell = cells[1] if len(cells) > 1 else None
            class_name = ""
            is_not_scheduled = False
            
            if name_cell:
                # Get the main name (first span with title or text)
                name_span = name_cell.find('span', title=True)
                if name_span:
                    class_name = name_span.get('title') or name_span.get_text(strip=True)
                else:
                    # Get text but exclude "ASIGNATURA SIN PROGRAMAR"
                    full_text = name_cell.get_text(strip=True)
                    if "ASIGNATURA SIN PROGRAMAR" in full_text:
                        is_not_scheduled = True
                        class_name = full_text.replace("ASIGNATURA SIN PROGRAMAR", "").strip()
                    else:
                        class_name = full_text
            
            if not class_name:
                return None
            
            # Extract credits
            credits = 2  # Default
            if len(cells) > 2:
                credits_text = cells[2].get_text(strip=True)
                try:
                    credits = int(credits_text)
                except ValueError:
                    credits = 2
            
            # Extract typology (type of course)
            typology = ""
            if len(cells) > 3:
                typology = cells[3].get_text(strip=True)
            
            # Extract description
            description = ""
            if len(cells) > 4:
                desc_span = cells[4].find('span', title=True)
                if desc_span:
                    description = desc_span.get('title') or desc_span.get_text(strip=True)
                else:
                    description = cells[4].get_text(strip=True)
            
            # Create class info
            class_info = Class(
                id=f"class_{class_code}_{index}",
                name=class_name,
                name_en=class_name,  # Will be translated if needed
                code=class_code,
                professor="Por asignar" if is_not_scheduled else "Ver horario",
                content=description[:500] if description else "",
                content_en="",
                credits=credits,
                description=description,
                description_en=""
            )
            
            # For SIA format, we create a group with typology info
            status = "Sin programar" if is_not_scheduled else "Disponible"
            
            return Group(
                id=f"group_{class_code}_01_{index}",
                group_number="01",
                class_info=class_info,
                time_slots=[],  # SIA catalog doesn't show specific times in this view
                capacity=30,
                enrolled=0
            )
        
        except Exception as e:
            print(f"Error parsing SIA row: {e}")
            return None
    
    def _parse_groups_legacy(self, soup: BeautifulSoup) -> List[Group]:
        """Parse class groups from legacy HTML format"""
        groups = []
        
        # Look for tables or divs with class information
        group_elements = soup.find_all(['tr', 'div'], class_=lambda x: x and 'group' in x.lower() if x else False)
        
        if not group_elements:
            # Fallback: look for table rows
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                for idx, row in enumerate(rows):
                    group = self._parse_group_row_legacy(row, idx)
                    if group:
                        groups.append(group)
        else:
            for idx, element in enumerate(group_elements):
                group = self._parse_group_element(element, idx)
                if group:
                    groups.append(group)
        
        return groups
    
    def _parse_group_row_legacy(self, row, index: int) -> Optional[Group]:
        """Parse a group from a table row (legacy format)"""
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 4:
                return None
            
            # Basic parsing - adjust based on actual HTML structure
            class_code = cells[0].get_text(strip=True)
            class_name = cells[1].get_text(strip=True) if len(cells) > 1 else "Unknown"
            group_number = cells[2].get_text(strip=True) if len(cells) > 2 else "01"
            professor = cells[3].get_text(strip=True) if len(cells) > 3 else "TBA"
            
            # Create class info
            class_info = Class(
                id=f"class_{class_code}_{index}",
                name=class_name,
                name_en=class_name,  # Will be translated
                code=class_code,
                professor=professor,
                content="",
                content_en="",
                credits=3
            )
            
            # Parse time slots
            time_slots = []
            if len(cells) > 4:
                time_text = cells[4].get_text(strip=True)
                time_slots = self._parse_time_slots(time_text)
            
            # Extract capacity and enrolled if available
            capacity = 30
            enrolled = 0
            if len(cells) > 5:
                try:
                    capacity = int(cells[5].get_text(strip=True))
                except ValueError:
                    pass
            if len(cells) > 6:
                try:
                    enrolled = int(cells[6].get_text(strip=True))
                except ValueError:
                    pass
            
            # Extract content if available
            content = ""
            if len(cells) > 7:
                content = cells[7].get_text(strip=True)
                class_info.content = content
            
            return Group(
                id=f"group_{class_code}_{group_number}_{index}",
                group_number=group_number,
                class_info=class_info,
                time_slots=time_slots,
                capacity=capacity,
                enrolled=enrolled
            )
        
        except Exception as e:
            print(f"Error parsing group row: {e}")
            return None
    
    def _parse_group_element(self, element, index: int) -> Optional[Group]:
        """Parse a group from a div or other element"""
        try:
            # Extract class information from element attributes or nested elements
            class_code = element.get('data-code', f'CODE{index:03d}')
            class_name = element.get('data-name', 'Unknown Class')
            group_number = element.get('data-group', '01')
            
            class_info = Class(
                id=f"class_{class_code}_{index}",
                name=class_name,
                name_en=class_name,
                code=class_code,
                professor="TBA",
                content="",
                content_en="",
                credits=3
            )
            
            return Group(
                id=f"group_{class_code}_{group_number}_{index}",
                group_number=group_number,
                class_info=class_info,
                time_slots=[],
                capacity=30,
                enrolled=0
            )
        
        except Exception as e:
            print(f"Error parsing group element: {e}")
            return None
    
    def _parse_time_slots(self, time_text: str) -> List[TimeSlot]:
        """Parse time slot information from text"""
        time_slots = []
        
        # Handle multiple schedules separated by comma
        schedule_parts = time_text.split(',')
        
        for part in schedule_parts:
            part = part.strip()
            if not part:
                continue
                
            # Example formats: "Lun 8:00-10:00", "Ma-Ju 14:00-16:00", "Lun 08:00-10:00"
            # Match patterns like "Day HH:MM-HH:MM"
            match = re.match(r'([A-Za-záéíóú]+)\s+(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', part)
            if match:
                day_abbr = match.group(1)
                start = match.group(2)
                end = match.group(3)
                
                # Map Spanish day abbreviations to full names
                day_map = {
                    'Lun': 'Lunes',
                    'Mar': 'Martes',
                    'Mie': 'Miércoles',
                    'Mié': 'Miércoles',
                    'Jue': 'Jueves',
                    'Vie': 'Viernes',
                    'Sab': 'Sábado',
                    'Sáb': 'Sábado',
                    'Dom': 'Domingo'
                }
                
                day_name = day_map.get(day_abbr, day_abbr)
                time_slots.append(TimeSlot(
                    day=day_name,
                    start_time=start,
                    end_time=end,
                    room=""
                ))
        
        return time_slots
    
    def _extract_text(self, soup: BeautifulSoup, class_name: str, default: str = "") -> str:
        """Extract text from element by class name"""
        element = soup.find(class_=class_name)
        if element:
            return element.get_text(strip=True)
        
        # Try meta tag
        meta = soup.find('meta', attrs={'name': class_name})
        if meta and meta.get('content'):
            return meta['content']
        
        return default
    
    def _extract_year(self, soup: BeautifulSoup, default: int = 2024) -> int:
        """Extract year from HTML"""
        year_text = self._extract_text(soup, 'year')
        if year_text:
            try:
                return int(year_text)
            except ValueError:
                pass
        return default
