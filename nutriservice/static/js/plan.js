const { gender, age, height, weight, body_fat: bodyFat, pal, pal_map: palMap } = jsContext;
const calc = document.getElementById('calc');
const BMR_CONSTANT = 6.25*height - 5*age + { m: 5, f: -161 }[gender];
const MACRONUTRIENTS_ARR = ['proteins', 'carbs', 'fats', 'proteins', 'carbs'];

let tmp = null;

function properRound(value, places) {
  const multiplier = 10 ** places;
  return Math.round(value * multiplier) / multiplier;
}

function getSignal(value) {
  return (value >= 0 ? '+ ' : '- ') + Math.abs(value);
}

function render() {  //TODO try without parseFloat
  const goalWeight = parseFloat($('#goal_weight_efield input').val());
  const goalBodyFat = parseFloat($('#goal_body_fat_efield input').val());
  const newPal = $('#new_pal_efield select').val();
  
  const goalTime = parseFloat($('#goal_time_efield input').val());
  const palChange = parseFloat($('#pal_change_efield input').val());
  const goalDailyEnergy = parseFloat($('#goal_daily_energy_efield input').val());

  const proteins = parseFloat($('#proteins_efield input').val()) / 100;
  const carbs = parseFloat($('#carbs_efield input').val()) / 100;
  const fats = parseFloat($('#fats_efield input').val()) / 100;

  // Update efield fields text  //TODO? run this on init and save
  $('#goal_weight').text(goalWeight);  //TODO? general assigment for all elements
  $('#goal_body_fat').text(goalBodyFat);
  $('#new_pal').text(palMap[newPal]);

  $('#goal_time').text(goalTime);
  $('#pal_change').text(palChange);

  $('#goal_daily_energy').text(goalDailyEnergy);
  
  // Update computed fields
  $('#goal_weight_extra').text(getSignal(goalWeight - weight) + ' kg');
  $('#goal_body_fat_extra').text(getSignal(goalBodyFat - bodyFat) + ' %');
  $('#new_pal_extra').text('PAL ' + newPal);
  
  $('#goal_bmi').text(properRound(goalWeight / (height / 100) ** 2, 1));
  const goalBmr = 10 * goalWeight + BMR_CONSTANT;
  $('#goal_bmr').text(Math.round(goalBmr));
  $('#goal_daily_energy_extra').text(Math.round(goalBmr * newPal) + ' kcal/dia');

  $('#proteins_weight').text(Math.round(goalDailyEnergy * proteins / 4));
  $('#carbs_weight').text(Math.round(goalDailyEnergy * carbs / 4));
  $('#fats_weight').text(Math.round(goalDailyEnergy * fats / 9));

  $('#proteins_per_weight').text(properRound($('#proteins_weight').text() / weight, 2));
  $('#carbs_per_weight').text(properRound($('#carbs_weight').text() / weight, 2));
  $('#fats_per_weight').text(properRound($('#fats_weight').text() / weight, 2));

  // Update NIDDK calculator results
  function niddk() {
    $('#energy_to_goal, #energy_to_maintain').text('...');
    while (calc.contentDocument.readyState !== 'complete') {
      setTimeout(niddk, 500);
      return;
    }
    const data = {
      ...jsContext,
      gender: { m: 'Male', f: 'Female' }[gender],
      pal: parseFloat(pal),
      goalWeight: goalWeight,
      goalTime: goalTime * 30,
      palChange: palChange,
    };
    for (let key in data) {
      if (typeof data[key] === 'undefined' || (typeof data[key] === 'number' && Number.isNaN(data[key]))) {
        return;
      }
    }
    const calcBody = calc.contentDocument.body;
    const scope = calc.contentWindow.angular.element(calcBody).scope();
    const result = scope.getEnergy(data);
    $('#energy_to_goal').text(result.energyGoal);
    $('#energy_to_maintain').text(result.energyMaintain);
  }
  setTimeout(niddk);
}

function init() {
  // Hide efields controls
  $('.efield-controls').hide();

  // Set range input label values
  $('.efield input[type="range"]').each(function() {
    $(this).parent().siblings('.field-extra').text($(this).val());
  });

  // Set constant field values
  $('#pal_extra').text('PAL ' + pal);
  $('#bmi').text(properRound(weight / (height / 100) ** 2, 1));
  const bmr = 10 * weight + BMR_CONSTANT;
  $('#bmr').text(Math.round(bmr));
  $('#daily_energy').text(Math.round(bmr * pal));
  
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

  $('.efield input[type!="range"], .efield select').blur(function() {
    if (!event.relatedTarget || !event.relatedTarget.classList.contains('efield-save')) {
      cancel(this);
    }
  }).keydown(function(event) {
    if (event.key === 'Enter') save(this, $(this).val());
    else if (event.key === 'Escape') cancel(this);
  });

  $('.efield input[type="range"]').on('input', function() {
    $(this).parent().siblings('.field-extra').text($(this).val());
  });

  $('.efield input[type="range"]').change(render);

  // Range inputs interdependence
  const mns = MACRONUTRIENTS_ARR.map(mn => $(`#${mn}_efield input`));
  for (let i = 0; i < 3; i++) {
    mns[i].on('input', function() {
      const secondVal = Math.max(100 - $(this).val() - mns[i+2].val(), 0);
      mns[i+1].val(secondVal).parent().siblings('.field-extra').text(secondVal);
      if (secondVal === 0) {
        const thirdVal = 100 - $(this).val();
        mns[i+2].val(thirdVal).parent().siblings('.field-extra').text(thirdVal);
      }
    });
  }
}

init();
