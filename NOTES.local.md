# nutri

## TODOs

* Integrate calculations in meeting flow
  * Also allow independent calculations

* Change daily energy calculation layout
  * Make goal column same as current
  * Create separate table to input desired daily energy
  * Try split niddk table into two rows
  * ? Move niddk table below other calcs
* Move height to measurements
* Measurement, PrePlan, Plan
  * Allow either meeting or date
  * get_date method

* Handle notifyNegativeMaintCals


### Clients

* models.Client.Meta.ordering: display and order by last meeting/activity
* Filter clients by user (nutri)
* Filter pre plans/meetings by clients
* Use for loop to display table headers in client_form.html


### Meetings

Meeting flow
* Dev process
  * Define models
  * Define urls
  * Define empty/generic views
  * Test flow
  * Improve views
* Flow
  0. Click start button in meeting list item
  1. Start
    * IF previous meeting: notes from previous meeting
  2. Measurements
  3. IF first meeting: calculations page
  4. Meal plan adjustments
    * Slide down option to check calculations
      * Option to edit calculations
  5. Finish
    * Notes for next meeting
    * Generate meal plan deliverable

Calendar
* Add event / fill date time by clicking calendar cell
* Update events start datetime by dragging
* Update events duration by dragging
* Split calendar.js into separate files

Create meeting
* Fail on conflict and show conflicting event
* Possibility to add custom event types

* Choose calendars to show
* Show upcoming meetings in home page
* ? calendar.js: Use eventSources instead of events
  * Use addEventSource, remove, etc.

Misc
* Save phase and if meeting_state == 'ongoing', return to last phase
* Meeting flow breadcrumb
* ? Put calendar in meetings list page

LATER
* If any meeting is ongoing, place button/popup in every page to return to meeting
  * Return to phase where left off


### Measurements

* Add measurments list to client detail page
  * ? Show only latest measurement for each measure
  * Button to view all measurements and create new ones
* Integrate new measurement form in measurement create/update views
* LATER
  * Progress graph EITHER:
    * For selected measure
    * For pre defined measures (eg. weight, body fat)
  * Allow client to add measurements
  * Distinguish client and nutritionist added measurements
  * Progress graph
* ? Get data from GET request in MeasurementCreate


### PrePlans

* Fetch data instead of reloading page in PrePlanCreate

PrePlan page
  * Make 
  * preplan.js: Use 'fields', 'cfields' and 'efields' objects
  * Compare performance of two versions of maxProtein/Carbs/Fats calculation
  * Fix select elements width
  * Review table column widths
  * Try to use Bootstrap help text for Field extra
    * https://getbootstrap.com/docs/4.0/components/forms/#help-text
  * Try to use Bootstrap form-control-plaintext input for Field value
    * https://getbootstrap.com/docs/4.0/components/forms/#readonly-plain-text
  * Range inputs
    * Allow text input
    * Find better way to center horizontally
    * Review and improve template code
  * Food dosages distribution table
    * Establish min/max errors? Account for average value, spread?
    * Peso/volume por dose igual para todos? Fazer média?
    * ? Rename fruit to fruits
  * Test dosages calculator

  * Tab and arrows navigation
  * Use Vue / React to minimize rendering?
  * Use Babel to transpile JS to older versions
  * preplan.js: Handle people born on the 29th of Feb for the NIDDK Calculator
  * BMI fields description
  * Detect calculator dialogs on errors
    * ? appController $scope.goalChange(): $scope.unachievableGoal
  * ? Simplify NIDDK calculator code
    * Learn angular
  * ? efields: Ignore non number characters when type === 'number'
  * ? Duration as range input
  * ? field.html: Make 'extra' variable boolean
  * ? Use goalPAL in NIDDK calc instead
  * ? Fibra
  * ? Recommendations
    * ? NIDDK healthy weight and body fat range
      * $scope.weightRangeLow
      * $scope.weightRangeHigh


### MealPlans

Meals page
  * ...
  * Intermediate 'dosage distribution per meal' table


### Google API

* Load gapi only once? Store stuff in sessionData?
* Split calendar.js script into multiple files
  * Node.js required?


### Misc

* Put view classes into scopes
  * Create python package for views?
* Check for errors when fetching data from server
  * PrePlanCreate page
  * MeetingCreate page
* Change any 'get_object_or_404' calls with 'self.object'
* More tests
* Handle brute force attacks
* Handle DDoS attacks
* Fix opposite logic on Paper Dashboard sidebar toggler
* Filter db entries appropriately
* Turn function views into classes
* Retry to generalize Meeting/PrePlan mixins
* Set card max height and scroll vertically
* Send email to NIDDK guy
* BootstrapMixin to add form-control class, etc. to input elements
* ! Duplicate plan
* New meeting/plan: show client field when creating and coming from meeting/plan list pages
* Generalize tables
* Regex to parse ints from urls
* White/dark switch
* Review permissions for everything (e.g. individual plans, etc.)
* Don't add "?next=" when current page is login page
* Dynamic meal formset. Variable number of fields.
* Default partner
* Search input
  * When selecting clients
  * In homepage, to jump to client page

LATER
* Put 'today' or 'now' row in or mark today items in list views.
* ? Optimize MealsFormSet.__init__() for loop
* ? Don't store empty meal forms; problem: position filled meal forms appropriately
* ? core.models.Meeting/PrePlan.date: set default value in form, not in model


### Client version
* Filter plans/meetings by user (client)



## Data

### IMC 2-20 years old

Healthy is 5-85 percentile

5 pontos

Boys 85th percentile
y = 21.51323 - 2.275467*x + 0.3407884*x^2 - 0.0162381*x^3 + 0.0002786596*x^4

Boys 5th percentile
y = 15.67596 - 0.5499096*x + 0.02681244*x^2 + 0.002254393*x^3 - 0.00008898679*x^4


### NIDDK calculator PAL -> percentage conversion

(0.9 * BMR * PAL - BMR) / weight * (1.0 + change / 100.0)
activityParam = BMR * (0.9 * PAL - 1) / weight * (1.0 + change / 100.0)
change = (activityParam / BMR / (0.9 * PAL - 1) * weight - 1) * 100
PAL = (activityParam / BMR * weight / (1.0 + change / 100.0) + 1) / 0.9
change = ((0.9 * newPAL - 1) / (0.9 * PAL - 1) - 1) * 100


### Clients page

  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Clientes</h4>
    </div>
    <div class="card-body">
      {% comment %} {% if perms.core.add_client %}
        <a class="btn btn-primary" href="{% url 'client-create' %}">Novo cliente</a>
      {% endif %} {% endcomment %}
      {% if client_list %}
        <ul class="list-unstyled team-members">
          {% for client in client_list %}
            <li>
              <div class="row">
                <div class="col-md-8 col-8">
                  <a href="{{ client.get_absolute_url }}">{{ client.name }}</a>
                </div>
                <div class="col-md-4 col-4 text-right">
                  {% comment %} <btn class="btn btn-sm btn-outline-success btn-round btn-icon"><i class="fa fa-envelope"></i></btn> {% endcomment %}
                  {% if perms.core.change_client %} <a class="btn btn-primary" href="{% url 'client-update' client.pk %}">Editar</a>{% endif %}
                  {% if perms.core.delete_client %} <a class="btn btn-secondary" href="{% url 'client-delete' client.pk %}">Apagar</a>{% endif %}
                </div>
              </div>
            </li>
          {% endfor %}
        </ul>
      {% else %}
        <p>Não tem clientes.</p>
      {% endif %}  
    </div>
  </div>