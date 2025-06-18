document.addEventListener('DOMContentLoaded', function() {
    // Инициализация календаря
    const calendar = flatpickr('#calendar-inline', {
        inline: true,
        dateFormat: "Y-m-d",
        onChange: function(selectedDates, dateStr) {
            document.getElementById('selected-date').value = dateStr;
        }
    });

    // Обработка сброса фильтров
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            const inputs = form.querySelectorAll('input[type="checkbox"], input[type="radio"]');
            inputs.forEach(input => input.checked = false);
            form.submit();
        });
    }
}); 