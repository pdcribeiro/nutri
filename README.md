# nutri

## TODOs

* debug and test as nutritionist

* models.Plan: review usage for meeting and date fields
* models.Client.Meta.ordering: order by last meeting/activity
* Client.last_meeting: calculate and display last meeting in list view
* Filter clients by user (nutri)
* Filter plans/meetings by clients
* Client.age: calculate and display age in list view
* Use for loop to display table headers in client_form.html
* meals_formset: disregard has_changed() only on object creation

* Filter plans/meetings by user (client)
* Don't add "?next=" when current page is login page
* ? Optimize MealsFormSet.__init__() for loop
* ? Don't store empty meal forms; problem: position filled meal forms appropriately
* ? nutriservice.models.Meeting/Plan.date: set default value in form, not in model
