# nutri

## TODOs

* Plan page
  * ...
  * \+ or - in extras
  * Fix niddk calc on first time

* Move calc iframe to after plan.js execution? Probably not
* Try to not load niddk calc html

* Fix select elements width
* ? Edit weight in plan page
  * Create custom form taking fields from both models (Client and Plan)
* ? Move plan model to plan app
* ? field.html: Make 'extra' variable boolean

* After creating plan, use "next" to redirect either to 'client-detail' or 'plans'
* Use Babel to transpile JS to older versions
* plan.js: Handle people born on the 29th of Feb for the NIDDK Calculator


* Old

  * Static macronutrient calculator using React
  * Static meal creator using React

  * Create/update/delete plans. Override as_view()?

  * Dynamic meal formset. Variable number of fields.
  * debug and test as nutritionist
  * models.Plan: review usage for meeting and date fields
  * models.Client.Meta.ordering: order by last meeting/activity
  * Client.last_meeting: calculate and display last meeting in list view
  * Filter clients by user (nutri)
  * Filter plans/meetings by clients
  * Client.age: calculate and display age in list view
  * Use for loop to display table headers in client_form.html

  * Review access to everything (e.g. individual plans, etc.)
  * Filter plans/meetings by user (client)
  * Don't add "?next=" when current page is login page
  * ? Optimize MealsFormSet.__init__() for loop
  * ? Don't store empty meal forms; problem: position filled meal forms appropriately
  * ? nutriservice.models.Meeting/Plan.date: set default value in form, not in model
