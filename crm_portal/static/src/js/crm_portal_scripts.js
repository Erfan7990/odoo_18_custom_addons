odoo.define('crm_portal.crm_portal_scripts', function (require) {
    "use strict";

    document.addEventListener('DOMContentLoaded', function () {
        const btnOpenForm = document.querySelector('#btnOpenForm');
        const popupForm = document.createElement('div');
        popupForm.id = 'popupForm';
        popupForm.classList.add('popup-form', 'hidden');

        // Add form HTML to the popupForm element
        popupForm.innerHTML = `
            <div class="popup-content">
                <span id="closePopup" class="close">&times;</span>
                <h3>Create New CRM Entry</h3>
                <form id="newCRMForm">
                    <div class="form-group">
                        <label for="customerName">Customer Name:</label>
                        <input type="text" id="customerName" name="customerName" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="priority">Priority:</label>
                        <select id="priority" name="priority" class="form-control" required>
                            <option value="normal">Normal</option>
                            <option value="low">Low</option>
                            <option value="high">High</option>
                            <option value="very_high">Very High</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-success">Submit</button>
                </form>
            </div>
        `;

        // Append the popupForm to the body
        document.body.appendChild(popupForm);

        const closePopup = popupForm.querySelector('#closePopup');

        // Show popup
        btnOpenForm.addEventListener('click', function () {
            popupForm.classList.remove('hidden');
        });

        // Hide popup
        closePopup.addEventListener('click', function () {
            popupForm.classList.add('hidden');
        });

        // Form submission logic
        popupForm.querySelector('#newCRMForm').addEventListener('submit', function (e) {
            e.preventDefault();
            const customerName = document.querySelector('#customerName').value;
            const priority = document.querySelector('#priority').value;

            console.log('Customer Name:', customerName);
            console.log('Priority:', priority);

            // Implement RPC call to Odoo backend here
            popupForm.classList.add('hidden');
        });
    });
});
