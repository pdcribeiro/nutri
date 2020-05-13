const { gender, age, height, weight, body_fat, pal, pal_map } = js_context;
// console.log(typeof height);
let tmp = null;

function properRound(value, places) {
  const multiplier = 10 ** places;
  return Math.round(value * multiplier) / multiplier;
}

function render() {
  const goal_weight = parseFloat($('#goal_weight_efield input').val());
  const goal_body_fat = parseFloat($('#goal_body_fat_efield input').val());
  const new_pal = $('#new_pal_efield select').val();
  
  const goal_time = parseFloat($('#goal_time_efield input').val());
  const pal_change = parseFloat($('#pal_change_efield input').val());

  // Update efield fields text
  $('#goal_weight').text(goal_weight);  //TODO general assigment for all elements
  $('#goal_body_fat').text(goal_body_fat);
  $('#new_pal').text(pal_map[new_pal]);

  $('#goal_time').text(goal_time);
  $('#pal_change').text(pal_change);

  // Update computed fields
  $('#goal_weight_extra').text(goal_weight - weight + ' kg');
  $('#goal_body_fat_extra').text(goal_body_fat - body_fat + ' %');
  $('#new_pal_extra').text('PAL ' + new_pal);
  
  $('#goal_bmi').text(properRound(goal_weight / (height / 100) ** 2, 1));

  // Update NIDDK calculator results
  function niddk() {
    $('#energy_to_goal, #energy_to_maintain').text('...');
    const calc = document.getElementById('calc');
    while (calc.contentDocument.readyState !== 'complete') {
      setTimeout(niddk, 500);
      return;
    }
    const calcBody = calc.contentDocument.body;
    const scope = calc.contentWindow.angular.element(calcBody).scope();
    const result = scope.getEnergy({
      ...js_context,
      goalWeight: goal_weight,
      goalTime: goal_time,
      palChange: pal_change,
    });
    $('#energy_to_goal').text(result.energyGoal);
    $('#energy_to_maintain').text(result.energyMaintain);
  }
  niddk();
}

function init() {
  // Hide efields controls
  $('.efield-controls').hide();
  
  // Set computed fields values
  $('#pal_extra').text('PAL ' + pal);
  $('#bmi').text(properRound(weight / (height / 100) ** 2, 1));
  
  render();

  // Bind event handlers.
  $('.efield .field-value').click(function edit() {
    tmp = $(this).parent().hide()
        .siblings('.efield-controls').show()
          .children('input, select').focus().val();
  });

  $('.efield input').focus(function(event) {
    event.target.select();
  });

  function save(self, value) {
    $(self).parent().hide()
      .siblings('.field').show();
    render();
  }

  function cancel(self) {
    $(self).val(tmp).parent().hide()
      .siblings('.field').show();
  }

  $('.efield-save').click(function(event) {
    event.preventDefault();
    save(this, $(this).siblings('input').val());
  });
  
  $('.efield-cancel').click(function(event) {
    event.preventDefault();
    cancel(this);
  });

  $('.efield input, .efield select').blur(function() {
    if (!event.relatedTarget || !event.relatedTarget.classList.contains('efield-save')) {
      cancel(this);
    }
  }).keydown(function(event) {
    if (event.key === 'Enter') save(this, $(this).val());
    else if (event.key === 'Escape') cancel(this);
  });
}

init();


// function edit(event) {
//   event.target.classList.add('d-none');
//   event.target.parentElement.classList.add('d-flex');
//   event.target.parentElement.classList.remove('d-none');
// }

// var app = new Vue({
//   delimiters: ['[[', ']]'],
//   el: '#app',
//   data: {
//     ...js_context,
//     goal_weight: js_context.weight,
//     bmi: 0, goal_bmi: 0,
//   },
//   mounted: function() {
//     this.render();
//     document.querySelectorAll('.efield-wrapper .field').forEach(element => {
//       element.addEventListener('click', edit());
//       console.log('in');
//     });
//   },
//   methods: {
//     render: function() {
//       this.bmi = this.weight / (this.height / 100) ** 2;
//     }
//   }
// });
