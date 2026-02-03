"""
Translation service for dual language support (Spanish/English)
"""

from typing import Dict

class TranslationService:
    """Service for translating between Spanish and English"""
    
    def __init__(self):
        """Initialize translation service"""
        self.translations = self._load_translations()
    
    def translate(self, text: str, target_language: str) -> str:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code ('es' or 'en')
            
        Returns:
            Translated text
        """
        # Check if text is a translation key
        if text in self.translations:
            return self.translations[text].get(target_language, text)
        
        # For dynamic content, would use translation API
        # For now, return original text
        return text
    
    def get_ui_translations(self, language: str = 'es') -> Dict:
        """
        Get all UI translations for a language
        
        Args:
            language: Language code ('es' or 'en')
            
        Returns:
            Dictionary of UI translations
        """
        ui_texts = {}
        
        for key, translations in self.translations.items():
            if language in translations:
                ui_texts[key] = translations[language]
        
        return ui_texts
    
    def _load_translations(self) -> Dict:
        """Load translation dictionary"""
        return {
            # App titles
            'app_title': {
                'es': 'Organizador de Horarios',
                'en': 'Schedule Organizer'
            },
            'app_subtitle': {
                'es': 'Asistente para organizar tu horario de estudio',
                'en': 'Assistant to organize your study schedule'
            },
            
            # Navigation
            'nav_home': {
                'es': 'Inicio',
                'en': 'Home'
            },
            'nav_schedules': {
                'es': 'Horarios',
                'en': 'Schedules'
            },
            'nav_classes': {
                'es': 'Clases',
                'en': 'Classes'
            },
            'nav_analysis': {
                'es': 'Análisis',
                'en': 'Analysis'
            },
            
            # Schedule page
            'schedule_title': {
                'es': 'Horarios Disponibles',
                'en': 'Available Schedules'
            },
            'schedule_semester': {
                'es': 'Semestre',
                'en': 'Semester'
            },
            'schedule_period': {
                'es': 'Período',
                'en': 'Period'
            },
            'schedule_groups': {
                'es': 'Grupos',
                'en': 'Groups'
            },
            
            # Class information
            'class_code': {
                'es': 'Código',
                'en': 'Code'
            },
            'class_name': {
                'es': 'Nombre',
                'en': 'Name'
            },
            'class_professor': {
                'es': 'Profesor',
                'en': 'Professor'
            },
            'class_credits': {
                'es': 'Créditos',
                'en': 'Credits'
            },
            'class_schedule': {
                'es': 'Horario',
                'en': 'Schedule'
            },
            'class_group': {
                'es': 'Grupo',
                'en': 'Group'
            },
            'class_capacity': {
                'es': 'Capacidad',
                'en': 'Capacity'
            },
            'class_enrolled': {
                'es': 'Inscritos',
                'en': 'Enrolled'
            },
            'class_available': {
                'es': 'Disponibles',
                'en': 'Available'
            },
            
            # Days of week
            'day_monday': {
                'es': 'Lunes',
                'en': 'Monday'
            },
            'day_tuesday': {
                'es': 'Martes',
                'en': 'Tuesday'
            },
            'day_wednesday': {
                'es': 'Miércoles',
                'en': 'Wednesday'
            },
            'day_thursday': {
                'es': 'Jueves',
                'en': 'Thursday'
            },
            'day_friday': {
                'es': 'Viernes',
                'en': 'Friday'
            },
            'day_saturday': {
                'es': 'Sábado',
                'en': 'Saturday'
            },
            
            # AI Analysis
            'analysis_title': {
                'es': 'Análisis de Contenido',
                'en': 'Content Analysis'
            },
            'analysis_summary': {
                'es': 'Resumen',
                'en': 'Summary'
            },
            'analysis_topics': {
                'es': 'Temas Clave',
                'en': 'Key Topics'
            },
            'analysis_difficulty': {
                'es': 'Nivel de Dificultad',
                'en': 'Difficulty Level'
            },
            'analysis_prerequisites': {
                'es': 'Prerrequisitos',
                'en': 'Prerequisites'
            },
            'analysis_recommendations': {
                'es': 'Recomendaciones',
                'en': 'Recommendations'
            },
            
            # Difficulty levels
            'difficulty_basic': {
                'es': 'Básico',
                'en': 'Basic'
            },
            'difficulty_intermediate': {
                'es': 'Intermedio',
                'en': 'Intermediate'
            },
            'difficulty_advanced': {
                'es': 'Avanzado',
                'en': 'Advanced'
            },
            
            # Buttons
            'btn_analyze': {
                'es': 'Analizar',
                'en': 'Analyze'
            },
            'btn_translate': {
                'es': 'Traducir',
                'en': 'Translate'
            },
            'btn_view_details': {
                'es': 'Ver Detalles',
                'en': 'View Details'
            },
            'btn_close': {
                'es': 'Cerrar',
                'en': 'Close'
            },
            
            # Messages
            'msg_loading': {
                'es': 'Cargando...',
                'en': 'Loading...'
            },
            'msg_no_schedules': {
                'es': 'No hay horarios disponibles',
                'en': 'No schedules available'
            },
            'msg_error': {
                'es': 'Error al cargar datos',
                'en': 'Error loading data'
            },
            'msg_analyzing': {
                'es': 'Analizando contenido...',
                'en': 'Analyzing content...'
            }
        }
