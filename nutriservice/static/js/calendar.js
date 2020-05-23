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


function handleClientLoad() {
  $('#spinner').show();
  gapi.load('client:auth2', initClient);
}

function initClient() {
  gapi.client.init({
    apiKey: API_KEY,
    clientId: CLIENT_ID,
    discoveryDocs: DISCOVERY_DOCS,
    scope: SCOPES
  }).then(function () {
    // Listen for sign-in state changes.
    gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);

    // Handle the initial sign-in state.
    initCalendar();
    updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
    authorizeButton.onclick = handleAuthClick;
    signoutButton.onclick = handleSignoutClick;
  }, function(error) {
    appendPre(JSON.stringify(error, null, 2));
  });
}

function updateSigninStatus(isSignedIn) {
  if (isSignedIn) {
    $(authorizeButton).hide();
    $(signoutButton).show();
    //listUpcomingEvents();
    calendar.render();
  } else {
    $(authorizeButton).show();
    $(signoutButton).hide();
  }
}

function handleAuthClick(event) {
  gapi.auth2.getAuthInstance().signIn();
  calendar.src = calendar.src;
}

function handleSignoutClick(event) {
  gapi.auth2.getAuthInstance().signOut();
  calendar.src = '';
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
  }).then(function(response) {
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
        //console.log(event);
      }
    } else {
      appendPre('No upcoming events found.');
    }
  });
}

function execute() {
  return gapi.client.calendar.calendarList.list({})
    .then(function(response) {
      for (var calendar of response.result.items) {
        if (calendar.summary === 'nutricenas') {
          return calendar.id;
        }
      }
      throw 'Calendar not found.';
    })
    .catch(function(error) {
      return gapi.client.calendar.calendars.insert({
        "resource": {
          "summary": "nutricenas"
        }
      }).then(function(response) {
        return response.result.id;
      })
      .catch(function(response) {
        throw 'Failed to create calendar.';
      });
    })
    .then(function(id) {
      console.log(id);
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
  return events.map(function(event) {
    console.log(color.foreground);
    return {
      'title': event.summary,
      'start': event.start.date || event.start.dateTime,
      'end': event.end.date || event.end.dateTime,
      'color': color.background,
    };
  })
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
