// Confirm delete actions
document.addEventListener('DOMContentLoaded', function() {
    // Generic confirm delete function
    function confirmDelete(event) {
        if (!confirm('Are you sure you want to delete this item?')) {
            event.preventDefault();
            return false;
        }
        return true;
    }

    // Add confirm to all delete buttons
    document.querySelectorAll('.btn-danger[type="submit"]').forEach(button => {
        button.addEventListener('click', confirmDelete);
    });

    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
}); 