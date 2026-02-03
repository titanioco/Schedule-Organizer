"""
AI-powered content analyzer for class content
Uses OpenAI API to analyze and provide insights about class content
"""

from typing import Dict, Optional
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AIAnalyzer:
    """AI analyzer for class content"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI analyzer
        
        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        self.client = None
        
        if OPENAI_AVAILABLE and api_key:
            try:
                self.client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Warning: Could not initialize OpenAI client: {e}")
    
    def analyze_class_content(self, content: str, language: str = 'es') -> Dict:
        """
        Analyze class content and provide insights
        
        Args:
            content: Class content to analyze
            language: Target language ('es' for Spanish, 'en' for English)
            
        Returns:
            Dictionary with analysis results
        """
        if not self.client:
            return self._get_mock_analysis(content, language)
        
        try:
            # Prepare prompt based on language
            if language == 'es':
                prompt = self._get_spanish_prompt(content)
            else:
                prompt = self._get_english_prompt(content)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente educativo experto en analizar contenido de cursos y proporcionar información útil y relevante." if language == 'es' else "You are an expert educational assistant analyzing course content and providing useful and relevant information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the response
            return self._parse_ai_response(analysis_text, language)
        
        except Exception as e:
            print(f"Error during AI analysis: {e}")
            return self._get_mock_analysis(content, language)
    
    def _get_spanish_prompt(self, content: str) -> str:
        """Get analysis prompt in Spanish"""
        return f"""Analiza el siguiente contenido de un curso y proporciona:

1. Un resumen breve del curso (2-3 oraciones)
2. Los temas clave cubiertos (lista de 5-7 temas)
3. El nivel de dificultad (Básico, Intermedio, Avanzado)
4. Prerrequisitos sugeridos (si aplica)
5. Recomendaciones de estudio

Contenido del curso:
{content}

Por favor responde en formato JSON con las siguientes claves:
- summary: resumen del curso
- key_topics: lista de temas clave
- difficulty_level: nivel de dificultad
- prerequisites: lista de prerrequisitos
- recommendations: recomendaciones de estudio
"""
    
    def _get_english_prompt(self, content: str) -> str:
        """Get analysis prompt in English"""
        return f"""Analyze the following course content and provide:

1. A brief course summary (2-3 sentences)
2. Key topics covered (list of 5-7 topics)
3. Difficulty level (Basic, Intermediate, Advanced)
4. Suggested prerequisites (if applicable)
5. Study recommendations

Course content:
{content}

Please respond in JSON format with the following keys:
- summary: course summary
- key_topics: list of key topics
- difficulty_level: difficulty level
- prerequisites: list of prerequisites
- recommendations: study recommendations
"""
    
    def _parse_ai_response(self, response_text: str, language: str) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                return {
                    'summary': data.get('summary', ''),
                    'key_topics': data.get('key_topics', []),
                    'difficulty_level': data.get('difficulty_level', 'Intermedio' if language == 'es' else 'Intermediate'),
                    'prerequisites': data.get('prerequisites', []),
                    'recommendations': data.get('recommendations', '')
                }
        except Exception as e:
            print(f"Error parsing AI response: {e}")
        
        # Fallback to text parsing
        return {
            'summary': response_text[:200] if len(response_text) > 200 else response_text,
            'key_topics': [],
            'difficulty_level': 'Intermedio' if language == 'es' else 'Intermediate',
            'prerequisites': [],
            'recommendations': ''
        }
    
    def _get_mock_analysis(self, content: str, language: str) -> Dict:
        """
        Get mock analysis when AI is not available
        
        Args:
            content: Class content
            language: Target language
            
        Returns:
            Mock analysis dictionary
        """
        if language == 'es':
            return {
                'summary': 'Este curso cubre conceptos fundamentales y avanzados del tema. Se enfoca en aplicaciones prácticas y teóricas.',
                'key_topics': [
                    'Fundamentos teóricos',
                    'Aplicaciones prácticas',
                    'Metodologías de trabajo',
                    'Herramientas y tecnologías',
                    'Casos de estudio'
                ],
                'difficulty_level': 'Intermedio',
                'prerequisites': [
                    'Conocimientos básicos del área',
                    'Fundamentos de matemáticas'
                ],
                'recommendations': 'Se recomienda estudiar regularmente, participar en sesiones prácticas y completar todos los ejercicios asignados.'
            }
        else:
            return {
                'summary': 'This course covers fundamental and advanced concepts of the subject. It focuses on practical and theoretical applications.',
                'key_topics': [
                    'Theoretical fundamentals',
                    'Practical applications',
                    'Work methodologies',
                    'Tools and technologies',
                    'Case studies'
                ],
                'difficulty_level': 'Intermediate',
                'prerequisites': [
                    'Basic knowledge of the area',
                    'Mathematics fundamentals'
                ],
                'recommendations': 'It is recommended to study regularly, participate in practical sessions, and complete all assigned exercises.'
            }
