// Client ID and API key from the Developer Console
var CLIENT_ID = '177217773425-ktoaf0un3hgni6ud1sf3ih4cb2agd1e9.apps.googleusercontent.com';
var API_KEY = 'AIzaSyD9HgSmymaLu43wOmr6ImG-il2tUnMFpf0';

// Array of API discovery doc URLs for APIs used by the quickstart
var DISCOVERY_DOCS = ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"];

// Authorization scopes required by the API; multiple scopes can be
// included, separated by spaces.
var SCOPES = "https://www.googleapis.com/auth/calendar";

var authorizeButton = document.getElementById('authorize_button');
var signoutButton = document.getElementById('signout_button');
var calendarEl = document.getElementById('calendar');

var calendar = null;


function handleClientLoad(renderCalendar=true) {
  $('#spinner').show();
  gapi.load('client:auth2', () => {
    gapi.client.init({
      apiKey: API_KEY,
      clientId: CLIENT_ID,
      discoveryDocs: DISCOVERY_DOCS,
      scope: SCOPES
    })
      .then(() => {
        if (renderCalendar) {
          initCalendar();
        }
        else {
          $('#spinner').hide();
        }
  
        // Listen for sign-in state changes.
        gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);
  
        // Handle the initial sign-in state.
        updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
        authorizeButton.onclick = handleAuthClick;
        signoutButton.onclick = handleSignoutClick;
      }, function (error) {
        appendPre(JSON.stringify(error, null, 2));
      });
  });
}

function updateSigninStatus(isSignedIn) {
  if (isSignedIn) {
    $(authorizeButton).hide();
    $(signoutButton).show();
    //listUpcomingEvents();
    if (calendar) calendar.render();
  } else {
    $(authorizeButton).show();
    $(signoutButton).hide();
  }
}

function handleAuthClick(event) {
  gapi.auth2.getAuthInstance().signIn();
}

function handleSignoutClick(event) {
  gapi.auth2.getAuthInstance().signOut();
}

function appendPre(message) {
  var pre = document.getElementById('content');
  var textContent = document.createTextNode(message + '\n');
  pre.appendChild(textContent);
}

function listUpcomingEvents() {
  gapi.client.calendar.events.list({
    'calendarId': 'primary',
    'timeMin': (new Date()).toISOString(),
    'showDeleted': false,
    'singleEvents': true,
    'maxResults': 10,
    'orderBy': 'startTime'
  }).then(function (response) {
    var events = response.result.items;
    appendPre('Upcoming events:');

    if (events.length > 0) {
      for (i = 0; i < events.length; i++) {
        var event = events[i];
        var when = event.start.dateTime;
        if (!when) {
          when = event.start.date;
        }
        appendPre(event.summary + ' (' + when + ')')
      }
    } else {
      appendPre('No upcoming events found.');
    }
  });
}

function execute() {
  return gapi.client.calendar.calendarList.list({})
    .then(function (response) {
      for (var calendar of response.result.items) {
        if (calendar.summary === 'nutricenas') {
          return calendar.id;
        }
      }
      throw 'Calendar not found.';
    })
    .catch(function (error) {
      return gapi.client.calendar.calendars.insert({
        "resource": {
          "summary": "nutricenas"
        }
      }).then(function (response) {
        return response.result.id;
      })
        .catch(function (response) {
          throw 'Failed to create calendar.';
        });
    })
    .then(function (id) {
      //calendar.src = 'https://calendar.google.com/calendar/embed?height=600&amp;wkst=1&amp;bgcolor=%23f4f3ef&amp;ctz=Europe%2FLisbon&amp;src=' + encodeURIComponent(id) + '&amp;showTitle=0&amp;showNav=1&amp;showDate=1&amp;showTabs=1&amp;showPrint=0&amp;showCalendars=1&amp;mode=WEEK&amp;hl=pt_PT';
      //calendar.src = 'https://calendar.google.com/calendar/embed?height=600&amp;wkst=1&amp;bgcolor=%23f4f3ef&amp;ctz=Europe%2FLisbon&amp;src=' + encodeURIComponent(id) + '&amp;showTitle=0&amp;showNav=1&amp;showPrint=0&amp;showTabs=1&amp;showTz=0&amp;mode=WEEK&amp;hl=pt_PT';
    });
}


function initCalendar() {
  calendar = new FullCalendar.Calendar(calendarEl, {
    plugins: ['interaction', 'dayGrid', 'timeGrid', 'googleCalendar'],
    defaultView: 'timeGridWeek',
    // height: 500,
    eventTextColor: 'white',
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay'
    },
    minTime: '08:00:00',
    events: fetchEvents,
  });
}

function fetchEvents(fetchInfo, successCallback, failureCallback) {
  $('#spinner').show();
  Promise.all([fetchCalendarList(), fetchCalendarColors()])
    .then(([calendars, colors]) =>
      fetchEventsFromCalendars(fetchInfo, calendars, colors))
    .then(events => {
      // console.log('Fetched', events.length, 'events.');  //DEV
      // console.log(events);  //DEV
      successCallback(events);
    })
    .catch(error => {
      console.error("Error in 'initCalendar'.", error);
      alert('Erro ao obter calendários Google. Verifique a sua ligação à internet.');
      failureCallback(error);
    })
    .then(() => {
      $('#spinner').hide();
    });
}

function fetchCalendarList() {
  return gapi.client.calendar.calendarList.list({})
    .then(response => response.result.items);
}

function fetchCalendarColors() {
  return gapi.client.calendar.colors.get({})
    .then(response => response.result.calendar);
}

function fetchEventsFromCalendars(fetchInfo, calendars, colors) {
  return calendars.reduce((prevPromise, calendar) => {
    var color = colors[calendar.colorId];
    return Promise.all([
      prevPromise,
      fetchEventsFromCalendar(fetchInfo, calendar, color)
    ])
      .then(([prevEvents, events]) => prevEvents.concat(events))
  }, Promise.resolve([]));
}

function fetchEventsFromCalendar(fetchInfo, calendar, color) {
  return gapi.client.calendar.events.list({
    'calendarId': calendar.id,
    'timeMin': fetchInfo.startStr,
    'timeMax': fetchInfo.endStr,
  })
    .then(response => parseEvents(response.result.items, color))
    .catch(error => {
      console.error("Error fetching '", calendar.summary, "'events.", error);
    });
}

function parseEvents(events, color) {
  // console.log(events);
  return events.map(function (event) {
    return {
      'title': event.summary,
      'start': event.start.date || event.start.dateTime,
      'end': event.end.date || event.end.dateTime,
      'color': color.background,
    };
  })
}


// Update summary when client changes
var client = null;
$('#id_client').focus(function() {
  if ($('#id_client').val()) {
    client = getClientName();
  }
}).change(function() {
  if ($('#id_client').val()) {
    if ($('#id_summary').val()) {
      var regex = new RegExp(`(.*)${client}(.*)`, 'i');
      if (regex.test($('#id_summary').val())) {
        var newClient = getClientName();
        var newSummary = $('#id_summary').val().replace(regex, `$1${newClient}$2`);
        $('#id_summary').val(newSummary);
        client = newClient;
      }
    }
    else {
      var newClient = getClientName();
      $('#id_summary').val('Consulta ' + newClient);
      client = newClient;
    }
  }
});

function getClientName() {
  var client_id = $('#id_client').val();
  return $(`#id_client option[value="${client_id}"]`).text();
}


// Fetch gcal calendar ID
function fetchCalendar() {
  if ($('#id_client').val()) {
    var url = '/main/calendar/' + $('#id_client').val();
    fetch(url).then(response => response.text()).then(function (calId) {
      calendarId = calId;
    });
  }
}
if (typeof calendarId === 'undefined') {
  var calendarId = null;
  fetchCalendar();
}
$('#id_client').change(fetchCalendar);


// Gcal integration on form submission
var path = window.location.pathname;
$('form').submit(function (event, gcalSync = false) {
  if (path.indexOf('/meeting/create/') > -1 && !gcalSync) {
    event.preventDefault();
    createMeeting();
  }
  else if (/\/meeting\/\d+\/update\//.test(path) && !gcalSync) {
    event.preventDefault();
    updateMeeting();
  }
  else if (/\/meeting\/\d+\/delete\//.test(path) && !gcalSync) {
    event.preventDefault();
    deleteMeeting();
  }
});

// Create meeting on gcal
function createMeeting() {
  return gapi.client.calendar.events.insert({
    calendarId,
    resource: getEventResource(),
  })
    .then(response => {
      $('#id_event').val(response.result.id);
      $('form').trigger('submit', true);
    })
    .catch(error => {
      console.error('Error creating meeting.', error);
      alert('Erro ao criar evento Google. Verifique a sua ligação à internet.');
    });
}

function getEventResource() {
  var [startDateTime, endDateTime] = parseDateTime();
  return {
    'summary': $('#id_summary').val(),
    'start': {
      'dateTime': startDateTime,
    },
    'end': {
      'dateTime': endDateTime,
    },
  }
}

function parseDateTime() {
  var date = $('#id_date').val();
  var time = $('#id_time').val();
  var duration = $('#id_duration').val();

  // Parse date.
  var now = new Date();
  var [_, day, _, month, _, year] = date.match(/(\d+)(\D(\d+)(\D(\d+))?)?/)
  if (day.length === 1) day = '0' + day;
  if (typeof month === 'undefined') var month = (now.getMonth() + 1).toString();
  if (month.length === 1) month = '0' + month;
  if (typeof year === 'undefined') var year = (now.getYear() + 1900).toString();
  else if (year.length === 2) year = '20' + year;
  date = `${year}-${month}-${day}`;
  $('#id_date').val(`${day}-${month}-${year}`)

  // Parse time.
  var [_, hours, _, minutes] = time.match(/(\d+)(\D(\d+))?/)
  if (hours.length === 1) hours = '0' + hours;
  if (typeof minutes === 'undefined') var minutes = '00';
  else if (minutes.length === 1) minutes = '0' + minutes;
  time = hours + ':' + minutes;
  $('#id_time').val(time);

  // Compute UTC date time strings.
  var startDateObj = new Date(date + 'T' + time);
  var durationInMs = duration * 60 * 1000;
  var endDateObj = new Date(startDateObj.getTime() + durationInMs);

  return [
    startDateObj.toISOString(),
    endDateObj.toISOString()
  ];
}

// Update meeting on gcal
function updateMeeting() {
  return gapi.client.calendar.events.update({
    calendarId,
    'eventId': $('#id_event').val(),
    'resource': getEventResource(),
  })
    .then(response => {
      $('form').trigger('submit', true);
    })
    .catch(error => {
      console.error('Error creating meeting.', error);
      alert('Erro ao criar evento Google. Verifique a sua ligação à internet.');
    });
}

// Delete meeting on gcal
function deleteMeeting() {
  return gapi.client.calendar.events.delete({
    calendarId,
    eventId,
  })
    .then(response => {
      $('form').trigger('submit', true);
    })
    .catch(response => {
      if (response.result.error.code === 410) {
        alert('O evento Google já tinha sido apagado. A consulta foi apagada da base de dados.');
        $('form').trigger('submit', true);
      }
      else {
        console.error('Error deleting meeting.', error);
        alert('Erro ao apagar evento Google. Verifique a sua ligação à internet.');
      }
    });
}


    // events: [
    //   {
    //     title: 'All Day Event',
    //     start: '2020-05-01'
    //   },
    //   {
    //     title: 'Long Event',
    //     start: '2020-05-07',
    //     end: '2020-05-10'
    //   },
    //   {
    //     groupId: '999',
    //     title: 'Repeating Event',
    //     start: '2020-05-09T16:00:00'
    //   },
    //   {
    //     groupId: '999',
    //     title: 'Repeating Event',
    //     start: '2020-05-16T16:00:00'
    //   },
    //   {
    //     title: 'Conference',
    //     start: '2020-05-11',
    //     end: '2020-05-13'
    //   },
    //   {
    //     title: 'Meeting',
    //     start: '2020-05-12T10:30:00',
    //     end: '2020-05-12T12:30:00'
    //   },
    //   {
    //     title: 'Lunch',
    //     start: '2020-05-12T12:00:00'
    //   },
    //   {
    //     title: 'Meeting',
    //     start: '2020-05-12T14:30:00'
    //   },
    //   {
    //     title: 'Birthday Party',
    //     start: '2020-05-13T07:00:00'
    //   },
    //   {
    //     title: 'Click for Google',
    //     url: 'http://google.com/',
    //     start: '2020-05-28',
    //   }
    // ]
