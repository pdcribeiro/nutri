# nutri

## TODOs

* Enviar email!!!


### Planning

1. Plan page
  * Food dosages distribution table <----- WIP
    * Set minimum limit values or redo table
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

2. Meal page

3. Measurements page
  * Move height to measurements

4. Appointment "timeline" / nav element


### Clients list page
* models.Client.Meta.ordering: display and order by last meeting/activity
* Filter clients by user (nutri)
* Filter plans/meetings by clients
* Client.age: calculate and display age in list view
* Use for loop to display table headers in client_form.html


### Misc
* Review permissions for everything (e.g. individual plans, etc.)
* Don't add "?next=" when current page is login page
* Dynamic meal formset. Variable number of fields.
* ? Optimize MealsFormSet.__init__() for loop
* ? Don't store empty meal forms; problem: position filled meal forms appropriately
* ? nutriservice.models.Meeting/Plan.date: set default value in form, not in model


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
