document.addEventListener('DOMContentLoaded', function() {
    // Инициализация календаря
    const calendar = flatpickr('#calendar-inline', {
        locale: 'ru',
        dateFormat: 'Y-m-d',
        defaultDate: "{{ selected_date|default:'' }}",
        inline: true,
        onChange: function(selectedDates, dateStr) {
            document.getElementById('selected-date').value = dateStr;
        }
    });

    // Обработка кнопки сброса
    document.getElementById('reset-filters').addEventListener('click', function() {
        // Сброс календаря
        calendar.clear();
        document.getElementById('selected-date').value = '';
        
        // Сброс категорий
        document.querySelectorAll('input[name="category"]').forEach(checkbox => {
            checkbox.checked = false;
        });
        
        // Сброс актуальности
        document.getElementById('relevance').value = 'all';
        
        // Отправка формы
        document.getElementById('filter-form').submit();
    });
}); 