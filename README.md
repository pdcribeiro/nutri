# nutri

## TODOs

### Meetings

* Calendar
  * Add event / fill date time by clicking calendar cell
  * Update events start datetime by dragging
  * Update events duration by dragging

* Create meeting
  * Fail on conflict and show conflicting event
  * Possibility to add custom event types

* Edit meeting (reschedule)
  * Only update gcalendar if date or time changed

* Save calendar name instead of ID
  * Fetch ID automatically
* Choose calendars to show
* Format and parse duration without seconds
* Show upcoming meetings in home page
* Add partner permissions to Herokuapp
  * Review other permissions
* ? calendar.js: Use eventSources instead of events
  * Use addEventSource, remove, etc.


### Partners page (Partner model)

* Name
* Partnership start date
* Calendar id


### Plan pages

Meals page
  * ...
  * Intermediate 'dosage distribution per meal' table

Plan page
  * Make 
  * plan.js: Use 'fields', 'cfields' and 'efields' objects
  * Compare performance of two versions of maxProteins/Carbs/Fats calculation
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
  * plan.js: Handle people born on the 29th of Feb for the NIDDK Calculator
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

Measurements page
  * Move height to measurements

Appointment "timeline" / nav element


### Plans list page

* New plan
  * Intermediate page to get client


### Clients list page
* models.Client.Meta.ordering: display and order by last meeting/activity
* Filter clients by user (nutri)
* Filter plans/meetings by clients
* Client.age: calculate and display age in list view
* Use for loop to display table headers in client_form.html


### Misc
* Fix opposite logic on Paper Dashboard sidebar toggler
* Filter db entries appropriately
* Turn function views into classes
* Retry to generalize Meeting/Plan mixins
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
* ? Optimize MealsFormSet.__init__() for loop
* ? Don't store empty meal forms; problem: position filled meal forms appropriately
* ? nutriservice.models.Meeting/Plan.date: set default value in form, not in model
* ? Bottom navbar for forms views


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
      {% comment %} {% if perms.nutriservice.add_client %}
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
                  {% if perms.nutriservice.change_client %} <a class="btn btn-primary" href="{% url 'client-update' client.pk %}">Editar</a>{% endif %}
                  {% if perms.nutriservice.delete_client %} <a class="btn btn-secondary" href="{% url 'client-delete' client.pk %}">Apagar</a>{% endif %}
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
