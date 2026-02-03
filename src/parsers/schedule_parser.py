"""
HTML Schedule Parser
Parses HTML files containing class schedules and groups
"""

from bs4 import BeautifulSoup
import os
from typing import List, Dict, Optional
from src.models.schedule import Schedule, Group, Class, TimeSlot

class ScheduleParser:
    """Parser for HTML schedule files"""
    
    def __init__(self, schedules_dir: str = "data/schedules"):
        """
        Initialize parser
        
        Args:
            schedules_dir: Directory containing schedule HTML files
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
            if filename.endswith('.html'):
                try:
                    schedule = self.parse_schedule_file(
                        os.path.join(self.schedules_dir, filename)
                    )
                    if schedule:
                        schedules.append(schedule.to_dict())
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
        
        return schedules
    
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
        Parse a single HTML schedule file
        
        Args:
            filepath: Path to HTML file
            
        Returns:
            Schedule object or None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract schedule metadata
            schedule_id = os.path.splitext(os.path.basename(filepath))[0]
            
            # Look for schedule metadata in meta tags or specific elements
            semester = self._extract_text(soup, 'semester', default='2024-1')
            year = self._extract_year(soup, default=2024)
            period = self._extract_text(soup, 'period', default='Semester 2024-1')
            
            # Parse groups
            groups = self._parse_groups(soup)
            
            return Schedule(
                id=schedule_id,
                semester=semester,
                year=year,
                period=period,
                groups=groups
            )
        
        except Exception as e:
            print(f"Error parsing schedule file {filepath}: {e}")
            return None
    
    def _parse_groups(self, soup: BeautifulSoup) -> List[Group]:
        """Parse class groups from HTML"""
        groups = []
        
        # Look for tables or divs with class information
        group_elements = soup.find_all(['tr', 'div'], class_=lambda x: x and 'group' in x.lower() if x else False)
        
        if not group_elements:
            # Fallback: look for table rows
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                for idx, row in enumerate(rows):
                    group = self._parse_group_row(row, idx)
                    if group:
                        groups.append(group)
        else:
            for idx, element in enumerate(group_elements):
                group = self._parse_group_element(element, idx)
                if group:
                    groups.append(group)
        
        return groups
    
    def _parse_group_row(self, row, index: int) -> Optional[Group]:
        """Parse a group from a table row"""
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
            
            return Group(
                id=f"group_{class_code}_{group_number}_{index}",
                group_number=group_number,
                class_info=class_info,
                time_slots=time_slots,
                capacity=30,
                enrolled=0
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
        
        # Example formats: "Lun 8:00-10:00", "Ma-Ju 14:00-16:00"
        # Simple parsing - can be extended based on actual format
        parts = time_text.split()
        if len(parts) >= 2:
            days = parts[0]
            times = parts[1] if len(parts) > 1 else "08:00-10:00"
            
            if '-' in times:
                start, end = times.split('-')
                
                # Map Spanish day abbreviations to full names
                day_map = {
                    'Lun': 'Lunes',
                    'Mar': 'Martes',
                    'Mie': 'Miércoles',
                    'Jue': 'Jueves',
                    'Vie': 'Viernes',
                    'Sab': 'Sábado'
                }
                
                for day_abbr, day_name in day_map.items():
                    if day_abbr in days:
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
