// Doctor Availability Handling
document.querySelectorAll('#doctor-availability input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const dayContainer = this.parentElement;
        const timeInputs = dayContainer.querySelectorAll('input[type="time"]');
        timeInputs.forEach(input => {
            input.disabled = !this.checked;
            if (!this.checked) {
                input.value = '';
            }
        });
    });
});

// Appointment Date Handling
document.getElementById('appointment-date').addEventListener('change', async function() {
    const doctorId = document.getElementById('appointment-doctor').value;
    const date = this.value;
    
    if (doctorId && date) {
        const response = await fetch(`/get-slots/?doctor_id=${doctorId}&date=${date}`);
        const data = await response.json();
        renderTimeSlots(data.slots);
    }
});

// Time Slot Rendering
function renderTimeSlots(slots) {
    const container = document.getElementById('time-slots');
    container.innerHTML = '';
    
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

// Calendar Navigation
document.getElementById('prev-month').addEventListener('click', () => {
    // Implement calendar navigation
});

document.getElementById('next-month').addEventListener('click', () => {
    // Implement calendar navigation
});

// Logout
document.getElementById('logout-btn').addEventListener('click', () => {
    fetch('/logout/')
        .then(() => {
            document.getElementById('app-container').style.display = 'none';
            document.getElementById('login-page').style.display = 'block';
        });
});