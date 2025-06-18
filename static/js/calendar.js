document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            initialDate: window.selectedDate || undefined,
            locale: 'ru',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth'
            },
            events: window.eventsDates || [],
            dateClick: function(info) {
                document.getElementById('selected-date').value = info.dateStr;
                
                var prevSelected = calendarEl.querySelector('.fc-day-selected');
                if (prevSelected) {
                    prevSelected.classList.remove('fc-day-selected');
                }
                var clickedCell = info.dayEl;
                clickedCell.classList.add('fc-day-selected');
            },
            dayMaxEvents: true,
            height: 'auto',
            dayMaxEventRows: 2,
            displayEventTime: false,
            eventDisplay: 'background',
            selectable: true,
            selectMirror: true,
            dayMaxEvents: true,
            eventColor: '#4F46E5',
            eventBackgroundColor: '#4F46E5',
            eventBorderColor: '#4F46E5',
            eventTextColor: '#ffffff'
        });
        calendar.render();
    }
}); 