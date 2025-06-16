// Utilise la variable globale BASE_PATH définie dans le template




if (typeof BASE_PATH === 'undefined') {
    console.error('BASE_PATH is not defined. Using fallback /gestion/');
    var BASE_PATH = '/gestion/'; // Fallback pour le développement
}

// Fonction utilitaire pour construire les URLs avec le bon préfixe
function buildUrl(path) {
    return `${BASE_PATH}${path}`;
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation
    loadSection('dashboard');
    
    // Navigation avec mise à jour de l'URL
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const target = this.getAttribute('data-target');
            loadSection(target);
            
            // Mettre à jour l'URL avec le bon préfixe
            history.pushState(null, null, buildUrl(`${target}/`));
        });
    });
    
    // Délégation d'événements pour les éléments dynamiques
    document.addEventListener('click', function(e) {
        // Bouton Ajouter Patient
        if (e.target.matches('#add-patient-btn')) {
            openModal('add-patient-modal');
        }
        
        // Bouton Ajouter Médecin
        if (e.target.matches('#add-doctor-btn')) {
            openModal('add-doctor-modal');
        }
        
        // Bouton Ajouter Rendez-vous
        if (e.target.matches('#add-appointment-btn')) {
            openModal('add-appointment-modal');
            loadPatientsDropdown();
            loadDoctorsDropdown();
        }
        
        // Fermeture des modales
        if (e.target.matches('.close')) {
            const modal = e.target.closest('.modal');
            closeModal(modal.id);
        }
    });
    
    // Délégation d'événements pour les changements dans les formulaires
    document.addEventListener('change', function(e) {
        // Gestion des disponibilités des médecins
        if (e.target.matches('#doctor-availability input[type="checkbox"]')) {
            const dayContainer = e.target.closest('.day-availability');
            const timeInputs = dayContainer.querySelectorAll('input[type="time"]');
            timeInputs.forEach(input => {
                input.disabled = !e.target.checked;
                if (!e.target.checked) {
                    input.value = '';
                }
            });
        }
        
        // Changement de date pour les rendez-vous
        if (e.target.matches('#appointment-date')) {
            const doctorId = document.getElementById('appointment-doctor').value;
            const date = e.target.value;
            
            if (doctorId && date) {
                try {
                    fetch(`${GET_SLOTS_URL}?doctor_id=${doctorId}&date=${date}`)
                        .then(response => response.json())
                        .then(data => renderTimeSlots(data.slots))
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Erreur lors du chargement des créneaux');
                        });
                } catch (error) {
                    console.error('Error:', error);
                    alert('Erreur lors du chargement des créneaux');
                }
            }
        }
    });
    
    // Délégation d'événements pour la soumission des formulaires
    document.addEventListener('submit', function(e) {
        // Authentification
        if (e.target.matches('#login-form')) {
            e.preventDefault();
            const form = e.target;
            const formData = new FormData(form);
            
            fetch(LOGIN_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = buildUrl('dashboard/');
                } else {
                    alert(data.error || 'Erreur de connexion');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion');
            });
        }
        
        // Formulaire Ajout Patient
        if (e.target.matches('#add-patient-form')) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            fetch(ADD_PATIENT_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Patient ajouté avec succès!');
                    closeModal('add-patient-modal');
                    loadPatients();
                } else {
                    alert(data.error || 'Erreur lors de l\'ajout du patient');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur lors de l\'ajout du patient');
            });
        }
        
        // Formulaire Ajout Médecin
        if (e.target.matches('#add-doctor-form')) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            fetch(ADD_DOCTOR_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Médecin ajouté avec succès!');
                    closeModal('add-doctor-modal');
                    loadDoctors();
                } else {
                    alert(data.error || 'Erreur lors de l\'ajout du médecin');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur lors de l\'ajout du médecin');
            });
        }
        
        // Formulaire Ajout Rendez-vous
        if (e.target.matches('#add-appointment-form')) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            // Vérifier qu'un créneau est sélectionné
            if (!document.getElementById('selected-slot').value) {
                alert('Veuillez sélectionner un créneau horaire');
                return;
            }
            
            fetch(ADD_APPOINTMENT_URL, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
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
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur lors de l\'ajout du rendez-vous');
            });
        }
    });
    
    // Déconnexion
    document.getElementById('logout-btn')?.addEventListener('click', () => {
        fetch(LOGOUT_URL)
            .then(() => {
                window.location.href = BASE_PATH;
            });
    });
});

// Ajoutez ces fonctions manquantes
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function loadPatients() {
    fetch(GET_PATIENTS_URL)
        .then(response => response.json())
        .then(data => console.log("Patients chargés", data));
}

function loadDoctors() {
    fetch(GET_DOCTORS_URL)
        .then(response => response.json())
        .then(data => console.log("Médecins chargés", data));
}

function loadPatientsDropdown() {
    fetch(GET_PATIENTS_URL)
        .then(response => response.json())
        .then(patients => {
            const select = document.getElementById('appointment-patient');
            select.innerHTML = '<option value="">Sélectionnez un patient</option>';
            
            patients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = `${patient.first_name} ${patient.last_name}`;
                select.appendChild(option);
            });
        });
}

function loadDoctorsDropdown() {
    fetch(GET_DOCTORS_URL)
        .then(response => response.json())
        .then(doctors => {
            const select = document.getElementById('appointment-doctor');
            select.innerHTML = '<option value="">Sélectionnez un médecin</option>';
            
            doctors.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = `Dr. ${doctor.user__first_name} ${doctor.user__last_name}`;
                select.appendChild(option);
            });
        });
}

function renderTimeSlots(slots) {
    const container = document.getElementById('available-slots');
    container.innerHTML = '';
    
    slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'time-slot-btn';
        btn.textContent = slot;
        btn.onclick = () => {
            document.querySelectorAll('.time-slot-btn').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            document.getElementById('selected-slot').value = slot;
        };
        container.appendChild(btn);
    });
}