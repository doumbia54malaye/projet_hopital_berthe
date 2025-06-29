// gestion/static/gestion/fichier2.js

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const loginPage = document.getElementById('login-page');
    const appContainer = document.getElementById('app-container');
    const usernameDisplay = document.getElementById('username-display');
    const userAvatar = document.getElementById('user-avatar');
    const pageTitle = document.getElementById('page-title');
    const menuItems = document.querySelectorAll('.sidebar-menu .menu-item');
    const pageContents = document.querySelectorAll('.page-content');
    
    // Buttons to open modals
    const addPatientBtn = document.getElementById('add-patient-btn');
    const addDoctorBtn = document.getElementById('add-doctor-btn');
    const addAppointmentBtn = document.getElementById('add-appointment-btn');

    // Buttons to save data in modals
    const savePatientBtn = document.getElementById('save-patient-btn');
    const saveDoctorBtn = document.getElementById('save-doctor-btn');
    const saveAppointmentBtn = document.getElementById('save-appointment-btn');
    const cancelAppointmentBtn = document.getElementById('cancel-appointment-btn'); // New button for cancelling appt

    // Modals themselves
    const addPatientModal = document.getElementById('add-patient-modal');
    const addDoctorModal = document.getElementById('add-doctor-modal');
    const addAppointmentModal = document.getElementById('add-appointment-modal');
    const viewPatientModal = document.getElementById('view-patient-modal'); // Assuming you want to view details
    const viewAppointmentModal = document.getElementById('view-appointment-modal'); // Assuming you want to view details

    // Forms within modals
    const addPatientForm = document.getElementById('add-patient-form');
    const addDoctorForm = document.getElementById('add-doctor-form');
    const addAppointmentForm = document.getElementById('add-appointment-form');

    // Calendar elements
    const prevMonthBtn = document.getElementById('prev-month');
    const nextMonthBtn = document.getElementById('next-month');
    const currentMonthSpan = document.getElementById('current-month');
    const appointmentCalendar = document.getElementById('appointment-calendar');

    let currentCalendarDate = new Date(); // To track month in calendar view

    // Close buttons for modals (common logic)
    document.querySelectorAll('.modal .close, .modal .btn-danger.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal').style.display = 'none';
            // Reset forms on close
            if (btn.closest('.modal').id === 'add-patient-modal') addPatientForm.reset();
            if (btn.closest('.modal').id === 'add-doctor-modal') {
                addDoctorForm.reset();
                document.querySelectorAll('#doctor-availability input[type="time"]').forEach(input => input.disabled = true);
            }
            if (btn.closest('.modal').id === 'add-appointment-modal') addAppointmentForm.reset();
        });
    });

    // --- CSRF Token for Django POST requests ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    async function fetchData(url, method = 'GET', data = null) {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
        };
        if (data) {
            options.body = JSON.stringify(data);
        }
        const response = await fetch(url, options);
        if (response.status === 204) return null; // No content for delete
        if (!response.ok) {
            let errorData = {};
            try {
                errorData = await response.json();
            } catch (e) {
                errorData.message = response.statusText;
            }
            throw new Error(errorData.message || `Erreur: ${response.status}`);
        }
        return response.json();
    }

    // --- Login Logic ---
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const usernameInput = document.getElementById('login-username').value;
        const passwordInput = document.getElementById('login-password').value;

        try {
            // Adjust the URL for your Django login endpoint
            const data = await fetchData('/gestion/api/login/', 'POST', { username: usernameInput, password: passwordInput });
            if (data.success) {
                loginPage.style.display = 'none';
                appContainer.style.display = 'flex';
                usernameDisplay.textContent = data.username;
                userAvatar.textContent = data.username.charAt(0).toUpperCase();
                alert('Connexion réussie ! Bienvenue ' + data.username);

                // Initialize app functionalities after successful login
                updateDashboardStats();
                loadPatients();
                loadDoctors();
                loadAppointments('today'); // Load today's appointments by default
                renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth());
                showPage('dashboard');
            } else {
                alert(data.message || 'Identifiant ou mot de passe incorrect. Veuillez réessayer.');
            }
        } catch (error) {
            alert('Erreur de connexion: ' + error.message);
            console.error('Login error:', error);
        }
    });

    // --- Navigation Logic ---
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            menuItems.forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const targetPage = item.dataset.target;
            showPage(targetPage);
            // Re-load data when navigating to ensure freshness
            if (targetPage === 'patients') loadPatients();
            if (targetPage === 'doctors') loadDoctors();
            if (targetPage === 'appointments') {
                // Ensure the 'today' tab is active and loaded when entering appointments
                document.querySelectorAll('.tabs .tab').forEach(tab => tab.classList.remove('active'));
                document.querySelector('.tabs .tab[data-tab="today"]').classList.add('active');
                document.querySelectorAll('.tab-content').forEach(content => content.style.display = 'none');
                document.getElementById('today-tab').style.display = 'block';
                loadAppointments('today');
            }
            if (targetPage === 'calendar') {
                renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth());
            }
        });
    });

    function showPage(pageId) {
        pageContents.forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(`${pageId}-content`).style.display = 'block';
        pageTitle.textContent = document.querySelector(`.sidebar-menu [data-target="${pageId}"]`).textContent.trim();
    }

    // --- Dashboard Stats ---
    async function updateDashboardStats() {
        try {
            const stats = await fetchData('/gestion/api/dashboard-stats/');
            document.getElementById('today-appointments').textContent = stats.today_appointments;
            document.getElementById('available-doctors').textContent = stats.available_doctors;
            document.getElementById('total-patients').textContent = stats.total_patients;
            document.getElementById('upcoming-appointments').textContent = stats.upcoming_appointments;

            // Populate upcoming appointments table on dashboard
            const upcomingAppts = await fetchData('/gestion/api/appointments/?filter=upcoming&limit=5'); // Limit to 5 for dashboard
            populateAppointmentsTable('upcoming-appointments-table', upcomingAppts, false); // No actions needed here
        } catch (error) {
            console.error('Error fetching dashboard stats:', error);
            // alert('Erreur lors du chargement des statistiques du tableau de bord.'); // Avoid multiple alerts on load
        }
    }

    // --- Patients Management ---
    addPatientBtn.addEventListener('click', () => {
        addPatientForm.reset();
        addPatientModal.style.display = 'block';
    });

    savePatientBtn.addEventListener('click', async () => {
        const patientData = {
            last_name: document.getElementById('patient-lastname').value,
            first_name: document.getElementById('patient-firstname').value,
            phone: document.getElementById('patient-phone').value,
            gender: document.getElementById('patient-gender').value,
            birth_date: document.getElementById('patient-birthdate').value,
            address: document.getElementById('patient-address').value,
        };

        try {
            let response;
            const patientId = addPatientForm.dataset.patientId; // Check if we are editing
            if (patientId) {
                response = await fetchData(`/gestion/api/patients/${patientId}/`, 'PUT', patientData);
                alert('Patient modifié avec succès !');
                addPatientForm.dataset.patientId = ''; // Clear edit mode
            } else {
                response = await fetchData('/gestion/api/patients/', 'POST', patientData);
                alert('Patient ajouté avec succès !');
            }
            addPatientModal.style.display = 'none';
            addPatientForm.reset();
            loadPatients(); // Reload list
            updateDashboardStats(); // Update stats
        } catch (error) {
            alert('Erreur lors de l\'enregistrement du patient: ' + error.message);
            console.error('Save patient error:', error);
        }
    });

    async function loadPatients(searchQuery = '') {
        try {
            let url = '/gestion/api/patients/';
            if (searchQuery) {
                url += `?search=${encodeURIComponent(searchQuery)}`;
            }
            const patients = await fetchData(url);
            const tableBody = document.querySelector('#patients-table tbody');
            tableBody.innerHTML = ''; // Clear existing rows

            if (patients && patients.length > 0) {
                patients.forEach(patient => {
                    const row = tableBody.insertRow();
                    row.insertCell().textContent = patient.id;
                    row.insertCell().textContent = patient.last_name;
                    row.insertCell().textContent = patient.first_name;
                    row.insertCell().textContent = patient.phone;
                    row.insertCell().textContent = patient.gender;
                    row.insertCell().textContent = patient.birth_date;
                    const actionsCell = row.insertCell();

                    const viewBtn = document.createElement('button');
                    viewBtn.innerHTML = '<i class="fas fa-eye"></i>';
                    viewBtn.classList.add('btn', 'btn-info', 'btn-sm');
                    viewBtn.title = 'Voir';
                    viewBtn.addEventListener('click', () => viewPatientDetails(patient.id));
                    actionsCell.appendChild(viewBtn);

                    const editBtn = document.createElement('button');
                    editBtn.innerHTML = '<i class="fas fa-edit"></i>';
                    editBtn.classList.add('btn', 'btn-warning', 'btn-sm');
                    editBtn.title = 'Modifier';
                    editBtn.addEventListener('click', () => editPatient(patient.id));
                    actionsCell.appendChild(editBtn);

                    const deleteBtn = document.createElement('button');
                    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                    deleteBtn.classList.add('btn', 'btn-danger', 'btn-sm');
                    deleteBtn.title = 'Supprimer';
                    deleteBtn.addEventListener('click', () => deletePatient(patient.id));
                    actionsCell.appendChild(deleteBtn);
                });
            } else {
                const row = tableBody.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 7;
                cell.textContent = 'Aucun patient trouvé.';
                cell.style.textAlign = 'center';
            }
        } catch (error) {
            console.error('Error loading patients:', error);
            alert('Erreur lors du chargement des patients: ' + error.message);
        }
    }

    async function editPatient(id) {
        try {
            const patient = await fetchData(`/gestion/api/patients/${id}/`);
            document.getElementById('patient-lastname').value = patient.last_name;
            document.getElementById('patient-firstname').value = patient.first_name;
            document.getElementById('patient-phone').value = patient.phone;
            document.getElementById('patient-gender').value = patient.gender;
            document.getElementById('patient-birthdate').value = patient.birth_date;
            document.getElementById('patient-address').value = patient.address;
            addPatientForm.dataset.patientId = patient.id; // Store ID for update
            addPatientModal.style.display = 'block';
        } catch (error) {
            alert('Erreur lors de la récupération du patient pour modification: ' + error.message);
            console.error('Edit patient error:', error);
        }
    }

    async function deletePatient(id) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce patient et tous ses rendez-vous ?')) {
            try {
                await fetchData(`/gestion/api/patients/${id}/`, 'DELETE');
                alert('Patient supprimé avec succès !');
                loadPatients(); // Reload list
                updateDashboardStats(); // Update stats
            } catch (error) {
                alert('Erreur lors de la suppression du patient: ' + error.message);
                console.error('Delete patient error:', error);
            }
        }
    }
 

      // Nouvelle fonction scheduleAppointment qui prend l'ID du patient
    function scheduleAppointment(patientId) {
        if (patientId) {
        // Adaptez cette URL en fonction de votre configuration Django
        // Si votre application 'gestion' est incluse sous le préfixe 'gestion/' dans votre urls.py principal:
        window.location.href = `/gestion/patients/${patientId}/prendre_rendezvous/`;
        console.log("Redirection vers : " + window.location.href);
    } else {
        console.error("Erreur: ID du patient introuvable pour la prise de rendez-vous.");
        alert("Impossible de prendre rendez-vous. ID du patient introuvable.");
    }
}







    async function viewPatientDetails(id) {
        try {
            const patient = await fetchData(`/gestion/api/patients/${id}/`);
            const appointments = await fetchData(`/gestion/api/appointments/?patient=${id}`); // Get appointments for this patient

            let detailsHtml = `
                <p><strong>Nom:</strong> ${patient.last_name}</p>
                <p><strong>Prénom:</strong> ${patient.first_name}</p>
                <p><strong>Téléphone:</strong> ${patient.phone}</p>
                <p><strong>Sexe:</strong> ${patient.gender}</p>
                <p><strong>Date de naissance:</strong> ${patient.birth_date}</p>
                <p><strong>Adresse:</strong> ${patient.address || 'N/A'}</p>
            `;
            document.getElementById('patient-details').innerHTML = detailsHtml;

            const apptTableBody = document.querySelector('#patient-appointments-table tbody');
            apptTableBody.innerHTML = '';
            if (appointments && appointments.length > 0) {
                appointments.forEach(appt => {
                    const row = apptTableBody.insertRow();
                    row.insertCell().textContent = appt.date;
                    row.insertCell().textContent = `${appt.doctor_first_name} ${appt.doctor_last_name}`;
                    row.insertCell().textContent = appt.reason;
                    row.insertCell().textContent = appt.status;
                });
            } else {
                const row = apptTableBody.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 4;
                cell.textContent = 'Aucun rendez-vous pour ce patient.';
                cell.style.textAlign = 'center';
            }

            viewPatientModal.style.display = 'block';
        } catch (error) {
            alert('Erreur lors de l\'affichage des détails du patient: ' + error.message);
            console.error('View patient details error:', error);
        }
    }

    // Patient Search
    document.getElementById('patient-search-btn').addEventListener('click', () => {
        const searchQuery = document.getElementById('patient-search').value;
        loadPatients(searchQuery);
    });
    document.getElementById('patient-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('patient-search-btn').click();
        }
    });

    // --- Doctors Management ---
    addDoctorBtn.addEventListener('click', () => {
        addDoctorForm.reset();
        document.querySelectorAll('#doctor-availability input[type="time"]').forEach(input => input.disabled = true);
        document.querySelectorAll('#doctor-availability input[type="checkbox"]').forEach(checkbox => checkbox.checked = false);
        addDoctorModal.style.display = 'block';
    });

    // Toggle time inputs based on checkbox
    document.querySelectorAll('#doctor-availability input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', (event) => {
            const parent = event.target.closest('.availability-day');
            const timeInputs = parent.querySelectorAll('input[type="time"]');
            timeInputs.forEach(input => input.disabled = !event.target.checked);
        });
    });

    saveDoctorBtn.addEventListener('click', async () => {
        const availability = {};
        document.querySelectorAll('.availability-day').forEach(dayDiv => {
            const checkbox = dayDiv.querySelector('input[type="checkbox"]');
            if (checkbox.checked) {
                const day = checkbox.value;
                const startTime = dayDiv.querySelector('input[name="start-time"]').value;
                const endTime = dayDiv.querySelector('input[name="end-time"]').value;
                if (startTime && endTime) { // Ensure times are entered
                    availability[day] = `${startTime}-${endTime}`;
                }
            }
        });

        const doctorData = {
            last_name: document.getElementById('doctor-lastname').value,
            first_name: document.getElementById('doctor-firstname').value,
            specialty: document.getElementById('doctor-specialty').value,
            phone: document.getElementById('doctor-phone').value,
            availability: availability, // Store as JSON string or object, depending on Django model
        };

        try {
            let response;
            const doctorId = addDoctorForm.dataset.doctorId;
            if (doctorId) {
                response = await fetchData(`/gestion/api/doctors/${doctorId}/`, 'PUT', doctorData);
                alert('Médecin modifié avec succès !');
                addDoctorForm.dataset.doctorId = '';
            } else {
                response = await fetchData('/gestion/api/doctors/', 'POST', doctorData);
                alert('Médecin ajouté avec succès !');
            }
            addDoctorModal.style.display = 'none';
            addDoctorForm.reset();
            loadDoctors();
            updateDashboardStats();
        } catch (error) {
            alert('Erreur lors de l\'enregistrement du médecin: ' + error.message);
            console.error('Save doctor error:', error);
        }
    });

    async function loadDoctors() {
        try {
            const doctors = await fetchData('/gestion/api/doctors/');
            const tableBody = document.querySelector('#doctors-table tbody');
            tableBody.innerHTML = '';

            if (doctors && doctors.length > 0) {
                doctors.forEach(doctor => {
                    const row = tableBody.insertRow();
                    row.insertCell().textContent = doctor.id;
                    row.insertCell().textContent = doctor.last_name;
                    row.insertCell().textContent = doctor.first_name;
                    row.insertCell().textContent = doctor.specialty;

                    let availabilityText = '';
                    if (doctor.availability) {
                        try {
                            const availObj = typeof doctor.availability === 'string' ? JSON.parse(doctor.availability) : doctor.availability;
                            availabilityText = Object.entries(availObj)
                                .map(([day, time]) => `${day}: ${time}`)
                                .join(', ');
                        } catch (e) {
                            console.error('Error parsing doctor availability:', e);
                            availabilityText = 'Format invalide';
                        }
                    }
                    row.insertCell().textContent = availabilityText || 'Non spécifié';

                    const actionsCell = row.insertCell();
                    const editBtn = document.createElement('button');
                    editBtn.innerHTML = '<i class="fas fa-edit"></i>';
                    editBtn.classList.add('btn', 'btn-warning', 'btn-sm');
                    editBtn.title = 'Modifier';
                    editBtn.addEventListener('click', () => editDoctor(doctor.id));
                    actionsCell.appendChild(editBtn);

                    const deleteBtn = document.createElement('button');
                    deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                    deleteBtn.classList.add('btn', 'btn-danger', 'btn-sm');
                    deleteBtn.title = 'Supprimer';
                    deleteBtn.addEventListener('click', () => deleteDoctor(doctor.id));
                    actionsCell.appendChild(deleteBtn);
                });
            } else {
                const row = tableBody.insertRow();
                const cell = row.insertCell();
                cell.colSpan = 6;
                cell.textContent = 'Aucun médecin trouvé.';
                cell.style.textAlign = 'center';
            }
        } catch (error) {
            console.error('Error loading doctors:', error);
            alert('Erreur lors du chargement des médecins: ' + error.message);
        }
    }

    async function editDoctor(id) {
        try {
            const doctor = await fetchData(`/gestion/api/doctors/${id}/`);
            document.getElementById('doctor-lastname').value = doctor.last_name;
            document.getElementById('doctor-firstname').value = doctor.first_name;
            document.getElementById('doctor-specialty').value = doctor.specialty;
            document.getElementById('doctor-phone').value = doctor.phone;

            // Reset checkboxes and time inputs first
            document.querySelectorAll('#doctor-availability input[type="checkbox"]').forEach(checkbox => {
                checkbox.checked = false;
                const parent = checkbox.closest('.availability-day');
                parent.querySelector('input[name="start-time"]').value = '';
                parent.querySelector('input[name="end-time"]').value = '';
                parent.querySelectorAll('input[type="time"]').forEach(input => input.disabled = true);
            });

            if (doctor.availability) {
                const availObj = typeof doctor.availability === 'string' ? JSON.parse(doctor.availability) : doctor.availability;
                for (const day in availObj) {
                    const dayCheckbox = document.querySelector(`#doctor-availability input[value="${day}"]`);
                    if (dayCheckbox) {
                        dayCheckbox.checked = true;
                        const parent = dayCheckbox.closest('.availability-day');
                        const [startTime, endTime] = availObj[day].split('-');
                        parent.querySelector('input[name="start-time"]').value = startTime;
                        parent.querySelector('input[name="end-time"]').value = endTime;
                        parent.querySelectorAll('input[type="time"]').forEach(input => input.disabled = false);
                    }
                }
            }

            addDoctorForm.dataset.doctorId = doctor.id;
            addDoctorModal.style.display = 'block';
        } catch (error) {
            alert('Erreur lors de la récupération du médecin pour modification: ' + error.message);
            console.error('Edit doctor error:', error);
        }
    }

    async function deleteDoctor(id) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce médecin et ses rendez-vous associés ?')) {
            try {
                await fetchData(`/gestion/api/doctors/${id}/`, 'DELETE');
                alert('Médecin supprimé avec succès !');
                loadDoctors();
                loadAppointments('all'); // Refresh appointments as well
                updateDashboardStats();
            } catch (error) {
                alert('Erreur lors de la suppression du médecin: ' + error.message);
                console.error('Delete doctor error:', error);
            }
        }
    }

    // --- Appointments Management ---
    const appointmentTabs = document.querySelectorAll('.appointments-content .tabs .tab');
    appointmentTabs.forEach(tab => {
        tab.addEventListener('click', (event) => {
            appointmentTabs.forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            const targetTabId = event.target.dataset.tab;
            document.querySelectorAll('.appointments-content .tab-content').forEach(content => {
                content.style.display = 'none';
            });
            document.getElementById(`${targetTabId}-tab`).style.display = 'block';
            loadAppointments(targetTabId);
        });
    });

    addAppointmentBtn.addEventListener('click', async () => {
        addAppointmentForm.reset();
        await populateAppointmentPatientsDropdown();
        await populateAppointmentDoctorsDropdown();
        document.getElementById('time-slots').innerHTML = ''; // Clear time slots initially
        addAppointmentModal.style.display = 'block';
    });

    async function populateAppointmentPatientsDropdown() {
        const selectElement = document.getElementById('appointment-patient');
        selectElement.innerHTML = '<option value="">Sélectionner un patient</option>';
        try {
            const patients = await fetchData('/gestion/api/patients/');
            patients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = `${patient.first_name} ${patient.last_name}`;
                selectElement.appendChild(option);
            });
        } catch (error) {
            console.error('Error populating patients dropdown:', error);
        }
    }

    async function populateAppointmentDoctorsDropdown() {
        const selectElement = document.getElementById('appointment-doctor');
        selectElement.innerHTML = '<option value="">Sélectionner un médecin</option>';
        try {
            const doctors = await fetchData('/gestion/api/doctors/');
            doctors.forEach(doctor => {
                const option = document.createElement('option');
                option.value = doctor.id;
                option.textContent = `${doctor.first_name} ${doctor.last_name} (${doctor.specialty})`;
                selectElement.appendChild(option);
            });
        } catch (error) {
            console.error('Error populating doctors dropdown:', error);
        }
    }

    document.getElementById('appointment-doctor').addEventListener('change', fetchAvailableTimeSlots);
    document.getElementById('appointment-date').addEventListener('change', fetchAvailableTimeSlots);

    async function fetchAvailableTimeSlots() {
        const doctorId = document.getElementById('appointment-doctor').value;
        const date = document.getElementById('appointment-date').value;
        const timeSlotsContainer = document.getElementById('time-slots');
        timeSlotsContainer.innerHTML = ''; // Clear previous slots

        if (!doctorId || !date) {
            timeSlotsContainer.textContent = 'Sélectionnez un médecin et une date pour voir les créneaux.';
            return;
        }

        try {
            // Assume API can give available slots for a doctor on a specific date
            // This might require a custom endpoint on Django side
            const availableSlots = await fetchData(`/gestion/api/doctors/${doctorId}/availability/?date=${date}`);
            
            if (availableSlots && availableSlots.length > 0) {
                availableSlots.forEach(slot => {
                    const radioDiv = document.createElement('div');
                    radioDiv.classList.add('time-slot-option');
                    const radioInput = document.createElement('input');
                    radioInput.type = 'radio';
                    radioInput.name = 'appointment-time';
                    radioInput.value = slot; // e.g., "09:00"
                    radioInput.id = `time-${slot.replace(':', '-')}`; // Unique ID
                    
                    const radioLabel = document.createElement('label');
                    radioLabel.htmlFor = `time-${slot.replace(':', '-')}`;
                    radioLabel.textContent = slot;

                    radioDiv.appendChild(radioInput);
                    radioDiv.appendChild(radioLabel);
                    timeSlotsContainer.appendChild(radioDiv);
                });
            } else {
                timeSlotsContainer.textContent = 'Aucun créneau disponible pour cette date et ce médecin.';
            }

        } catch (error) {
            console.error('Error fetching time slots:', error);
            timeSlotsContainer.textContent = 'Erreur lors du chargement des créneaux. Veuillez réessayer.';
        }
    }

    saveAppointmentBtn.addEventListener('click', async () => {
        const selectedPatient = document.getElementById('appointment-patient').value;
        const selectedDoctor = document.getElementById('appointment-doctor').value;
        const selectedDate = document.getElementById('appointment-date').value;
        const selectedTimeInput = document.querySelector('input[name="appointment-time"]:checked');
        const selectedTime = selectedTimeInput ? selectedTimeInput.value : '';
        const reason = document.getElementById('appointment-reason').value;

        if (!selectedPatient || !selectedDoctor || !selectedDate || !selectedTime || !reason) {
            alert('Veuillez remplir tous les champs obligatoires pour le rendez-vous.');
            return;
        }

        const appointmentData = {
            patient: selectedPatient,
            doctor: selectedDoctor,
            date: selectedDate,
            time: selectedTime,
            reason: reason,
            status: 'Prévu' // Default status
        };

        try {
            let response;
            const appointmentId = addAppointmentForm.dataset.appointmentId;
            if (appointmentId) {
                response = await fetchData(`/gestion/api/appointments/${appointmentId}/`, 'PUT', appointmentData);
                alert('Rendez-vous modifié avec succès !');
                addAppointmentForm.dataset.appointmentId = '';
            } else {
                response = await fetchData('/gestion/api/appointments/', 'POST', appointmentData);
                alert('Rendez-vous pris avec succès !');
            }
            addAppointmentModal.style.display = 'none';
            addAppointmentForm.reset();
            loadAppointments(document.querySelector('.appointments-content .tabs .tab.active').dataset.tab); // Reload current tab
            updateDashboardStats();
            renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth()); // Refresh calendar
        } catch (error) {
            alert('Erreur lors de la prise/modification du rendez-vous: ' + error.message);
            console.error('Save appointment error:', error);
        }
    });

    async function loadAppointments(filter = 'today') {
        let url = '/gestion/api/appointments/';
        if (filter === 'today') {
            url += '?filter=today';
        } else if (filter === 'upcoming') {
            url += '?filter=upcoming';
        } else if (filter === 'all') {
            // No specific filter needed for 'all'
        }

        try {
            const appointments = await fetchData(url);
            const tableId = `${filter}-appointments-table`;
            populateAppointmentsTable(tableId, appointments, true); // Pass true to include actions
        } catch (error) {
            console.error(`Error loading ${filter} appointments:`, error);
            // alert(`Erreur lors du chargement des rendez-vous (${filter}): ` + error.message);
        }
    }

    function populateAppointmentsTable(tableId, appointments, includeActions) {
        const tableBody = document.querySelector(`#${tableId} tbody`);
        tableBody.innerHTML = '';

        if (appointments && appointments.length > 0) {
            appointments.forEach(appt => {
                const row = tableBody.insertRow();
                if (tableId !== 'upcoming-appointments-table' || includeActions) { // Add date column for non-dashboard upcoming
                    if (tableId === 'upcoming-appointments-table' && !includeActions || tableId === 'all-appointments-table' || tableId === 'patient-appointments-table') {
                        row.insertCell().textContent = appt.date;
                    }
                }
                row.insertCell().textContent = appt.time;
                row.insertCell().textContent = `${appt.patient_first_name} ${appt.patient_last_name}`;
                row.insertCell().textContent = `${appt.doctor_first_name} ${appt.doctor_last_name}`;
                row.insertCell().textContent = appt.reason;
                const statusCell = row.insertCell();
                statusCell.textContent = appt.status;
                // Add class for styling status
                statusCell.classList.add(`status-${appt.status.toLowerCase().replace(' ', '-')}`);

                if (includeActions) {
                    const actionsCell = row.insertCell();

                    const viewBtn = document.createElement('button');
                    viewBtn.innerHTML = '<i class="fas fa-eye"></i>';
                    viewBtn.classList.add('btn', 'btn-info', 'btn-sm');
                    viewBtn.title = 'Voir';
                    viewBtn.addEventListener('click', () => viewAppointmentDetails(appt.id));
                    actionsCell.appendChild(viewBtn);

                    const editBtn = document.createElement('button');
                    editBtn.innerHTML = '<i class="fas fa-edit"></i>';
                    editBtn.classList.add('btn', 'btn-warning', 'btn-sm');
                    editBtn.title = 'Modifier';
                    editBtn.addEventListener('click', () => editAppointment(appt.id));
                    actionsCell.appendChild(editBtn);

                    if (appt.status !== 'Annulé' && appt.status !== 'Terminé') {
                        const cancelBtn = document.createElement('button');
                        cancelBtn.innerHTML = '<i class="fas fa-times-circle"></i>';
                        cancelBtn.classList.add('btn', 'btn-danger', 'btn-sm');
                        cancelBtn.title = 'Annuler';
                        cancelBtn.addEventListener('click', () => cancelAppointment(appt.id));
                        actionsCell.appendChild(cancelBtn);
                    }
                }
            });
        } else {
            const row = tableBody.insertRow();
            const cell = row.insertCell();
            cell.colSpan = includeActions ? 6 : 5; // Adjust colspan based on action column
            cell.textContent = 'Aucun rendez-vous trouvé.';
            cell.style.textAlign = 'center';
        }
    }

    async function viewAppointmentDetails(id) {
        try {
            const appt = await fetchData(`/gestion/api/appointments/${id}/`);
            let detailsHtml = `
                <p><strong>Patient:</strong> ${appt.patient_first_name} ${appt.patient_last_name}</p>
                <p><strong>Médecin:</strong> ${appt.doctor_first_name} ${appt.doctor_last_name} (${appt.doctor_specialty})</p>
                <p><strong>Date:</strong> ${appt.date}</p>
                <p><strong>Heure:</strong> ${appt.time}</p>
                <p><strong>Motif:</strong> ${appt.reason}</p>
                <p><strong>Statut:</strong> <span class="status-${appt.status.toLowerCase().replace(' ', '-')}">${appt.status}</span></p>
            `;
            document.getElementById('appointment-details').innerHTML = detailsHtml;
            
            // Set data-appointment-id on the cancel button for easy access
            cancelAppointmentBtn.dataset.appointmentId = appt.id;
            // Show/hide cancel button based on status
            if (appt.status === 'Annulé' || appt.status === 'Terminé') {
                cancelAppointmentBtn.style.display = 'none';
            } else {
                cancelAppointmentBtn.style.display = 'inline-block';
            }

            viewAppointmentModal.style.display = 'block';
        } catch (error) {
            alert('Erreur lors de l\'affichage des détails du rendez-vous: ' + error.message);
            console.error('View appointment details error:', error);
        }
    }

    async function editAppointment(id) {
        try {
            const appt = await fetchData(`/gestion/api/appointments/${id}/`);
            await populateAppointmentPatientsDropdown();
            await populateAppointmentDoctorsDropdown();

            document.getElementById('appointment-patient').value = appt.patient;
            document.getElementById('appointment-doctor').value = appt.doctor;
            document.getElementById('appointment-date').value = appt.date;
            document.getElementById('appointment-reason').value = appt.reason;
            
            // Re-fetch and select time slots
            await fetchAvailableTimeSlots();
            const selectedTimeRadio = document.querySelector(`input[name="appointment-time"][value="${appt.time}"]`);
            if (selectedTimeRadio) {
                selectedTimeRadio.checked = true;
            }

            addAppointmentForm.dataset.appointmentId = appt.id;
            addAppointmentModal.style.display = 'block';
        } catch (error) {
            alert('Erreur lors de la récupération du rendez-vous pour modification: ' + error.message);
            console.error('Edit appointment error:', error);
        }
    }

    cancelAppointmentBtn.addEventListener('click', async () => {
        const appointmentId = cancelAppointmentBtn.dataset.appointmentId;
        if (appointmentId && confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous ?')) {
            try {
                // Assuming an endpoint to update status or delete
                // For simplicity, let's assume a PUT request to update status to 'Annulé'
                await fetchData(`/gestion/api/appointments/${appointmentId}/`, 'PUT', { status: 'Annulé' });
                alert('Rendez-vous annulé avec succès !');
                viewAppointmentModal.style.display = 'none';
                loadAppointments(document.querySelector('.appointments-content .tabs .tab.active').dataset.tab); // Refresh current tab
                updateDashboardStats();
                renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth()); // Refresh calendar
            } catch (error) {
                alert('Erreur lors de l\'annulation du rendez-vous: ' + error.message);
                console.error('Cancel appointment error:', error);
            }
        }
    });

    async function cancelAppointment(id) {
         if (confirm('Êtes-vous sûr de vouloir annuler ce rendez-vous ?')) {
            try {
                await fetchData(`/gestion/api/appointments/${id}/`, 'PUT', { status: 'Annulé' });
                alert('Rendez-vous annulé avec succès !');
                loadAppointments(document.querySelector('.appointments-content .tabs .tab.active').dataset.tab);
                updateDashboardStats();
                renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth());
            } catch (error) {
                alert('Erreur lors de l\'annulation du rendez-vous: ' + error.message);
                console.error('Cancel appointment error:', error);
            }
        }
    }

    // --- Quick Search on Dashboard ---
    document.getElementById('quick-search-btn').addEventListener('click', async () => {
        const query = document.getElementById('quick-search').value.trim();
        const resultsContainer = document.getElementById('quick-search-results');
        resultsContainer.innerHTML = '';

        if (query.length < 2) {
            resultsContainer.textContent = 'Veuillez entrer au moins 2 caractères pour la recherche.';
            return;
        }

        try {
            // This endpoint would need to be implemented in Django to search across models
            const results = await fetchData(`/gestion/api/appointments/search/?q=${encodeURIComponent(query)}`);

            if (results && results.length > 0) {
                let html = '<h4>Résultats de la recherche:</h4>';
                results.forEach(item => {
                    html += `<div class="search-result-item">`;
                    html += `<strong>Type:</strong> ${item.type} | `;
                    if (item.type === 'patient') {
                        html += `<strong>Nom:</strong> ${item.first_name} ${item.last_name} | `;
                        html += `<strong>Téléphone:</strong> ${item.phone}`;
                        html += ` <button class="btn btn-sm btn-info" onclick="viewPatientDetails(${item.id})">Voir</button>`;
                    } else if (item.type === 'doctor') {
                        html += `<strong>Nom:</strong> ${item.first_name} ${item.last_name} | `;
                        html += `<strong>Spécialité:</strong> ${item.specialty}`;
                        // No specific view for doctor details yet, but could add one
                    } else if (item.type === 'appointment') {
                        html += `<strong>Date:</strong> ${item.date} ${item.time} | `;
                        html += `<strong>Patient:</strong> ${item.patient_name} | `;
                        html += `<strong>Médecin:</strong> ${item.doctor_name} | `;
                        html += `<strong>Motif:</strong> ${item.reason} | `;
                        html += `<strong>Statut:</strong> <span class="status-${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span>`;
                        html += ` <button class="btn btn-sm btn-info" onclick="viewAppointmentDetails(${item.id})">Voir</button>`;
                    }
                    html += `</div>`;
                });
                resultsContainer.innerHTML = html;
            } else {
                resultsContainer.textContent = 'Aucun résultat trouvé pour votre recherche.';
            }
        } catch (error) {
            console.error('Error during quick search:', error);
            resultsContainer.textContent = 'Erreur lors de la recherche rapide.';
        }
    });

    document.getElementById('quick-search').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            document.getElementById('quick-search-btn').click();
        }
    });


    // --- Calendar Logic ---
    function renderCalendar(year, month) {
        const today = new Date();
        const firstDayOfMonth = new Date(year, month, 1);
        const lastDayOfMonth = new Date(year, month + 1, 0);
        const firstDayOfWeek = firstDayOfMonth.getDay(); // 0 for Sunday, 1 for Monday...
        const daysInMonth = lastDayOfMonth.getDate();

        // Adjust firstDayOfWeek for Monday start (if Sunday is 0, make it 7 for consistency)
        const startDayOffset = (firstDayOfWeek === 0) ? 6 : firstDayOfWeek - 1;

        currentMonthSpan.textContent = new Date(year, month).toLocaleString('fr-FR', { month: 'long', year: 'numeric' });

        const tableBody = appointmentCalendar.querySelector('tbody');
        tableBody.innerHTML = '';

        let date = 1;
        for (let i = 0; i < 6; i++) { // Max 6 weeks for a month
            const row = tableBody.insertRow();
            for (let j = 0; j < 7; j++) { // 7 days a week
                const cell = row.insertCell();
                if (i === 0 && j < startDayOffset) {
                    // Empty cells before the first day of the month
                    cell.classList.add('empty');
                } else if (date > daysInMonth) {
                    // Empty cells after the last day of the month
                    cell.classList.add('empty');
                } else {
                    cell.textContent = date;
                    const cellDate = new Date(year, month, date);
                    
                    if (cellDate.toDateString() === today.toDateString()) {
                        cell.classList.add('today');
                    }
                    
                    cell.dataset.date = cellDate.toISOString().split('T')[0]; // Store date in YYYY-MM-DD
                    
                    // Add event listener to show appointments for the day
                    cell.addEventListener('click', () => showAppointmentsForDay(cell.dataset.date));
                    date++;
                }
            }
            if (date > daysInMonth) break; // Stop if all days are rendered
        }
        loadAppointmentsForCalendar(year, month);
    }

    async function loadAppointmentsForCalendar(year, month) {
        try {
            // Fetch all appointments for the current month
            // You'll need a Django API endpoint that can filter by month/year
            const appointments = await fetchData(`/gestion/api/appointments/?year=${year}&month=${month + 1}`); // month is 0-indexed in JS, 1-indexed in Django usually

            appointments.forEach(appt => {
                const apptDate = new Date(appt.date);
                if (apptDate.getFullYear() === year && apptDate.getMonth() === month) {
                    const day = apptDate.getDate();
                    const calendarCells = appointmentCalendar.querySelectorAll('td[data-date]');
                    calendarCells.forEach(cell => {
                        if (parseInt(cell.textContent) === day) {
                            // Create a small indicator for appointments
                            let apptCountSpan = cell.querySelector('.appointment-count');
                            if (!apptCountSpan) {
                                apptCountSpan = document.createElement('span');
                                apptCountSpan.classList.add('appointment-count');
                                cell.appendChild(apptCountSpan);
                            }
                            apptCountSpan.textContent = (parseInt(apptCountSpan.textContent) || 0) + 1;
                            cell.classList.add('has-appointments'); // Style days with appointments
                        }
                    });
                }
            });
        } catch (error) {
            console.error('Error loading appointments for calendar:', error);
        }
    }

    async function showAppointmentsForDay(date) {
        try {
            const appointments = await fetchData(`/gestion/api/appointments/?date=${date}`);
            const apptList = appointments.map(appt => `
                <li>
                    <strong>${appt.time}</strong> - ${appt.patient_first_name} ${appt.patient_last_name} avec Dr. ${appt.doctor_first_name} ${appt.doctor_last_name}
                    <br>Motif: ${appt.reason} - Statut: <span class="status-${appt.status.toLowerCase().replace(' ', '-')}">${appt.status}</span>
                    <button class="btn btn-sm btn-info" onclick="viewAppointmentDetails(${appt.id})" style="margin-left: 10px;">Voir détails</button>
                </li>
            `).join('');

            alert(`Rendez-vous pour le ${date}:\n\n${apptList || 'Aucun rendez-vous.'}`);
        } catch (error) {
            alert('Erreur lors du chargement des rendez-vous pour ce jour: ' + error.message);
            console.error('Error showing appointments for day:', error);
        }
    }

    prevMonthBtn.addEventListener('click', () => {
        currentCalendarDate.setMonth(currentCalendarDate.getMonth() - 1);
        renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth());
    });

    nextMonthBtn.addEventListener('click', () => {
        currentCalendarDate.setMonth(currentCalendarDate.getMonth() + 1);
        renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth());
    });

    // Initial render for calendar when page loads (if applicable)
    // If the calendar page is default, call it here, otherwise it's called on navigation
    // renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth());


    // --- Initial Load (after login) ---
    // If the user is already logged in (e.g., refreshing page with session cookie)
    // You might want to check this with a Django view that confirms authentication.
    // For now, assuming login is always required.
    // However, after a successful login, we need to load initial data:
    // updateDashboardStats();
    // loadPatients();
    // loadDoctors();
    // loadAppointments('today');
    // renderCalendar(currentCalendarDate.getFullYear(), currentCalendarDate.getMonth()); // Initial calendar render

});