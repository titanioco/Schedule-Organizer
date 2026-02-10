"""
Schedule Optimizer Service
Generates optimal weekly study schedules based on selected classes.

Rules:
- No overlapping time slots allowed
- Cannot be in 2 groups of the same class simultaneously
- Credits: 6 minimum, 21 maximum (1 credit = 2 hours study time)
- Best schedule has no gaps between classes from 9am onward
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from itertools import product


@dataclass
class ScheduleSlot:
    """A time slot in a generated schedule"""
    class_code: str
    class_name: str
    group_id: str
    group_number: str
    day: str
    start_time: str
    end_time: str
    professor: str
    room: str
    credits: int
    
    def to_dict(self) -> Dict:
        return {
            'class_code': self.class_code,
            'class_name': self.class_name,
            'group_id': self.group_id,
            'group_number': self.group_number,
            'day': self.day,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'professor': self.professor,
            'room': self.room,
            'credits': self.credits
        }


@dataclass
class GeneratedSchedule:
    """A complete generated weekly schedule"""
    id: str
    slots: List[ScheduleSlot] = field(default_factory=list)
    selected_groups: List[Dict] = field(default_factory=list)
    total_credits: int = 0
    total_study_hours: float = 0  # Credits * 2
    total_class_hours: float = 0
    gap_minutes: int = 0  # Total gaps between classes (from 9am)
    days_used: int = 0
    earliest_start: str = ""
    latest_end: str = ""
    score: float = 0  # Higher is better
    rank: int = 0
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'rank': self.rank,
            'slots': [slot.to_dict() for slot in self.slots],
            'selected_groups': [
                {
                    'class_code': g.get('class_info', {}).get('code', ''),
                    'class_name': g.get('class_info', {}).get('name', ''),
                    'group_number': g.get('group_number', ''),
                    'professor': g.get('class_info', {}).get('professor', ''),
                }
                for g in self.selected_groups
            ],
            'total_credits': self.total_credits,
            'total_study_hours': self.total_study_hours,
            'total_class_hours': round(self.total_class_hours, 1),
            'gap_minutes': self.gap_minutes,
            'days_used': self.days_used,
            'earliest_start': self.earliest_start,
            'latest_end': self.latest_end,
            'score': round(self.score, 2),
            'weekly_view': self._get_weekly_view()
        }
    
    def _get_weekly_view(self) -> Dict[str, List[Dict]]:
        """Organize slots by day for weekly calendar view"""
        weekly = {}
        day_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for day in day_order:
            day_slots = [s for s in self.slots if s.day == day]
            day_slots.sort(key=lambda x: x.start_time)
            if day_slots:
                weekly[day] = [s.to_dict() for s in day_slots]
        
        return weekly


class ScheduleOptimizer:
    """
    Optimizes class schedules based on selected courses.
    
    Generates all valid combinations where:
    - No time slot overlaps
    - One group per class only
    - Total credits between 6 and 21
    
    Ranks schedules by compactness (fewer gaps from 9am onward is better).
    """
    
    # Credit limits
    MIN_CREDITS = 6
    MAX_CREDITS = 21
    HOURS_PER_CREDIT = 2
    
    # Reference time for gap calculation (9:00 AM)
    REFERENCE_START_MINUTES = 9 * 60  # 9:00 AM in minutes
    
    def __init__(self):
        self.available_courses: Dict[str, Dict] = {}
    
    def time_to_minutes(self, time_str: str) -> int:
        """Convert time string (HH:MM) to minutes from midnight"""
        try:
            parts = time_str.strip().split(':')
            hours = int(parts[0])
            minutes = int(parts[1]) if len(parts) > 1 else 0
            return hours * 60 + minutes
        except:
            return 0
    
    def minutes_to_time(self, minutes: int) -> str:
        """Convert minutes from midnight to time string"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def slots_overlap(self, slot1: Dict, slot2: Dict) -> bool:
        """Check if two time slots overlap on the same day"""
        day1 = slot1.get('day', '').strip()
        day2 = slot2.get('day', '').strip()
        
        if day1 != day2:
            return False
        
        start1 = self.time_to_minutes(slot1.get('start_time', '00:00'))
        end1 = self.time_to_minutes(slot1.get('end_time', '00:00'))
        start2 = self.time_to_minutes(slot2.get('start_time', '00:00'))
        end2 = self.time_to_minutes(slot2.get('end_time', '00:00'))
        
        # Check for overlap
        return not (end1 <= start2 or end2 <= start1)
    
    def groups_conflict(self, group1: Dict, group2: Dict) -> bool:
        """Check if two groups have any overlapping time slots"""
        slots1 = group1.get('time_slots', [])
        slots2 = group2.get('time_slots', [])
        
        for s1 in slots1:
            for s2 in slots2:
                if self.slots_overlap(s1, s2):
                    return True
        return False
    
    def combination_has_conflicts(self, groups: List[Dict]) -> bool:
        """Check if a combination of groups has any time conflicts"""
        for i, g1 in enumerate(groups):
            for g2 in groups[i+1:]:
                if self.groups_conflict(g1, g2):
                    return True
        return False
    
    def calculate_total_credits(self, groups: List[Dict]) -> int:
        """Calculate total credits from selected groups"""
        return sum(
            g.get('class_info', {}).get('credits', 0) 
            for g in groups
        )
    
    def calculate_class_hours(self, groups: List[Dict]) -> float:
        """Calculate total class hours per week"""
        total_minutes = 0
        for group in groups:
            for slot in group.get('time_slots', []):
                start = self.time_to_minutes(slot.get('start_time', '00:00'))
                end = self.time_to_minutes(slot.get('end_time', '00:00'))
                total_minutes += max(0, end - start)
        return total_minutes / 60
    
    def calculate_gap_score(self, groups: List[Dict]) -> int:
        """
        Calculate total gap minutes between classes from 9am onward.
        
        A gap is the time between the end of one class and start of the next
        on the same day, counting only from 9:00 AM.
        
        Returns total gap minutes (lower is better).
        """
        if not groups:
            return 0
        
        # Organize all slots by day
        slots_by_day: Dict[str, List[Dict]] = {}
        for group in groups:
            for slot in group.get('time_slots', []):
                day = slot.get('day', '').strip()
                if not day:
                    continue
                if day not in slots_by_day:
                    slots_by_day[day] = []
                slots_by_day[day].append({
                    'start': self.time_to_minutes(slot.get('start_time', '00:00')),
                    'end': self.time_to_minutes(slot.get('end_time', '00:00')),
                })
        
        total_gap = 0
        
        for day, slots in slots_by_day.items():
            if len(slots) < 2:
                continue
            
            # Sort by start time
            slots.sort(key=lambda x: x['start'])
            
            # Calculate gaps between consecutive classes
            for i in range(1, len(slots)):
                prev_end = slots[i-1]['end']
                curr_start = slots[i]['start']
                
                # Only count gaps from 9am onward
                if prev_end >= self.REFERENCE_START_MINUTES:
                    gap = curr_start - prev_end
                    if gap > 0:
                        total_gap += gap
        
        return total_gap
    
    def calculate_days_used(self, groups: List[Dict]) -> int:
        """Count number of unique days with classes"""
        days = set()
        for group in groups:
            for slot in group.get('time_slots', []):
                day = slot.get('day', '').strip()
                if day:
                    days.add(day)
        return len(days)
    
    def get_time_range(self, groups: List[Dict]) -> Tuple[str, str]:
        """Get earliest start and latest end times"""
        earliest = 24 * 60
        latest = 0
        
        for group in groups:
            for slot in group.get('time_slots', []):
                start = self.time_to_minutes(slot.get('start_time', '23:59'))
                end = self.time_to_minutes(slot.get('end_time', '00:00'))
                earliest = min(earliest, start)
                latest = max(latest, end)
        
        return self.minutes_to_time(earliest), self.minutes_to_time(latest)
    
    def score_schedule(self, groups: List[Dict]) -> float:
        """
        Calculate a score for a schedule. Higher is better.
        
        Scoring factors:
        1. Gap penalty: Less gaps from 9am onward = higher score
        2. Days concentration: Fewer days = slightly better
        3. Credits: More credits = slightly better (within limits)
        """
        gap_minutes = self.calculate_gap_score(groups)
        days_used = self.calculate_days_used(groups)
        credits = self.calculate_total_credits(groups)
        
        # Base score of 1000
        score = 1000.0
        
        # Gap penalty: -1 point per minute of gap
        score -= gap_minutes
        
        # Days bonus: +10 points for fewer days (max 5 days typical)
        score += (6 - days_used) * 10
        
        # Credits bonus: +2 points per credit
        score += credits * 2
        
        return max(0, score)
    
    def create_schedule_slots(self, groups: List[Dict]) -> List[ScheduleSlot]:
        """Create ScheduleSlot objects from group data"""
        slots = []
        for group in groups:
            class_info = group.get('class_info', {})
            for time_slot in group.get('time_slots', []):
                slot = ScheduleSlot(
                    class_code=class_info.get('code', ''),
                    class_name=class_info.get('name', ''),
                    group_id=group.get('id', ''),
                    group_number=group.get('group_number', ''),
                    day=time_slot.get('day', ''),
                    start_time=time_slot.get('start_time', ''),
                    end_time=time_slot.get('end_time', ''),
                    professor=class_info.get('professor', ''),
                    room=time_slot.get('room', ''),
                    credits=class_info.get('credits', 0)
                )
                slots.append(slot)
        return slots
    
    def get_available_courses(self, all_groups: List[Dict]) -> List[Dict]:
        """
        Get list of available courses with their groups for student selection.
        
        Returns list of courses with:
        - code, name, credits
        - list of available groups with time slots
        """
        courses: Dict[str, Dict] = {}
        
        for group in all_groups:
            class_info = group.get('class_info', {})
            code = class_info.get('code', 'UNKNOWN')
            
            # Only include groups that have time slots
            if not group.get('time_slots'):
                continue
            
            if code not in courses:
                courses[code] = {
                    'code': code,
                    'name': class_info.get('name', ''),
                    'credits': class_info.get('credits', 0),
                    'content': class_info.get('content', ''),
                    'groups': []
                }
            
            courses[code]['groups'].append({
                'id': group.get('id', ''),
                'group_number': group.get('group_number', ''),
                'professor': class_info.get('professor', ''),
                'time_slots': group.get('time_slots', []),
                'capacity': group.get('capacity', 0),
                'enrolled': group.get('enrolled', 0)
            })
        
        # Sort by name and return as list
        return sorted(courses.values(), key=lambda x: x['name'])
    
    def generate_schedules(
        self,
        selected_course_codes: List[str],
        all_groups: List[Dict],
        min_credits: int = None,
        max_credits: int = None
    ) -> List[GeneratedSchedule]:
        """
        Generate all valid schedule combinations for selected courses.
        
        Args:
            selected_course_codes: List of course codes the student wants to take
            all_groups: All available groups from parsed PDFs
            min_credits: Minimum credits (default: 6)
            max_credits: Maximum credits (default: 21)
            
        Returns:
            List of GeneratedSchedule objects, sorted from best to worst
        """
        min_credits = min_credits or self.MIN_CREDITS
        max_credits = max_credits or self.MAX_CREDITS
        
        # Organize groups by course code
        groups_by_course: Dict[str, List[Dict]] = {}
        
        for group in all_groups:
            class_info = group.get('class_info', {})
            code = class_info.get('code', '')
            
            # Only include selected courses
            if code not in selected_course_codes:
                continue
            
            # Only include groups with time slots
            if not group.get('time_slots'):
                continue
            
            if code not in groups_by_course:
                groups_by_course[code] = []
            groups_by_course[code].append(group)
        
        # Check which courses were found
        found_courses = set(groups_by_course.keys())
        missing_courses = set(selected_course_codes) - found_courses
        
        if not groups_by_course:
            return []
        
        # Generate all combinations: one group per course
        course_codes = list(groups_by_course.keys())
        group_options = [groups_by_course[code] for code in course_codes]
        
        valid_schedules = []
        schedule_id = 0
        
        # Generate cartesian product of all group options
        for combination in product(*group_options):
            groups = list(combination)
            
            # Check credit limits
            total_credits = self.calculate_total_credits(groups)
            if total_credits < min_credits or total_credits > max_credits:
                continue
            
            # Check for time conflicts
            if self.combination_has_conflicts(groups):
                continue
            
            # Valid schedule found!
            schedule_id += 1
            
            slots = self.create_schedule_slots(groups)
            gap_minutes = self.calculate_gap_score(groups)
            days_used = self.calculate_days_used(groups)
            earliest, latest = self.get_time_range(groups)
            score = self.score_schedule(groups)
            class_hours = self.calculate_class_hours(groups)
            
            schedule = GeneratedSchedule(
                id=f"schedule_{schedule_id:04d}",
                slots=slots,
                selected_groups=groups,
                total_credits=total_credits,
                total_study_hours=total_credits * self.HOURS_PER_CREDIT,
                total_class_hours=class_hours,
                gap_minutes=gap_minutes,
                days_used=days_used,
                earliest_start=earliest,
                latest_end=latest,
                score=score
            )
            
            valid_schedules.append(schedule)
        
        # Sort by score (highest/best first)
        valid_schedules.sort(key=lambda x: x.score, reverse=True)
        
        # Assign ranks
        for i, schedule in enumerate(valid_schedules):
            schedule.rank = i + 1
        
        return valid_schedules
    
    def get_schedule_summary(self, schedules: List[GeneratedSchedule]) -> Dict:
        """Get summary statistics for generated schedules"""
        if not schedules:
            return {
                'total_options': 0,
                'best_score': 0,
                'worst_score': 0,
                'min_gaps': 0,
                'max_gaps': 0
            }
        
        return {
            'total_options': len(schedules),
            'best_score': round(schedules[0].score, 2),
            'worst_score': round(schedules[-1].score, 2),
            'min_gaps': min(s.gap_minutes for s in schedules),
            'max_gaps': max(s.gap_minutes for s in schedules),
            'credit_range': {
                'min': min(s.total_credits for s in schedules),
                'max': max(s.total_credits for s in schedules)
            }
        }


# Legacy compatibility - for API backwards compatibility
class StudentAvailability:
    """Legacy compatibility class"""
    def __init__(self, days=None, start_time='07:00', end_time='21:00', 
                 min_classes=1, max_classes=10, preferred_gap_minutes=30):
        self.days = days or ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        self.start_time = start_time
        self.end_time = end_time
        self.min_classes = min_classes
        self.max_classes = max_classes
        self.preferred_gap_minutes = preferred_gap_minutes
    
    def to_dict(self):
        return {
            'days': self.days,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'min_classes': self.min_classes,
            'max_classes': self.max_classes,
            'preferred_gap_minutes': self.preferred_gap_minutes
        }
