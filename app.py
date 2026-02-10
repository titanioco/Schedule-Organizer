"""
Schedule Organizer - Main Application
Organizes study schedules according to class availability by period
Supports Spanish and English languages
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

from src.parsers.schedule_parser import ScheduleParser
from src.services.ai_analyzer import AIAnalyzer
from src.services.translation_service import TranslationService
from src.services.schedule_optimizer import ScheduleOptimizer

# Load environment variables
load_dotenv()

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Configure secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize services
schedule_parser = ScheduleParser()
ai_analyzer = AIAnalyzer(api_key=os.getenv('OPENAI_API_KEY'))
translation_service = TranslationService()
schedule_optimizer = ScheduleOptimizer()

@app.route('/')
def index():
    """Main page - Schedule viewer"""
    return render_template('index.html')

@app.route('/api/schedules')
def get_schedules():
    """Get all available schedules"""
    try:
        schedules = schedule_parser.get_all_schedules()
        return jsonify({
            'success': True,
            'schedules': schedules
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/schedule/<schedule_id>')
def get_schedule(schedule_id):
    """Get specific schedule by ID"""
    try:
        schedule = schedule_parser.get_schedule_by_id(schedule_id)
        if schedule:
            return jsonify({
                'success': True,
                'schedule': schedule
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Schedule not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-content', methods=['POST'])
def analyze_content():
    """Analyze class content using AI"""
    try:
        data = request.json
        content = data.get('content', '')
        language = data.get('language', 'es')  # Default to Spanish
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'No content provided'
            }), 400
        
        analysis = ai_analyzer.analyze_class_content(content, language)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translate text between Spanish and English"""
    try:
        data = request.json
        text = data.get('text', '')
        target_language = data.get('target_language', 'en')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        translated = translation_service.translate(text, target_language)
        
        return jsonify({
            'success': True,
            'translated': translated
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0.0'
    })


@app.route('/api/available-courses')
def get_available_courses():
    """
    Get all available courses with their groups for student selection.
    
    The student should use this endpoint to see all courses, then select
    which ones they want to take before generating schedules.
    
    Returns:
    - List of courses with code, name, credits, and available groups
    - Each group includes time slots, professor, and capacity info
    """
    try:
        # Parse all schedule files to extract courses and groups
        all_groups = schedule_parser.get_all_groups()
        
        # Use optimizer to organize courses for selection
        courses = schedule_optimizer.get_available_courses(all_groups)
        
        return jsonify({
            'success': True,
            'courses': courses,
            'total_courses': len(courses),
            'total_groups': sum(len(c.get('groups', [])) for c in courses),
            'credit_limits': {
                'min': schedule_optimizer.MIN_CREDITS,
                'max': schedule_optimizer.MAX_CREDITS,
                'hours_per_credit': schedule_optimizer.HOURS_PER_CREDIT
            },
            'instructions': 'Select courses by code, then call /api/generate-schedules with selected course codes.'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/generate-schedules', methods=['POST'])
def generate_schedules():
    """
    Generate all valid schedule combinations for selected courses.
    
    Request body:
    {
        "selected_courses": ["2016377", "2016699", ...],  // Course codes
        "min_credits": 6,    // Optional, default 6
        "max_credits": 21    // Optional, default 21
    }
    
    Returns all valid schedules ranked from best to worst where:
    - No overlapping time slots
    - One group per course
    - Total credits within limits
    - Best = fewer gaps from 9am onward
    """
    try:
        data = request.json or {}
        
        selected_courses = data.get('selected_courses', [])
        
        if not selected_courses:
            return jsonify({
                'success': False,
                'error': 'No courses selected. Use /api/available-courses to see available courses.'
            }), 400
        
        # Get credit limits from request or use defaults
        min_credits = data.get('min_credits', schedule_optimizer.MIN_CREDITS)
        max_credits = data.get('max_credits', schedule_optimizer.MAX_CREDITS)
        
        # Validate credit limits
        if min_credits < 0 or max_credits < min_credits:
            return jsonify({
                'success': False,
                'error': f'Invalid credit limits. Must be 0 <= min <= max. Got min={min_credits}, max={max_credits}'
            }), 400
        
        # Get all available groups from parsed schedules
        all_groups = schedule_parser.get_all_groups()
        
        if not all_groups:
            return jsonify({
                'success': False,
                'error': 'No schedule data available. Ensure PDF files are in data/schedules folder.'
            }), 404
        
        # Generate ALL valid schedules
        schedules = schedule_optimizer.generate_schedules(
            selected_course_codes=selected_courses,
            all_groups=all_groups,
            min_credits=min_credits,
            max_credits=max_credits
        )
        
        # Get summary statistics
        summary = schedule_optimizer.get_schedule_summary(schedules)
        
        if not schedules:
            # Find which courses were found vs missing
            found_codes = set()
            for g in all_groups:
                code = g.get('class_info', {}).get('code', '')
                if code:
                    found_codes.add(code)
            
            missing = [c for c in selected_courses if c not in found_codes]
            found = [c for c in selected_courses if c in found_codes]
            
            return jsonify({
                'success': True,
                'schedules': [],
                'summary': summary,
                'message': 'No valid schedules found. Check for time conflicts or credit limits.',
                'debug': {
                    'courses_requested': selected_courses,
                    'courses_found': found,
                    'courses_missing': missing,
                    'credit_limits': {'min': min_credits, 'max': max_credits}
                }
            })
        
        return jsonify({
            'success': True,
            'schedules': [s.to_dict() for s in schedules],
            'summary': summary,
            'credit_limits': {'min': min_credits, 'max': max_credits}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/optimize-schedule', methods=['POST'])
def optimize_schedule():
    """
    [LEGACY] Generate schedules with availability constraints.
    For new workflow, use /api/generate-schedules instead.
    
    Request body:
    {
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
        "start_time": "09:00",
        "end_time": "20:00",
        "min_classes": 3,
        "max_classes": 6,
        "preferred_gap_minutes": 30,
        "required_courses": ["CS101", "MATH101"]  // optional
    }
    """
    try:
        data = request.json or {}
        
        # Get all available groups from parsed schedules
        all_groups = schedule_parser.get_all_groups()
        
        if not all_groups:
            return jsonify({
                'success': False,
                'error': 'No schedule data available.'
            }), 404
        
        # Filter groups with actual time slots
        groups_with_times = [g for g in all_groups if g.get('time_slots')]
        
        if not groups_with_times:
            return jsonify({
                'success': False,
                'error': 'No groups with scheduled times found.'
            }), 404
        
        # Redirect to new workflow
        required_courses = data.get('required_courses', None)
        
        if required_courses:
            # Use new generation with selected courses
            schedules = schedule_optimizer.generate_schedules(
                selected_course_codes=required_courses,
                all_groups=all_groups,
                min_credits=data.get('min_credits', 0),
                max_credits=data.get('max_credits', 30)
            )
            
            return jsonify({
                'success': True,
                'schedules': [s.to_dict() for s in schedules[:10]],
                'total_options': len(schedules),
                'groups_analyzed': len(groups_with_times),
                'note': 'Use /api/generate-schedules for full new workflow.'
            })
        else:
            return jsonify({
                'success': True,
                'schedules': [],
                'message': 'Use /api/available-courses to select courses, then /api/generate-schedules to generate schedules.',
                'groups_available': len(groups_with_times)
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    print(f"🚀 Starting Schedule Organizer on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
