document.addEventListener('DOMContentLoaded', () => {
    // Hardcoded statistics from the 800,000 records dataset for offline client-side support
    const PRECALCULATED_STATS = {
        total_students: 800000,
        overall_risk: {
            'Bajo': 58.21,
            'Medio': 31.43,
            'Alto': 10.37
        },
        modality_risk: {
            'Hibrida': { 'Alto': 12.75, 'Bajo': 50.96, 'Medio': 36.29 },
            'Presencial': { 'Alto': 5.44, 'Bajo': 72.90, 'Medio': 21.66 },
            'Virtual': { 'Alto': 12.93, 'Bajo': 50.69, 'Medio': 36.38 }
        },
        attendance_risk: {
            'Hibrida': { 'Alto': 60.69, 'Bajo': 85.00, 'Medio': 68.57 },
            'Presencial': { 'Alto': 73.91, 'Bajo': 88.20, 'Medio': 69.87 },
            'Virtual': { 'Alto': 60.50, 'Bajo': 85.04, 'Medio': 68.61 }
        }
    };

    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        localStorage.setItem('theme', document.body.classList.contains('light-theme') ? 'light' : 'dark');
    });
    
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-theme');
    }

    // Tab Switching
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });

    // Story Node interactive highlight
    const storyNodes = document.querySelectorAll('.story-node');
    storyNodes.forEach(node => {
        node.addEventListener('click', () => {
            storyNodes.forEach(n => n.classList.remove('active'));
            node.classList.add('active');
        });
    });

    // Story Selector Event Handler
    const storySelect = document.getElementById('story-select');
    const storyGroup1 = document.getElementById('story-group-1');
    const storyGroup2 = document.getElementById('story-group-2');

    if (storySelect) {
        storySelect.addEventListener('change', (e) => {
            if (e.target.value === 'story1') {
                storyGroup1.style.display = 'block';
                storyGroup2.style.display = 'none';
                storyNodes.forEach(n => n.classList.remove('active'));
                const firstNode = document.getElementById('story1-node-1');
                if (firstNode) firstNode.classList.add('active');
            } else {
                storyGroup1.style.display = 'none';
                storyGroup2.style.display = 'block';
                storyNodes.forEach(n => n.classList.remove('active'));
                const firstNode = document.getElementById('story2-node-1');
                if (firstNode) firstNode.classList.add('active');
            }
        });
    }

    // Range input sliders elements
    const inputs = {
        modalidad: document.getElementById('input-modalidad'),
        asistencia: document.getElementById('input-asistencia'),
        tareas: document.getElementById('input-tareas'),
        horas: document.getElementById('input-horas'),
        participacion: document.getElementById('input-participacion')
    };

    const valIndicators = {
        asistencia: document.getElementById('val-asistencia'),
        tareas: document.getElementById('val-tareas'),
        horas: document.getElementById('val-horas'),
        participacion: document.getElementById('val-participacion')
    };

    // Bind inputs to updates
    Object.keys(valIndicators).forEach(key => {
        inputs[key].addEventListener('input', (e) => {
            valIndicators[key].textContent = e.target.value;
            triggerPrediction();
        });
    });
    inputs.modalidad.addEventListener('change', triggerPrediction);

    // Dynamic UI risk predictor renderer helper
    function updatePredictionUI(pred, confidence) {
        const riskResult = document.getElementById('risk-result');
        const progressBar = document.getElementById('risk-confidence');
        const riskHint = document.getElementById('risk-hint');
        
        riskResult.className = `pred-value ${pred}`;
        riskResult.textContent = pred;
        
        let barColor = '#10b981'; // Green (Bajo)
        let hintText = '';
        
        if (pred === 'Alto') {
            barColor = '#ef4444'; // Red
            hintText = `Atencion: Alta probabilidad de reprobacion (${confidence}%). Se requiere tutoria obligatoria inmediata.`;
        } else if (pred === 'Medio') {
            barColor = '#f59e0b'; // Orange
            hintText = `Riesgo moderado (${confidence}%). Mantener monitoreo y enviar recordatorios de entrega de tareas.`;
        } else {
            hintText = `Riesgo academico bajo (${confidence}%). Estudiante con buen desempeno general.`;
        }
        
        progressBar.style.backgroundColor = barColor;
        progressBar.style.width = `${confidence}%`;
        riskHint.textContent = hintText;
    }

    // Heuristic client-side prediction engine (Fallback)
    function runClientSidePrediction() {
        const modalidad = inputs.modalidad.value;
        const asistencia = parseFloat(inputs.asistencia.value);
        const tareas = parseInt(inputs.tareas.value);
        
        let prediction = 'Bajo';
        let confidence = 88.0;
        
        if (asistencia < 62 || ((modalidad === 'Virtual' || modalidad === 'Hibrida') && asistencia < 72)) {
            prediction = 'Alto';
            confidence = 85.0;
        } else if (asistencia < 75 || tareas < 7) {
            prediction = 'Medio';
            confidence = 75.0;
        } else {
            prediction = 'Bajo';
            confidence = 88.0;
        }
        
        updatePredictionUI(prediction, confidence);
    }

    // Live Prediction Debouncer
    let debounceTimer;
    function triggerPrediction() {
        clearTimeout(debounceTimer);
        
        // If opened as a local file, predict offline immediately
        if (window.location.protocol === 'file:') {
            runClientSidePrediction();
            return;
        }

        debounceTimer = setTimeout(async () => {
            const payload = {
                modalidad: inputs.modalidad.value,
                asistencia: parseFloat(inputs.asistencia.value),
                tareas_entregadas: parseInt(inputs.tareas.value),
                horas_estudio: parseFloat(inputs.horas.value),
                participacion: parseFloat(inputs.participacion.value),
                uso_plataforma: 40.0
            };

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                
                if (!response.ok) throw new Error('API offline');
                const result = await response.json();
                
                const pred = result.prediction;
                const confidence = result.probabilities[pred];
                updatePredictionUI(pred, confidence);
            } catch (err) {
                // If API fails, fallback to local javascript rule-based engine
                runClientSidePrediction();
            }
        }, 100);
    }

    // Chart.js graphics renderer
    function renderCharts(statsData) {
        // Modality Risk Chart
        const modCtx = document.getElementById('modalityChart').getContext('2d');
        const modalities = Object.keys(statsData.modality_risk);
        
        const highData = modalities.map(m => statsData.modality_risk[m]['Alto']);
        const medData = modalities.map(m => statsData.modality_risk[m]['Medio']);
        const lowData = modalities.map(m => statsData.modality_risk[m]['Bajo']);
        
        new Chart(modCtx, {
            type: 'bar',
            data: {
                labels: modalities,
                datasets: [
                    {
                        label: 'Riesgo Alto',
                        data: highData,
                        backgroundColor: '#ef4444'
                    },
                    {
                        label: 'Riesgo Medio',
                        data: medData,
                        backgroundColor: '#f59e0b'
                    },
                    {
                        label: 'Riesgo Bajo',
                        data: lowData,
                        backgroundColor: '#10b981'
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Distribucion de Riesgo Academico por Modalidad (%)',
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: { position: 'bottom' }
                },
                scales: {
                    x: { stacked: true },
                    y: { stacked: true, max: 100 }
                }
            }
        });

        // Attendance Risk Chart
        const attCtx = document.getElementById('attendanceChart').getContext('2d');
        const attHigh = modalities.map(m => statsData.attendance_risk[m]['Alto']);
        const attMed = modalities.map(m => statsData.attendance_risk[m]['Medio']);
        const attLow = modalities.map(m => statsData.attendance_risk[m]['Bajo']);

        new Chart(attCtx, {
            type: 'bar',
            data: {
                labels: modalities,
                datasets: [
                    {
                        label: 'Asistencia Riesgo Alto',
                        data: attHigh,
                        backgroundColor: 'rgba(239, 68, 68, 0.75)',
                        borderColor: '#ef4444',
                        borderWidth: 1
                    },
                    {
                        label: 'Asistencia Riesgo Medio',
                        data: attMed,
                        backgroundColor: 'rgba(245, 158, 11, 0.75)',
                        borderColor: '#f59e0b',
                        borderWidth: 1
                    },
                    {
                        label: 'Asistencia Riesgo Bajo',
                        data: attLow,
                        backgroundColor: 'rgba(16, 185, 129, 0.75)',
                        borderColor: '#10b981',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Asistencia Promedio (%) por Nivel de Riesgo y Modalidad',
                        color: getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim(),
                        font: { size: 14, weight: 'bold' }
                    },
                    legend: { position: 'bottom' }
                },
                scales: {
                    y: { min: 50, max: 100 }
                }
            }
        });
    }

    // Load statistics
    async function loadStats() {
        if (window.location.protocol === 'file:') {
            renderCharts(PRECALCULATED_STATS);
            return;
        }

        try {
            const response = await fetch('/api/stats');
            if (!response.ok) throw new Error('Stats offline');
            const data = await response.json();
            renderCharts(data);
        } catch (err) {
            // Fallback to precalculated offline stats
            renderCharts(PRECALCULATED_STATS);
        }
    }

    // Initial load calls
    loadStats();
    triggerPrediction();
});
