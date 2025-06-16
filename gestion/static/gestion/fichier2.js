// script.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialisation
    loadSection('dashboard');
    
    // Navigation
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('data-target');
            loadSection(target);
        });
    });
    
    // Authentification
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch('{% url 'login' %}', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                window.location.href = '{% url 'dashboard' %}';
            } else {
                alert(data.error || 'Erreur de connexion');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur de connexion');
        }
    });
    
    // Gestion des patients
    document.getElementById('add-patient-btn')?.addEventListener('click', () => {
        openModal('add-patient-modal');
    });
    
    document.getElementById('add-patient-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/add-patient/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Patient ajouté avec succès!');
                closeModal('add-patient-modal');
                loadPatients();
            } else {
                alert(data.error || 'Erreur lors de l\'ajout du patient');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors de l\'ajout du patient');
        }
    });
    
    // Gestion des médecins
    document.getElementById('add-doctor-btn')?.addEventListener('click', () => {
        openModal('add-doctor-modal');
    });
    
    // Gestion des disponibilités
    document.querySelectorAll('#doctor-availability input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const dayContainer = this.closest('.day-availability');
            const timeInputs = dayContainer.querySelectorAll('input[type="time"]');
            timeInputs.forEach(input => {
                input.disabled = !this.checked;
                if (!this.checked) {
                    input.value = '';
                }
            });
        });
    });
    
    document.getElementById('add-doctor-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        try {
            const response = await fetch('/add-doctor/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Médecin ajouté avec succès!');
                closeModal('add-doctor-modal');
                loadDoctors();
            } else {
                alert(data.error || 'Erreur lors de l\'ajout du médecin');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors de l\'ajout du médecin');
        }
    });
    
    // Gestion des rendez-vous
    document.getElementById('add-appointment-btn')?.addEventListener('click', () => {
        openModal('add-appointment-modal');
        loadPatientsDropdown();
        loadDoctorsDropdown();
    });
    
    document.getElementById('appointment-date')?.addEventListener('change', async function() {
        const doctorId = document.getElementById('appointment-doctor').value;
        const date = this.value;
        
        if (doctorId && date) {
            try {
                const response = await fetch(`/get-slots/?doctor_id=${doctorId}&date=${date}`);
                const data = await response.json();
                renderTimeSlots(data.slots);
            } catch (error) {
                console.error('Error:', error);
                alert('Erreur lors du chargement des créneaux');
            }
        }
    });
    
    document.getElementById('add-appointment-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        
        // Vérifier qu'un créneau est sélectionné
        if (!document.getElementById('selected-slot').value) {
            alert('Veuillez sélectionner un créneau horaire');
            return;
        }
        
        try {
            const response = await fetch('/add-appointment/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            if (data.success) {
                alert('Rendez-vous ajouté avec succès!');
                closeModal('add-appointment-modal');
                loadAppointments();
                if (currentSection === 'calendar') {
                    loadCalendar();
                }
            } else {
                alert(data.error || 'Erreur lors de l\'ajout du rendez-vous');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Erreur lors de l\'ajout du rendez-vous');
        }
    });
    
    // Déconnexion
    document.getElementById('logout-btn')?.addEventListener('click', () => {
        fetch('/logout/')
            .then(() => {
                window.location.href = '/';
            });
    });
});

// Fonctions utilitaires
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let currentSection = 'dashboard';

async function loadSection(section) {
    document.querySelectorAll('.page-content').forEach(el => {
        el.classList.remove('active');
    });
    
    const content = document.getElementById(`${section}-content`);
    if (content) {
        content.classList.add('active');
        currentSection = section;
        
        // Mettre à jour le titre de la page
        document.getElementById('page-title').textContent = 
            document.querySelector(`[data-target="${section}"]`).textContent;
        
        // Charger les données spécifiques à la section
        if (section === 'dashboard') loadDashboard();
        if (section === 'patients') loadPatients();
        if (section === 'doctors') loadDoctors();
        if (section === 'appointments') loadAppointments();
        if (section === 'calendar') loadCalendar();
    }
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Fonctions de chargement des données
async function loadPatients() {
    try {
        const response = await fetch('/patients/');
        const html = await response.text();
        document.getElementById('patients-content').innerHTML = html;
    } catch (error) {
        console.error('Error loading patients:', error);
    }
}

async function loadDoctors() {
    try {
        const response = await fetch('/doctors/');
        const html = await response.text();
        document.getElementById('doctors-content').innerHTML = html;
    } catch (error) {
        console.error('Error loading doctors:', error);
    }
}

async function loadPatientsDropdown() {
    try {
        const response = await fetch('/get-patients/');
        const patients = await response.json();
        const select = document.getElementById('appointment-patient');
        select.innerHTML = '';
        
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = `${patient.first_name} ${patient.last_name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading patients dropdown:', error);
    }
}

async function loadDoctorsDropdown() {
    try {
        const response = await fetch('/get-doctors/');
        const doctors = await response.json();
        const select = document.getElementById('appointment-doctor');
        select.innerHTML = '';
        
        doctors.forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.id;
            option.textContent = `${doctor.user__first_name} ${doctor.user__last_name}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading doctors dropdown:', error);
    }
}

function renderTimeSlots(slots) {
    const container = document.getElementById('time-slots');
    container.innerHTML = '';
    
    if (slots.length === 0) {
        container.innerHTML = '<p>Aucun créneau disponible</p>';
        return;
    }
    
    slots.forEach(slot => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'time-slot-btn';
        button.textContent = slot;
        button.addEventListener('click', function() {
            document.querySelectorAll('.time-slot-btn').forEach(btn => {
                btn.classList.remove('selected');
            });
            this.classList.add('selected');
            document.getElementById('selected-slot').value = slot;
        });
        container.appendChild(button);
    });
}

// Fonctions pour les autres sections
function loadDashboard() {
    // Actualiser les données du tableau de bord
    fetch('/dashboard/')
        .then(response => response.text())
        .then(html => {
            document.getElementById('dashboard-content').innerHTML = html;
        });
}

function loadAppointments() {
    // Actualiser les rendez-vous
    fetch('/appointments/')
        .then(response => response.text())
        .then(html => {
            document.getElementById('appointments-content').innerHTML = html;
        });
}

function loadCalendar() {
    // Implémenter le calendrier complet
    // (Utiliser une bibliothèque comme FullCalendar serait idéal)
    document.getElementById('calendar-content').innerHTML = `
        <div class="calendar-controls">
            <button id="prev-month">&lt;</button>
            <h3 id="current-month">${new Date().toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</h3>
            <button id="next-month">&gt;</button>
        </div>
        <div id="calendar-view"></div>
    `;
    
    // Implémenter la navigation dans le calendrier
    document.getElementById('prev-month')?.addEventListener('click', () => {
        // Logique pour le mois précédent
    });
    
    document.getElementById('next-month')?.addEventListener('click', () => {
        // Logique pour le mois suivant
    });
    
    // Charger les rendez-vous pour le mois en cours
}

document.querySelectorAll('#doctor-availability input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const day = this.id.replace('avail-', '');
        document.getElementById(`${day}-start`).disabled = !this.checked;
        document.getElementById(`${day}-end`).disabled = !this.checked;
    });
});

function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'block';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
    }
}
