/**
 * Schedule Organizer - Main Application TypeScript
 * Handles UI interactions, API calls, and dual language support
 */

interface Schedule {
    id: string;
    semester: string;
    year: number;
    period: string;
    groups: Group[];
    total_groups: number;
}

interface Group {
    id: string;
    group_number: string;
    class_info: ClassInfo;
    time_slots: TimeSlot[];
    capacity: number;
    enrolled: number;
    available: number;
}

interface ClassInfo {
    id: string;
    name: string;
    name_en: string;
    code: string;
    professor: string;
    content: string;
    content_en: string;
    credits: number;
    description: string;
    description_en: string;
}

interface TimeSlot {
    day: string;
    start_time: string;
    end_time: string;
    room: string;
}

interface AnalysisResult {
    summary: string;
    key_topics: string[];
    difficulty_level: string;
    prerequisites: string[];
    recommendations: string;
}

class ScheduleOrganizerApp {
    private currentLanguage: string = 'es';
    private schedules: Schedule[] = [];

    constructor() {
        this.init();
    }

    private init(): void {
        this.setupEventListeners();
        this.loadSchedules();
    }

    private setupEventListeners(): void {
        // Language toggle
        const langToggle = document.getElementById('lang-toggle');
        if (langToggle) {
            langToggle.addEventListener('click', () => this.toggleLanguage());
        }

        // Navigation
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = (e.target as HTMLElement).closest('.nav-link')?.getAttribute('data-section');
                if (section) {
                    this.showSection(section);
                }
            });
        });

        // Analysis button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.analyzeContent());
        }

        // Modal close
        const closeBtn = document.querySelector('.close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeModal());
        }

        // Close modal on outside click
        const modal = document.getElementById('class-modal');
        if (modal) {
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    private toggleLanguage(): void {
        this.currentLanguage = this.currentLanguage === 'es' ? 'en' : 'es';
        this.updateLanguageDisplay();
    }

    private updateLanguageDisplay(): void {
        const esElements = document.querySelectorAll('.lang-es');
        const enElements = document.querySelectorAll('.lang-en');

        if (this.currentLanguage === 'es') {
            esElements.forEach(el => (el as HTMLElement).style.display = '');
            enElements.forEach(el => (el as HTMLElement).style.display = 'none');
        } else {
            esElements.forEach(el => (el as HTMLElement).style.display = 'none');
            enElements.forEach(el => (el as HTMLElement).style.display = '');
        }
    }

    private showSection(sectionId: string): void {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Update nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-section') === sectionId) {
                link.classList.add('active');
            }
        });
    }

    private async loadSchedules(): Promise<void> {
        try {
            const response = await fetch('/api/schedules');
            const data = await response.json();

            if (data.success) {
                this.schedules = data.schedules;
                this.displaySchedules();
            } else {
                this.showError('Error loading schedules: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading schedules: ' + error);
        }
    }

    private displaySchedules(): void {
        const container = document.getElementById('schedules-list');
        if (!container) return;

        if (this.schedules.length === 0) {
            container.innerHTML = `
                <p class="error">
                    <span class="lang-es">No hay horarios disponibles</span>
                    <span class="lang-en" style="display:none;">No schedules available</span>
                </p>
            `;
            this.updateLanguageDisplay();
            return;
        }

        container.innerHTML = this.schedules.map(schedule => this.renderScheduleCard(schedule)).join('');
        this.updateLanguageDisplay();
    }

    private renderScheduleCard(schedule: Schedule): string {
        return `
            <div class="schedule-card">
                <h3>${schedule.period}</h3>
                <div class="info">
                    <div class="info-item">
                        <strong>
                            <span class="lang-es">Semestre:</span>
                            <span class="lang-en" style="display:none;">Semester:</span>
                        </strong>
                        <span>${schedule.semester}</span>
                    </div>
                    <div class="info-item">
                        <strong>
                            <span class="lang-es">Año:</span>
                            <span class="lang-en" style="display:none;">Year:</span>
                        </strong>
                        <span>${schedule.year}</span>
                    </div>
                    <div class="info-item">
                        <strong>
                            <span class="lang-es">Grupos:</span>
                            <span class="lang-en" style="display:none;">Groups:</span>
                        </strong>
                        <span>${schedule.total_groups}</span>
                    </div>
                </div>
                <div class="groups-list">
                    ${schedule.groups.slice(0, 3).map(group => this.renderGroupItem(group)).join('')}
                    ${schedule.groups.length > 3 ? `<p style="text-align:center; color: var(--text-secondary); margin-top: 0.5rem;">+ ${schedule.groups.length - 3} más / more</p>` : ''}
                </div>
            </div>
        `;
    }

    private renderGroupItem(group: Group): string {
        const timeSlots = group.time_slots.map(slot => 
            `<span class="time-slot">${slot.day} ${slot.start_time}-${slot.end_time}</span>`
        ).join('');

        return `
            <div class="group-item">
                <h4>${this.currentLanguage === 'es' ? group.class_info.name : group.class_info.name_en || group.class_info.name}</h4>
                <div class="group-info">
                    <p><strong>
                        <span class="lang-es">Código:</span>
                        <span class="lang-en" style="display:none;">Code:</span>
                    </strong> ${group.class_info.code} | 
                    <strong>
                        <span class="lang-es">Grupo:</span>
                        <span class="lang-en" style="display:none;">Group:</span>
                    </strong> ${group.group_number}</p>
                    <p><strong>
                        <span class="lang-es">Profesor:</span>
                        <span class="lang-en" style="display:none;">Professor:</span>
                    </strong> ${group.class_info.professor}</p>
                    ${timeSlots ? `<div style="margin-top: 0.5rem;">${timeSlots}</div>` : ''}
                    <p style="margin-top: 0.5rem;"><strong>
                        <span class="lang-es">Disponibles:</span>
                        <span class="lang-en" style="display:none;">Available:</span>
                    </strong> ${group.available}/${group.capacity}</p>
                </div>
            </div>
        `;
    }

    private async analyzeContent(): Promise<void> {
        const contentInput = document.getElementById('content-input') as HTMLTextAreaElement;
        const analyzeBtn = document.getElementById('analyze-btn') as HTMLButtonElement;
        const resultsDiv = document.getElementById('analysis-results');

        if (!contentInput || !analyzeBtn || !resultsDiv) return;

        const content = contentInput.value.trim();
        if (!content) {
            alert(this.currentLanguage === 'es' ? 
                'Por favor ingrese contenido para analizar' : 
                'Please enter content to analyze');
            return;
        }

        // Disable button and show loading
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = this.currentLanguage === 'es' ? 
            'Analizando...' : 'Analyzing...';

        try {
            const response = await fetch('/api/analyze-content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: content,
                    language: this.currentLanguage
                })
            });

            const data = await response.json();

            if (data.success) {
                this.displayAnalysisResults(data.analysis);
                resultsDiv.style.display = 'block';
            } else {
                this.showError('Error analyzing content: ' + data.error);
            }
        } catch (error) {
            this.showError('Error analyzing content: ' + error);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span class="lang-es">Analizar con AI</span><span class="lang-en" style="display:none;">Analyze with AI</span>';
            this.updateLanguageDisplay();
        }
    }

    private displayAnalysisResults(analysis: AnalysisResult): void {
        const resultsDiv = document.getElementById('analysis-results');
        if (!resultsDiv) return;

        const difficultyClass = analysis.difficulty_level.toLowerCase();

        resultsDiv.innerHTML = `
            <h3>
                <span class="lang-es">Resultados del Análisis</span>
                <span class="lang-en" style="display:none;">Analysis Results</span>
            </h3>
            
            <div class="result-section">
                <h4>
                    <span class="lang-es">Resumen</span>
                    <span class="lang-en" style="display:none;">Summary</span>
                </h4>
                <p>${analysis.summary}</p>
            </div>

            <div class="result-section">
                <h4>
                    <span class="lang-es">Temas Clave</span>
                    <span class="lang-en" style="display:none;">Key Topics</span>
                </h4>
                <ul>
                    ${analysis.key_topics.map(topic => `<li>${topic}</li>`).join('')}
                </ul>
            </div>

            <div class="result-section">
                <h4>
                    <span class="lang-es">Nivel de Dificultad</span>
                    <span class="lang-en" style="display:none;">Difficulty Level</span>
                </h4>
                <span class="difficulty-badge ${difficultyClass}">${analysis.difficulty_level}</span>
            </div>

            ${analysis.prerequisites.length > 0 ? `
                <div class="result-section">
                    <h4>
                        <span class="lang-es">Prerrequisitos</span>
                        <span class="lang-en" style="display:none;">Prerequisites</span>
                    </h4>
                    <ul>
                        ${analysis.prerequisites.map(prereq => `<li>${prereq}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${analysis.recommendations ? `
                <div class="result-section">
                    <h4>
                        <span class="lang-es">Recomendaciones</span>
                        <span class="lang-en" style="display:none;">Recommendations</span>
                    </h4>
                    <p>${analysis.recommendations}</p>
                </div>
            ` : ''}
        `;

        this.updateLanguageDisplay();
    }

    private showError(message: string): void {
        const container = document.getElementById('schedules-list');
        if (container) {
            container.innerHTML = `<p class="error">${message}</p>`;
        }
    }

    private closeModal(): void {
        const modal = document.getElementById('class-modal');
        if (modal) {
            modal.classList.remove('show');
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ScheduleOrganizerApp();
});
