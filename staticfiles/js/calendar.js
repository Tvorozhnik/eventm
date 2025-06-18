document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    if (calendarEl) {
        // Инициализация событий календаря
        var events = window.eventsDates || [];
        console.log('Initializing calendar with events:', events);
        
        // Проверка формата событий
        events = events.map(function(event) {
            if (typeof event === 'string') {
                return {
                    start: event,
                    display: 'background'
                };
            }
            return event;
        });

        var calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            initialDate: window.selectedDate || undefined,
            locale: 'ru',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth'
            },
            events: events,
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
            eventColor: '#4F46E5',
            eventBackgroundColor: '#4F46E5',
            eventBorderColor: '#4F46E5',
            eventTextColor: '#ffffff',
            eventDidMount: function(info) {
                console.log('Event mounted:', info.event);
            }
        });
        
        calendar.render();
        console.log('Calendar rendered');
    }

    // Добавляем обработчик для сброса фильтров
    var resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            window.location.href = '{% url "apps.events:events_list" %}'; // Просто перезагружаем страницу без параметров
        });
    }
}); 