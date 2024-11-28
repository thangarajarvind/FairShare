// Global object to store user totals
let userTotals = {};

window.onload = (event) => {
    initMultiselect();
};

function initMultiselect() {
    // Initialize all dropdowns
    document.querySelectorAll('.multiselect').forEach(dropdown => {
        checkboxStatusChange(dropdown.querySelector('input[type=checkbox]'));
    });

    // Handle clicks outside dropdowns
    document.addEventListener("click", function(evt) {
        const clickedElement = evt.target;
        const multiselects = document.querySelectorAll('.multiselect');
        
        let clickedInsideDropdown = false;
        multiselects.forEach(multiselect => {
            if (multiselect.contains(clickedElement)) {
                clickedInsideDropdown = true;
            }
        });

        if (!clickedInsideDropdown) {
            document.querySelectorAll('.selectOptions').forEach(opt => {
                opt.style.display = 'none';
            });
        }
    });
}

function updateUserSummary() {
    const summaryContent = document.getElementById('userSummaryContent');
    summaryContent.innerHTML = '';
    
    let grandTotal = 0;
    
    Object.entries(userTotals).forEach(([user, total]) => {
        if (total > 0) {
            const userRow = document.createElement('div');
            userRow.className = 'user-row';
            userRow.innerHTML = `
                <span>${user}:</span>
                <span>$${total.toFixed(2)}</span>
            `;
            summaryContent.appendChild(userRow);
            grandTotal += total;
        }
    });
    
    document.getElementById('grandTotal').textContent = `$${grandTotal.toFixed(2)}`;
}

function checkboxStatusChange(checkbox) {
    const multiselect = checkbox.closest('.multiselect');
    const selectBox = multiselect.querySelector('.selectBox select option');
    const checkboxes = multiselect.querySelectorAll('input[type=checkbox]:checked');
    const row = checkbox.closest('tr');
    
    const values = Array.from(checkboxes).map(cb => cb.value);
    selectBox.innerText = values.length > 0 ? values.join(', ') : 'Select User';
    
    // Get the total price for this item (already includes quantity)
    const totalPrice = parseFloat(row.querySelector('td:nth-child(4)').textContent.substring(1));
    const pricePerUser = checkboxes.length > 0 ? totalPrice / checkboxes.length : 0;
    
    // Update price per user in the row
    row.querySelector('.price-per-user').textContent = `$${pricePerUser.toFixed(2)}`;
    
    // Initialize or reset user totals
    values.forEach(user => {
        if (!userTotals[user]) {
            userTotals[user] = 0;
        }
    });
    
    // Recalculate all user totals
    userTotals = {};
    document.querySelectorAll('tr').forEach(tableRow => {
        const rowCheckboxes = tableRow.querySelectorAll('input[type=checkbox]:checked');
        if (rowCheckboxes.length > 0) {
            const rowTotal = parseFloat(tableRow.querySelector('td:nth-child(4)').textContent.substring(1));
            const rowPricePerUser = rowTotal / rowCheckboxes.length;
            
            rowCheckboxes.forEach(cb => {
                if (!userTotals[cb.value]) {
                    userTotals[cb.value] = 0;
                }
                userTotals[cb.value] += rowPricePerUser;
            });
        }
    });
    
    updateUserSummary();
}

function toggleCheckboxArea(selectBox) {
    const options = selectBox.closest('.multiselect').querySelector('.selectOptions');
    const isVisible = options.style.display === 'block';
    
    document.querySelectorAll('.selectOptions').forEach(opt => {
        opt.style.display = 'none';
    });
    
    options.style.display = isVisible ? 'none' : 'block';
}